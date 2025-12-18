// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::ops::Deref;

use swh_contents::blame::blame::{BlameError, Blamer};
use swh_contents::retriever::ContentRetriever;
use swh_graph::graph::{SwhGraphWithProperties, SwhLabeledForwardGraph};
use swh_graph::labels::Permission;
use swh_graph::swhid;
use swh_graph::{properties, NodeType, SWHID};

#[path = "./graphs.rs"]
mod graphs;
use graphs::*;

// utility function to display the result of a blame, for testing purposes
fn format_blame<
    G: SwhLabeledForwardGraph
        + SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>,
    CR: Deref<Target: ContentRetriever> + Clone,
>(
    blamer: &Blamer<G, CR>,
) -> String {
    let ranges = blamer.ranges();
    let lines = blamer
        .final_contents()
        .lines()
        .expect("Cannot display a blame on a binary file");
    let mut output = String::new();
    for (index, line) in lines.iter().enumerate() {
        let line_str = std::str::from_utf8(line).expect("Cannot decode line as UTF-8");
        let origin = ranges.get(index);
        if let Some((_, origin)) = origin {
            output += &format!(
                "{}{} {}",
                origin.rev,
                if origin.added_in_this_rev { " " } else { "…" },
                line_str
            );
        } else {
            output += &format!("   {}", line_str);
        }
    }
    output
}

#[tokio::test]
async fn test_blame_single_file_change() {
    let file1 = b"A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\nK\n";
    let file2 = b"A\nXXX\nB\nD\nE\nF\nG\nH\nI\nJ\nYYY\nK";

    let graph = get_linear_graph();
    let graph = &graph;
    let props = graph.properties();

    let mut blamer = Blamer::new(
        graph,
        get_content_retriever!(graph, [file1, file2]),
        2,
        vec![props.label_name_id("test.txt").unwrap()].into_boxed_slice(),
        None,
    )
    .await
    .expect("Couldn't create the blamer");

    let further_steps_required = blamer
        .step()
        .await
        .expect("Error in the first step of the blame algorithm");
    assert!(further_steps_required);

    // after one step of blaming, we know which ranges have been added by the commit
    // we inspected, but we are not sure if the remaining ones come from its parent commit
    // or further down the history.
    let expected = "\
1… A
2  XXX
1… B
1… D
1… E
1… F
1… G
1… H
1… I
1… J
2  YYY
2  K";
    assert_eq!(format_blame(&blamer), expected);

    blamer
        .compute_fully()
        .await
        .expect("Error while computing the rest of the blame");

    // Once the blame is computed fully, we have final provenance info for all lines
    let expected = "\
1  A
2  XXX
1  B
1  D
1  E
1  F
1  G
1  H
1  I
1  J
2  YYY
2  K";
    assert_eq!(format_blame(&blamer), expected);
}

#[tokio::test]
async fn test_blame_with_binary_ancestor() {
    let file1 = b"\xff";
    let file2 = b"A\nB\nC\n";

    let graph = get_linear_graph();
    let graph = &graph;
    let props = graph.properties();

    let mut blamer = Blamer::new(
        graph,
        get_content_retriever!(graph, [file1, file2]),
        2,
        vec![props.label_name_id("test.txt").unwrap()].into_boxed_slice(),
        None,
    )
    .await
    .expect("Couldn't create the blamer");

    let further_steps_required = blamer
        .step()
        .await
        .expect("Error in the first step of the blame algorithm");
    assert!(!further_steps_required);

    // If the previous version of the file happens to be binary, then
    // we consider that the first text version added all of its lines.
    let expected = "\
2  A
2  B
2  C
";
    assert_eq!(format_blame(&blamer), expected);
}

#[tokio::test]
async fn test_blame_with_merge() {
    let file1 = b"A\nB\nC\nD\nE\nF\nG\n";
    let file2 = b"a1\na2\nB\nC\nd\nE\nG\n";
    let file3 = b"A\nB\nC\ndd\nE\nF\nG\nH\n";
    let file4 = b"a1\na2\nB\nC\nresolved\nE\nG\nH\n";

    let graph = get_diamond_graph();
    let graph = &graph;
    let props = graph.properties();

    let mut blamer = Blamer::new(
        graph,
        get_content_retriever!(graph, [file1, file2, file3, file4]),
        4,
        vec![props.label_name_id("test.txt").unwrap()].into_boxed_slice(),
        None,
    )
    .await
    .expect("Couldn't create the blamer");

    let further_steps_required = blamer
        .step()
        .await
        .expect("Error while doing the first blaming step");
    assert!(further_steps_required);

    // Initially, we have only inspected the merge commit, so we only know the provenance
    // of any changes that are specific to the commit (such as a conflict resolution).
    let expected = "\
2… a1
2… a2
2… B
2… C
4  resolved
2… E
2… G
3… H
";
    assert_eq!(format_blame(&blamer), expected);

    blamer
        .compute_fully()
        .await
        .expect("Error while computing the blame result");

    let expected = "\
2  a1
2  a2
1  B
1  C
4  resolved
1  E
1  G
3  H
";
    assert_eq!(format_blame(&blamer), expected);
}

#[tokio::test]
/// Tests a merge where the file only exists in one of the parents
async fn test_blame_with_merge_new_file() {
    let file1 = b"A\nC";
    let file2 = b"A\nB\nC";

    let mut builder = get_4rev_graph();
    // rev3 is a merge of rev1 and rev2
    builder.arc(3, 1);
    builder.arc(3, 2);

    let cnt1 = builder
        .node_id(swhid!(swh:1:cnt:2100000000000000000000000000000000000000))
        .unwrap();
    let cnt2 = builder
        .node_id(swhid!(swh:1:cnt:2200000000000000000000000000000000000000))
        .unwrap();

    // rev1's tree is unchanged
    let _dir1 = builder
        .node_id(swhid!(swh:1:dir:0000000000000000000000000000000000000011))
        .unwrap();

    // rev2's tree has a new file
    let dir2 = builder
        .node_id(swhid!(swh:1:dir:0000000000000000000000000000000000000012))
        .unwrap();
    builder.dir_arc(dir2, cnt1, Permission::Content, b"test2.txt");

    // rev3's tree has a new version of that new file
    let dir3 = builder
        .node_id(swhid!(swh:1:dir:0000000000000000000000000000000000000013))
        .unwrap();
    builder.dir_arc(dir3, cnt2, Permission::Content, b"test2.txt");

    let graph = builder.done().unwrap();
    let graph = &graph;
    let props = graph.properties();

    let mut blamer = Blamer::new(
        graph,
        get_content_retriever!(graph, [file1, file2]),
        3,
        vec![props.label_name_id("test2.txt").unwrap()].into_boxed_slice(),
        None,
    )
    .await
    .expect("Couldn't create the blamer");

    let further_steps_required = blamer
        .step()
        .await
        .expect("Error while doing the first blaming step");
    assert!(further_steps_required);

    // Initially, we have only inspected the merge commit, so we only know the provenance
    // of any changes that are specific to the commit (such as a conflict resolution).
    let expected = "\
2… A
3  B
2… C";
    assert_eq!(format_blame(&blamer), expected);

    blamer
        .compute_fully()
        .await
        .expect("Error while computing the blame result");

    let expected = "\
2  A
3  B
2  C";
    assert_eq!(format_blame(&blamer), expected);
}

#[tokio::test]
async fn test_blame_stops_once_the_range_is_covered() {
    let file1 = b"A\nB\nC\nD\nE\nF\nG\n";
    let file2 = b"a\nB\nC\nD\nE\nF\nG\n";
    let file3 = b"a\nB\nC\nD\nE\nG\n";
    let file4 = b"a\nB\nC\nx\ny\nz\nD\nE\nG\n";

    let graph = get_linear_graph();
    let graph = &graph;
    let props = graph.properties();

    let mut blamer = Blamer::new(
        graph,
        get_content_retriever!(graph, [file1, file2, file3, file4]),
        4,
        vec![props.label_name_id("test.txt").unwrap()].into_boxed_slice(),
        Some(3..5),
    )
    .await
    .expect("Couldn't create the blamer");

    let further_steps_required = blamer
        .step()
        .await
        .expect("Error while doing the first blaming step");

    assert!(!further_steps_required);

    // provenance info is only provided for the lines where it was requested
    let expected = "   \
   a
   B
   C
4  x
4  y
   z
   D
   E
   G
";
    assert_eq!(format_blame(&blamer), expected);
}

#[tokio::test]
async fn test_blame_non_existent_file() {
    let file1 = b"A\n";

    let (rev1, _, graph) = get_file_creation_graph();
    let graph = &graph;
    let props = graph.properties();

    let blamer = Blamer::new(
        graph,
        get_content_retriever!(graph, [file1]),
        rev1,
        vec![props.label_name_id("test.txt").unwrap()].into_boxed_slice(),
        None,
    )
    .await;
    assert!(
        matches!(blamer, Err(BlameError::FileNotFound { .. })),
        "Blaming a non-existent file should return an error"
    );
}

#[tokio::test]
async fn test_blame_binary_file() {
    let file1 = b"\xff";

    let (_, rev2, graph) = get_file_creation_graph();
    let graph = &graph;
    let props = graph.properties();

    let blamer = Blamer::new(
        graph,
        get_content_retriever!(graph, [file1]),
        rev2,
        vec![props.label_name_id("test.txt").unwrap()].into_boxed_slice(),
        None,
    )
    .await;
    assert!(
        matches!(blamer, Err(BlameError::BinaryContent { .. })),
        "Blaming a non-existent file should return an error"
    );
}
