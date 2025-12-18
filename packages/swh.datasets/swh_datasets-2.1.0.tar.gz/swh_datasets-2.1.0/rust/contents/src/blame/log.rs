// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::collections::HashSet;

use anyhow::{anyhow, Context, Result};
use swh_graph::graph::{NodeId, SwhGraphWithProperties, SwhLabeledForwardGraph};
use swh_graph::labels::LabelNameId;
use swh_graph::{properties, NodeType};
use swh_graph_stdlib::{find_root_dir, fs_resolve_path_by_id};

/// Find the oldest ancestors of a revision where the contents at the provided path
/// remain equal to the contents in the given revision.
///
/// The ancestors returned are only the "direct" ones, meaning that the path
/// between them and the supplied revision contains only other revisions which
/// didn't change the contents at the path.
/// There may be more than one such ancestor when merge commits are present.
/// The iterator will contain just the supplied revision if all its ancestors have
/// different contents at this path.
pub fn earliest_revisions_with_same_content<G, P>(
    graph: G,
    revision: NodeId,
    path: P,
) -> Result<impl Iterator<Item = RevWithParentContents>>
where
    G: SwhLabeledForwardGraph + SwhGraphWithProperties<Maps: properties::Maps>,
    P: Into<Box<[LabelNameId]>>,
{
    let path = path.into();
    let root_dir = find_root_dir(&graph, revision)
        .with_context(|| {
            format!(
                "Could not get root directory of revision {}",
                graph.properties().swhid(revision)
            )
        })?
        .ok_or_else(|| {
            anyhow!(
                "No root directory for revision {}",
                graph.properties().swhid(revision)
            )
        })?;
    let content_id = fs_resolve_path_by_id(&graph, root_dir, &path)
        .with_context(|| {
            format!(
                "Could not get content at supplied path in revision {}",
                graph.properties().swhid(revision)
            )
        })?
        .ok_or_else(|| {
            anyhow!(
                "No content at the supplied path in revision {}",
                graph.properties().swhid(revision)
            )
        })?;
    Ok(AncestorIterator {
        graph,
        revisions_to_explore: vec![revision],
        path,
        content_id,
        visited_revisions: HashSet::new(),
    })
}

/// A revision and a content id for the target file in that revision,
/// if it is present.
#[derive(Debug, Clone, Eq, PartialEq)]
pub struct RevContent {
    pub rev: NodeId,
    pub content: Option<NodeId>,
}

/// A revision with its list of parents and the version of the file that they have
#[derive(Debug, Clone, Eq, PartialEq)]
pub struct RevWithParentContents {
    pub rev: NodeId,
    pub parents: Vec<RevContent>,
}

/// The iterator underpinning [`earliest_revisions_with_same_content`]
struct AncestorIterator<G: SwhLabeledForwardGraph + SwhGraphWithProperties<Maps: properties::Maps>>
{
    graph: G,
    /// the path whose log should be extracted
    path: Box<[LabelNameId]>,
    /// the content expected at the path provided
    content_id: NodeId,
    /// a stack of revisions which have the same content as the starting revision,
    /// and whose descendants we should continue exploring
    revisions_to_explore: Vec<NodeId>,
    /// already visited revisions, which shouldn't be added to the stack again
    visited_revisions: HashSet<NodeId>,
}

impl<G> Iterator for AncestorIterator<G>
where
    G: SwhLabeledForwardGraph + SwhGraphWithProperties<Maps: properties::Maps>,
{
    type Item = RevWithParentContents;

    fn next(&mut self) -> Option<Self::Item> {
        let properties = self.graph.properties();

        while let Some(revision) = self.revisions_to_explore.pop() {
            if !self.visited_revisions.insert(revision) {
                continue;
            }
            let get_content_at_rev = |rev: NodeId| {
                let root_dir = find_root_dir(&self.graph, rev).ok()??;
                fs_resolve_path_by_id(&self.graph, root_dir, &self.path).ok()?
            };
            let mut found_next_revision_to_explore = false;
            let mut parents_with_different_contents = Vec::new();
            // Iterate over the parent revisions and check which ones have the target content
            for (parent_rev, parent_content) in self
                .graph
                .successors(revision)
                .into_iter()
                .filter(|successor| properties.node_type(*successor) == NodeType::Revision)
                .map(|parent| (parent, get_content_at_rev(parent)))
            {
                if parent_content.is_some_and(|content| content == self.content_id) {
                    found_next_revision_to_explore = true;
                    // queue the revision to visit it later, because we already have another
                    // revision to visit
                    self.revisions_to_explore.push(parent_rev)
                } else {
                    parents_with_different_contents.push(RevContent {
                        rev: parent_rev,
                        content: parent_content,
                    })
                }
            }
            if !found_next_revision_to_explore {
                // all the parents of the current revision have a different content,
                return Some(RevWithParentContents {
                    rev: revision,
                    parents: parents_with_different_contents,
                });
            }
        }
        None
    }
}
