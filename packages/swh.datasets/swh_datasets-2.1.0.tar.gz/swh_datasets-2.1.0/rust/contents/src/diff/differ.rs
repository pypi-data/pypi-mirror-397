// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::ops::Deref;

use anyhow::{anyhow, Context, Result};
use futures::{StreamExt, TryStreamExt};
use imara_diff::{Algorithm, Diff, InternedInput};
use swh_graph::graph::{SwhGraphWithProperties, SwhLabeledForwardGraph};
use swh_graph::properties;
use swh_graph::SWHID;
use swh_graph_stdlib::collections::NodeId;
use swh_graph_stdlib::diff::TreeDiff;

use crate::diff::contents::{FileAtRev, FileContents};
use crate::diff::diff::{DiffHunk, FileDiff, RevisionDiff};
use crate::retriever::ContentRetriever;

#[derive(thiserror::Error, Debug)]
pub enum DiffError {
    #[error("Could not resolve {path} from {rev}: {source}")]
    ResolvePath {
        root_dir: SWHID,
        rev: SWHID,
        path: String,
        #[source]
        source: anyhow::Error,
    },
    #[error("Could not download {cnt}, found from {rev}: {source}")]
    Download {
        cnt: SWHID,
        rev: SWHID,
        #[source]
        source: anyhow::Error,
    },
    #[error("Content {cnt} not found, found from {rev}")]
    NotFound { cnt: SWHID, rev: SWHID },
    #[error("{0}")]
    Other(#[from] anyhow::Error),
}

pub struct RevDiffer<
    G: SwhLabeledForwardGraph
        + SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>,
    CR: Deref<Target: ContentRetriever>,
> {
    pub graph: G,
    pub content_retriever: CR,
    pub concurrent_downloads: usize,
}

impl<
        G: SwhLabeledForwardGraph
            + SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>,
        CR: Deref<Target: ContentRetriever>,
    > RevDiffer<G, CR>
{
    /// Computes a diff between two revisions
    pub async fn diff_revisions(
        &self,
        old_rev: Option<NodeId>,
        new_rev: NodeId,
        limit: Option<usize>,
    ) -> Result<RevisionDiff> {
        let old_root_dir = if let Some(old_rev) = old_rev {
            Some(
                swh_graph_stdlib::find_root_dir(&self.graph, old_rev)
                    .with_context(|| {
                        format!(
                            "Could not get root directory of old revision {}",
                            self.graph.properties().swhid(old_rev)
                        )
                    })?
                    .ok_or_else(|| {
                        anyhow!(
                            "No root directory for revision {}",
                            self.graph.properties().swhid(old_rev)
                        )
                    })?,
            )
        } else {
            None
        };
        let new_root_dir = swh_graph_stdlib::find_root_dir(&self.graph, new_rev)
            .with_context(|| {
                format!(
                    "Could not get root directory of new revision {}",
                    self.graph.properties().swhid(new_rev)
                )
            })?
            .ok_or_else(|| {
                anyhow!(
                    "No root directory for revision {}",
                    self.graph.properties().swhid(new_rev)
                )
            })?;
        let tree_diff =
            swh_graph_stdlib::diff::tree_diff_dirs(&self.graph, old_root_dir, new_root_dir, limit)
                .with_context(|| {
                    if let Some(old_rev) = old_rev {
                        format!(
                            "Could not compute the tree-level diff between {} and {}",
                            self.graph.properties().swhid(old_rev),
                            self.graph.properties().swhid(new_rev)
                        )
                    } else {
                        format!(
                            "Could not compute the tree-level diff for {} as a root revision",
                            self.graph.properties().swhid(new_rev)
                        )
                    }
                })?;
        self.diff_contents(old_rev, new_rev, &tree_diff).await
    }

    async fn diff_contents(
        &self,
        old_rev: Option<NodeId>,
        new_rev: NodeId,
        tree_diff: &TreeDiff,
    ) -> Result<RevisionDiff> {
        let diffs = futures::stream::iter(tree_diff.operations())
            .map(|op| async move {
                match op {
                    swh_graph_stdlib::diff::TreeDiffOperation::Added {
                        path,
                        new_file,
                        new_perm,
                    } => {
                        let contents = FileContents::fetch(
                            &self.graph,
                            &self.content_retriever,
                            &FileAtRev {
                                rev: new_rev,
                                path,
                                content: new_file,
                                perm: new_perm,
                            },
                        )
                        .await?;
                        Ok::<FileDiff, DiffError>(FileDiff::Added { new_file: contents })
                    }
                    swh_graph_stdlib::diff::TreeDiffOperation::Deleted {
                        path,
                        old_file,
                        old_perm,
                    } => {
                        let contents = FileContents::fetch(
                            &self.graph,
                            &self.content_retriever,
                            &FileAtRev {
                                rev: old_rev.expect(
                                    "if a file was deleted, then an old_rev should be present",
                                ),
                                path,
                                content: old_file,
                                perm: old_perm,
                            },
                        )
                        .await?;
                        Ok(FileDiff::Removed { old_file: contents })
                    }
                    swh_graph_stdlib::diff::TreeDiffOperation::Modified {
                        path,
                        new_file,
                        old_file,
                        new_perm,
                        old_perm,
                    } => {
                        self.diff_file(
                            Some(&FileAtRev {
                                rev: old_rev.expect(
                                    "if a file was modified, then an old_rev should be present",
                                ),
                                path,
                                content: old_file,
                                perm: old_perm,
                            }),
                            &FileAtRev {
                                rev: new_rev,
                                path,
                                content: new_file,
                                perm: new_perm,
                            },
                        )
                        .await
                    }
                    swh_graph_stdlib::diff::TreeDiffOperation::Moved {
                        old_path,
                        new_path,
                        old_file,
                        new_file,
                        old_perm,
                        new_perm,
                    } => {
                        self.diff_file(
                            Some(&FileAtRev {
                                rev: old_rev.expect(
                                    "if a file was moved, then an old_rev should be present",
                                ),
                                path: old_path,
                                content: old_file,
                                perm: old_perm,
                            }),
                            &FileAtRev {
                                rev: new_rev,
                                path: new_path,
                                content: new_file,
                                perm: new_perm,
                            },
                        )
                        .await
                    }
                }
            })
            .buffer_unordered(self.concurrent_downloads)
            .try_collect()
            .await
            .context("Could not retrieve all contents")?;
        Ok(RevisionDiff::new(diffs))
    }

    /// Compute the diff between two versions of the same file.
    /// If no old file is provided, then a diff corresponding to a file creation is returned.
    pub async fn diff_file(
        &self,
        old_file: Option<&FileAtRev<'_>>,
        new_file: &FileAtRev<'_>,
    ) -> Result<FileDiff, DiffError> {
        let new_file = FileContents::fetch(&self.graph, &self.content_retriever, new_file).await?;
        let Some(old_file) = old_file else {
            return Ok(FileDiff::Added { new_file });
        };
        let old_file = FileContents::fetch(&self.graph, &self.content_retriever, old_file).await?;
        let (Some(old_lines), Some(new_lines)) = (old_file.lines(), new_file.lines()) else {
            // diff between binary files
            return Ok(FileDiff::Modified {
                old_file,
                new_file,
                hunks: None,
            });
        };
        let interned: InternedInput<&[u8]> = InternedInput::new(old_lines, new_lines);
        let diff = Diff::compute(Algorithm::Histogram, &interned);
        let hunks = diff
            .hunks()
            .map(|hunk| DiffHunk {
                old_range: hunk.before.clone(),
                new_range: hunk.after.clone(),
            })
            .collect();
        Ok(FileDiff::Modified {
            old_file,
            new_file,
            hunks: Some(hunks),
        })
    }
}
