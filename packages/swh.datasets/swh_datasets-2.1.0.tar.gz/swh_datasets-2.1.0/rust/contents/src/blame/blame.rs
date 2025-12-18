// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::ops::{Deref, Range};

use anyhow::anyhow;
use anyhow::{Context, Result};
use swh_graph::graph::{NodeId, SwhGraphWithProperties, SwhLabeledForwardGraph};
use swh_graph::labels::LabelNameId;
use swh_graph::{properties, SWHID};
use swh_graph_stdlib::{find_root_dir, fs_resolve_path_by_id};

use crate::blame::log::{earliest_revisions_with_same_content, RevContent};
use crate::blame::rangemap::{zip_range_iterators, RangeMap};
use crate::diff::contents::{FileAtRev, FileContents};
use crate::diff::diff::FileDiff;
use crate::diff::differ::RevDiffer;
use crate::retriever::ContentRetriever;

/// Annotations for ranges of lines in a blame result
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct LineProvenance {
    /// The revision this line interval is coming from
    pub rev: NodeId,
    /// The offset from the final revision (start of the blame algorithm) to this revision.
    /// This means that in this range, the line numbers in this revision are obtained by adding
    /// this offset to the line numbers in the final revision.
    pub offset: i32,
    /// Whether this line interval was added in this rev, or if it might come from an ancestor of it.
    /// If the blame has been fully computed, this field is always set to true, otherwise it is an
    /// indicator that the blame hasn't been fully computed in this area.
    pub added_in_this_rev: bool,
}

#[derive(Debug, thiserror::Error)]
pub enum BlameError {
    #[error("{cnt_swhid} is a binary file, which cannot be blamed")]
    BinaryContent { cnt_id: NodeId, cnt_swhid: SWHID },
    #[error("File not found in revision {rev_swhid}")]
    FileNotFound { rev_id: NodeId, rev_swhid: SWHID },
    #[error("Cannot fetch content of {cnt_swhid}")]
    CannotFetchContent {
        cnt_id: NodeId,
        cnt_swhid: SWHID,
        #[source]
        source: anyhow::Error,
    },
    #[error("Error while blaming")]
    Other(#[from] anyhow::Error),
}

/// The state of a blame algorithm on a single file
#[derive(Debug)]
pub struct Blamer<
    G: SwhLabeledForwardGraph
        + SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>,
    CR: Deref<Target: ContentRetriever> + Clone,
> {
    // Immutable context of the algorithm
    graph: G,
    retriever: CR,
    path: Box<[LabelNameId]>,
    /// Revision we are blaming from
    final_revision: NodeId,
    final_contents: FileContents,

    /// Provenance information being computed, mapping lines of the final revision to their provenance
    provenance: RangeMap<LineProvenance>,
    /// Stack of revisions to inspect to refine the provenance info
    revisions_to_explore: Vec<BlameTask>,
}

impl<
        G: SwhLabeledForwardGraph
            + SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>,
        CR: Deref<Target: ContentRetriever> + Clone,
    > Blamer<G, CR>
{
    /// Start blaming a file in a revision, potentially restricting the blame to a specific range of lines.
    /// This will fetch the contents of the file in the final revision.
    /// The [`ContentRetriever`] supplied should have a built-in caching functionality, as the same file
    /// will generally be requested multiple times over the course of the blaming algorithm.
    pub async fn new(
        graph: G,
        retriever: CR,
        rev: NodeId,
        path: impl Into<Box<[LabelNameId]>>,
        line_range: Option<Range<usize>>,
    ) -> Result<Self, BlameError> {
        let path = path.into();
        let root_dir = find_root_dir(&graph, rev)
            .with_context(|| {
                format!(
                    "Could not get root directory of revision {}",
                    graph.properties().swhid(rev)
                )
            })?
            .ok_or_else(|| {
                anyhow!(
                    "No root dir found in revision {}",
                    graph.properties().swhid(rev)
                )
            })?;
        let cnt = fs_resolve_path_by_id(&graph, root_dir, path.as_ref())
            .with_context(|| {
                format!(
                    "Could not get content at supplied path in revision {}",
                    graph.properties().swhid(rev)
                )
            })?
            .ok_or_else(|| BlameError::FileNotFound {
                rev_id: rev,
                rev_swhid: graph.properties().swhid(rev),
            })?;
        let final_contents = FileContents::fetch(
            &graph,
            &retriever,
            &FileAtRev {
                rev,
                content: cnt,
                path: &path,
                perm: None,
            },
        )
        .await
        .map_err(|err| BlameError::CannotFetchContent {
            cnt_id: cnt,
            cnt_swhid: graph.properties().swhid(cnt),
            source: err.into(),
        })?;
        let line_count = final_contents
            .lines()
            .ok_or(BlameError::BinaryContent {
                cnt_id: cnt,
                cnt_swhid: graph.properties().swhid(cnt),
            })?
            .len();
        let target_range = line_range.unwrap_or_else(|| 0..line_count);
        Ok(Blamer {
            graph,
            retriever,
            path,
            provenance: RangeMap::new(
                [(
                    target_range.clone(),
                    LineProvenance {
                        rev,
                        offset: 0,
                        added_in_this_rev: false,
                    },
                )]
                .into_iter(),
            ),
            revisions_to_explore: vec![BlameTask { rev, cnt }],
            final_revision: rev,
            final_contents,
        })
    }

    /// Get the contents of the file in the final revision
    pub fn final_contents(&self) -> &FileContents {
        &self.final_contents
    }

    /// Compute the blame of the target region entirely
    pub async fn compute_fully(&mut self) -> Result<()> {
        while self.step().await? {}
        Ok(())
    }

    // Transform the current blame result to index it by ranges of a specific revision
    // instead of the final one, retaining the offset to the final revision as a separate component
    fn ranges_to_annotate_from(&self, rev: NodeId) -> RangeMap<(LineProvenance, i32)> {
        self.provenance
            .iter()
            .filter_map(|(range, prov)| {
                if !prov.added_in_this_rev && prov.rev == rev {
                    return Some((
                        ((range.start as i32 + prov.offset) as usize)
                            ..((range.end as i32 + prov.offset) as usize),
                        (prov.clone(), prov.offset),
                    ));
                }
                None
            })
            .collect()
    }

    /// Inspect one more ancestor revisions, returning whether there are further revisions
    /// to explore before reaching a complete coverage of the blame result.
    pub async fn step(&mut self) -> Result<bool, BlameError> {
        let Some(BlameTask {
            rev: current_rev,
            cnt: current_content,
        }) = self.revisions_to_explore.pop()
        else {
            return Ok(false);
        };
        // Find the earliest revision which had the same content as in the revision to annotate, with its parents
        let earliest_revs =
            earliest_revisions_with_same_content(&self.graph, current_rev, self.path.as_ref())?;

        for earliest_rev in earliest_revs {
            // Select the ranges that we need to annotate further from this revision
            let mut ranges_to_annotate: RangeMap<(LineProvenance, i32)> =
                self.ranges_to_annotate_from(current_rev);

            // For each parent revision of the revision to annotate
            for parent_rev in &earliest_rev.parents {
                // Compute ranges in the current revision,
                // either coming from the current diff or to be annotated from a parent commit
                let diff = self
                    .match_common_lines(
                        &RevContent {
                            rev: current_rev,
                            content: Some(current_content),
                        },
                        parent_rev,
                    )
                    .await?;

                let Some(new_to_old_rangemap) = diff else {
                    continue; // one of the files is binary
                };

                // Update the ranges to annotate by removing all the ranges which come from the current diff
                let found_range_to_annotate_further = Self::update_ranges_to_annotate(
                    &mut ranges_to_annotate,
                    new_to_old_rangemap,
                    current_rev,
                    parent_rev.rev,
                );

                // Add the parent revision to the queue if we found any section of the file to be annotated from it
                if found_range_to_annotate_further {
                    let Some(cnt) = parent_rev.content else {
                        panic!(
                            "Could not annotate {:?} from {}: there are more ranges to annotate, but the file does not exist in the ancestor {}",
                            self.path,
                            self.graph.properties().swhid(self.final_revision),
                            self.graph.properties().swhid(parent_rev.rev),
                        );
                    };
                    self.revisions_to_explore.push(BlameTask {
                        rev: parent_rev.rev,
                        cnt,
                    });
                }
            }

            let unannotated_lines_remaining = Self::integrate_annotated_ranges(
                &mut self.provenance,
                ranges_to_annotate,
                current_rev,
            );

            // if all the lines have been annotated, stop the blame here
            if !unannotated_lines_remaining {
                self.revisions_to_explore.clear();
                return Ok(false);
            }
        }
        Ok(!self.revisions_to_explore.is_empty())
    }

    /// Obtain the line ranges and their provenance
    pub fn ranges(&self) -> &RangeMap<LineProvenance> {
        &self.provenance
    }

    /// Compute the diff between the file and transform it to a [`RangeMap`] mapping
    /// lines of the newer revision to their offset in the older revision
    /// (for lines that are preserved by the diff).
    /// The file needs to be present in the current revision.
    /// If any of the files is binary, None is returned.
    async fn match_common_lines(
        &self,
        current_rev: &RevContent,
        parent_rev: &RevContent,
    ) -> Result<Option<RangeMap<i32>>> {
        let differ = RevDiffer {
            graph: &self.graph,
            content_retriever: self.retriever.clone(),
            concurrent_downloads: 2,
        };
        let diff = differ
            .diff_file(
                parent_rev
                    .content
                    .map(|parent_content| FileAtRev {
                        rev: parent_rev.rev,
                        path: self.path.as_ref(),
                        content: parent_content,
                        perm: None,
                    })
                    .as_ref(),
                &FileAtRev {
                    rev: current_rev.rev,
                    path: self.path.as_ref(),
                    content: current_rev.content.expect(
                        "Cannot match common lines if the file isn't present in the current rev",
                    ),
                    perm: None,
                },
            )
            .await?;
        Ok(Self::diff_to_rangemap(&diff))
    }

    /// Convert a diff to the range map, for [`Self::match_common_lines`]
    fn diff_to_rangemap(file_diff: &FileDiff) -> Option<RangeMap<i32>> {
        match file_diff {
            FileDiff::Added { .. } | FileDiff::Removed { .. } => Some(RangeMap::new([])),
            FileDiff::Modified {
                new_file, hunks, ..
            } => {
                let mut start_new: usize = 0;
                let mut start_old: usize = 0;
                let line_count_new = new_file.lines()?.len();
                let mut ranges = Vec::new();
                let hunks = hunks.as_ref()?;
                for hunk in hunks {
                    ranges.push((
                        start_new..(hunk.new_range.start as usize),
                        start_old as i32 - start_new as i32,
                    ));
                    start_new = hunk.new_range.end as usize;
                    start_old = hunk.old_range.end as usize;
                }
                if start_new < line_count_new {
                    ranges.push((
                        start_new..line_count_new,
                        start_old as i32 - start_new as i32,
                    ));
                }
                Some(RangeMap::new(ranges))
            }
        }
    }

    /// Given ranges from the current revisions, refine their
    /// provenance annotations by integrating the common lines between
    /// the current and parent revision provided.
    /// Returns true if any range needs further annotating from the parent
    /// revision.
    fn update_ranges_to_annotate(
        ranges_to_annotate: &mut RangeMap<(LineProvenance, i32)>,
        new_to_old_rangemap: RangeMap<i32>,
        current_rev: NodeId,
        parent_rev: NodeId,
    ) -> bool {
        let mut found_range_to_annotate_further = false;
        *ranges_to_annotate = ranges_to_annotate
            .zip(&new_to_old_rangemap)
            .filter_map(|(range_current, state, parent_offset)| {
                let (prov, orig_offset) = state?;
                let mut new_prov = prov.clone();
                // TODO change the `is_some()` / `unwrap()` to an if let chain once we use Rust 2024
                #[allow(clippy::unnecessary_unwrap)]
                if !prov.added_in_this_rev && prov.rev == current_rev && parent_offset.is_some() {
                    found_range_to_annotate_further = true;
                    new_prov = LineProvenance {
                        rev: parent_rev,
                        offset: parent_offset.unwrap() + prov.offset,
                        added_in_this_rev: false,
                    }
                }
                Some((range_current.clone(), (new_prov, *orig_offset)))
            })
            .collect();
        found_range_to_annotate_further
    }

    /// Integrate annotations on the current revision back to the global state of the blame algorithm,
    /// as annotations on the final revision (the one the blame is run on).
    /// Returns whether any unannotated lines remain after this integration.
    fn integrate_annotated_ranges(
        provenance: &mut RangeMap<LineProvenance>,
        ranges_to_annotate: RangeMap<(LineProvenance, i32)>,
        current_rev: NodeId,
    ) -> bool {
        // Translate the current annotations back to a range map referring to the final line numbers
        let annotations_on_final_rev =
            ranges_to_annotate
                .iter()
                .map(|(current_range, (state, final_offset))| {
                    (
                        (current_range.start as i32 - final_offset) as usize
                            ..(current_range.end as i32 - final_offset) as usize,
                        state,
                    )
                });

        // Update the global blame state with the new annotations gathered from this revision
        let mut unannotated_lines_remaining = false;
        *provenance = zip_range_iterators(provenance.iter(), annotations_on_final_rev)
            .filter_map(|(orig_range, current_blame_state, new_blame_state)| {
                let mut final_state = new_blame_state.or(current_blame_state)?.clone();
                if !final_state.added_in_this_rev && final_state.rev == current_rev {
                    // if the range remains to be blamed from this revision, then that range was added in this revision,
                    // since we have explored all of its parents.s
                    final_state.added_in_this_rev = true;
                }
                if !final_state.added_in_this_rev {
                    unannotated_lines_remaining = true;
                }
                Some((orig_range, final_state))
            })
            .collect();
        unannotated_lines_remaining
    }
}

/// Internal state keeping track of a revision to explore and the version of the file at that revision
#[derive(Debug)]
struct BlameTask {
    /// The revision to explore
    rev: NodeId,
    /// The version of the target file at that revision
    cnt: NodeId,
}
