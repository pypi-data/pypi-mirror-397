// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use swh_graph::graph::SwhGraphWithProperties;
use swh_graph::{NodeType, SWHID};

use swh_contents::diff::diff::*;
use swh_contents::diff::differ::*;

#[path = "./graphs.rs"]
mod graphs;
use graphs::*;

#[tokio::test]
async fn test_diff_single_file_change() {
    let file1 = b"A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\nK\n";
    let file2 = b"A\nXXX\nB\nD\nE\nF\nG\nH\nI\nJ\nYYY\nK";

    let graph = get_linear_graph();
    let graph = &graph;

    let differ = RevDiffer {
        graph,
        content_retriever: get_content_retriever!(graph, [file1, file2]),
        concurrent_downloads: 4,
    };
    let differ = &differ;

    let result = differ
        .diff_revisions(Some(1), 2, None)
        .await
        .expect("Error while computing the diff");

    let changes: Vec<_> = result.changes().collect();
    assert_eq!(changes.len(), 1);
    let FileDiff::Modified {
        old_file,
        new_file,
        hunks,
    } = changes[0]
    else {
        panic!("expected a FileDiff::Modified entry");
    };
    assert_eq!(*old_file.contents, *file1);
    assert_eq!(*new_file.contents, *file2);
    let hunks = hunks
        .as_ref()
        .expect("No diff hunks returned between two text files");
    let hunks: Vec<_> = hunks.into_iter().collect();
    assert_eq!(hunks.len(), 3);
    let rendered = format!("{}", result);

    let expected = "\
diff --git a/test.txt b/test.txt
index 21000000..22000000
--- a/test.txt
+++ b/test.txt
@@ -1,6 +1,6 @@
 A
+XXX
 B
-C
 D
 E
 F
@@ -8,4 +8,5 @@
 H
 I
 J
-K
+YYY
+K
\\ No newline at end of file
";
    assert_eq!(expected, rendered);
}

#[tokio::test]
async fn test_diff_single_file_creation() {
    let file1 = b"line1\nline2\n";

    let (rev1, rev2, graph) = get_file_creation_graph();
    let graph = &graph;

    let differ = RevDiffer {
        graph,
        content_retriever: get_content_retriever!(graph, [file1]),
        concurrent_downloads: 4,
    };
    let differ = &differ;

    let result = differ
        .diff_revisions(Some(rev1), rev2, None)
        .await
        .expect("Error while computing the diff");

    let changes: Vec<_> = result.changes().collect();
    assert_eq!(changes.len(), 1);
    let FileDiff::Added { new_file } = &changes[0] else {
        panic!("expected a FileDiff::Added entry");
    };
    assert_eq!(*new_file.contents, *b"line1\nline2\n");
    let rendered = format!("{}", result);

    let expected = "\
diff --git a/test.txt b/test.txt
new file mode 33188
index 00000000..21000000
--- /dev/null
+++ b/test.txt
@@ -0,0 +1,2 @@
+line1
+line2
";
    assert_eq!(expected, rendered);
}

#[tokio::test]
async fn test_diff_empty_file_creation() {
    let file1 = b"";

    let (rev1, rev2, graph) = get_file_creation_graph();
    let graph = &graph;

    let differ = RevDiffer {
        graph,
        content_retriever: get_content_retriever!(graph, [file1]),
        concurrent_downloads: 4,
    };
    let differ = &differ;

    let result = differ
        .diff_revisions(Some(rev1), rev2, None)
        .await
        .expect("Error while computing the diff");

    let changes: Vec<_> = result.changes().collect();
    assert_eq!(changes.len(), 1);
    let FileDiff::Added { new_file } = &changes[0] else {
        panic!("expected a FileDiff::Added entry");
    };
    assert_eq!(*new_file.contents, *b"");
    let rendered = format!("{}", result);

    let expected = "\
diff --git a/test.txt b/test.txt
new file mode 33188
index 00000000..21000000
";
    assert_eq!(expected, rendered);
}

#[tokio::test]
async fn test_diff_single_file_deletion() {
    let file1 = b"line1\nline2";

    let (rev1, rev2, graph) = get_file_creation_graph();
    let graph = &graph;

    let differ = RevDiffer {
        graph,
        content_retriever: get_content_retriever!(graph, [file1]),
        concurrent_downloads: 4,
    };
    let differ = &differ;

    let result = differ
        .diff_revisions(Some(rev2), rev1, None)
        .await
        .expect("Error while computing the diff");

    let changes: Vec<_> = result.changes().collect();
    assert_eq!(changes.len(), 1);
    let FileDiff::Removed { old_file } = &changes[0] else {
        panic!("expected a FileDiff::Added entry");
    };
    assert_eq!(*old_file.contents, *b"line1\nline2");
    let rendered = format!("{}", result);

    let expected = "\
diff --git a/test.txt b/test.txt
deleted file mode 33188
index 21000000..00000000
--- a/test.txt
+++ /dev/null
@@ -1,2 +0,0 @@
-line1
-line2
\\ No newline at end of file
";
    assert_eq!(expected, rendered);
}

#[tokio::test]
async fn test_binary_file_creation() {
    let file1 = b"\xff\xff";

    let (rev1, rev2, graph) = get_file_creation_graph();
    let graph = &graph;

    let differ = RevDiffer {
        graph,
        content_retriever: get_content_retriever!(graph, [file1]),
        concurrent_downloads: 4,
    };
    let differ = &differ;

    let result = differ
        .diff_revisions(Some(rev1), rev2, None)
        .await
        .expect("Error while computing the diff");

    let changes: Vec<_> = result.changes().collect();
    assert_eq!(changes.len(), 1);
    let FileDiff::Added { new_file } = &changes[0] else {
        panic!("expected a FileDiff::Added entry");
    };
    assert_eq!(*new_file.contents, *file1);
    let rendered = format!("{}", result);

    let expected = "\
diff --git a/test.txt b/test.txt
new file mode 33188
index 00000000..21000000
Binary files /dev/null and b/test.txt differ
";
    assert_eq!(expected, rendered);
}

#[tokio::test]
async fn test_binary_file_change() {
    let file1 = b"\xff";
    let file2 = b"\xff\xff";

    let graph = get_linear_graph();
    let graph = &graph;

    let differ = RevDiffer {
        graph,
        content_retriever: get_content_retriever!(graph, [file1, file2]),
        concurrent_downloads: 4,
    };
    let differ = &differ;

    let result = differ
        .diff_revisions(Some(1), 2, None)
        .await
        .expect("Error while computing the diff");

    let changes: Vec<_> = result.changes().collect();
    assert_eq!(changes.len(), 1);
    let FileDiff::Modified {
        old_file,
        new_file,
        hunks,
    } = changes[0]
    else {
        panic!("expected a FileDiff::Modified entry");
    };
    assert_eq!(*old_file.contents, *file1);
    assert_eq!(*new_file.contents, *file2);
    assert!(
        hunks.is_none(),
        "no hunks should be returned for binary files"
    );
    let rendered = format!("{}", result);

    let expected = "\
diff --git a/test.txt b/test.txt
index 21000000..22000000
Binary files a/test.txt and b/test.txt differ
";
    assert_eq!(expected, rendered);
}

#[tokio::test]
async fn test_diff_root_revision() {
    let file1 = b"A\nB\nC\nD\nE\nF\nG\nH\nI\nJ\nK\n";

    let graph = get_linear_graph();
    let graph = &graph;

    let differ = RevDiffer {
        graph,
        content_retriever: get_content_retriever!(graph, [file1]),
        concurrent_downloads: 4,
    };
    let differ = &differ;

    let result = differ
        .diff_revisions(None, 1, None)
        .await
        .expect("Error while computing the diff");

    let changes: Vec<_> = result.changes().collect();
    assert_eq!(changes.len(), 1);
    let FileDiff::Added { new_file } = changes[0] else {
        panic!("expected a FileDiff::Added entry");
    };
    assert_eq!(*new_file.contents, *file1);
    let rendered = format!("{}", result);

    let expected = "\
diff --git a/test.txt b/test.txt
new file mode 33188
index 00000000..21000000
--- /dev/null
+++ b/test.txt
@@ -0,0 +1,11 @@
+A
+B
+C
+D
+E
+F
+G
+H
+I
+J
+K
";
    assert_eq!(expected, rendered);
}
