// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::ops::Deref;

use bytes::Bytes;
use imara_diff::TokenSource;
use itertools::Itertools;
use swh_graph::graph::{NodeId, SwhGraphWithProperties};
use swh_graph::labels::{LabelNameId, Permission};
use swh_graph::{properties, SWHID};

use crate::diff::differ::DiffError;
use crate::retriever::ContentRetriever;

/// A file accessible from a revision at a given path
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub struct FileAtRev<'a> {
    pub rev: NodeId,
    pub path: &'a [LabelNameId],
    pub content: NodeId,
    pub perm: Option<Permission>,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
/// The contents of a file in a given revision, with associated metadata.
pub struct FileContents {
    pub swhid: SWHID,
    pub contents: Bytes,
    /// The positions of all newline characters (`\n`) in the file.
    pub line_indices: Option<Box<[usize]>>,
    pub perm: Option<Permission>,
    pub path: Box<[LabelNameId]>,
    pub path_str_lossy: String,
}

impl FileContents {
    /// Fetches the contents of a file mentioned by a diff.
    pub async fn fetch(
        graph: &impl SwhGraphWithProperties<Maps: properties::Maps, LabelNames: properties::LabelNames>,
        content_retriever: &impl Deref<Target: ContentRetriever>,
        file_at_rev: &FileAtRev<'_>,
    ) -> Result<FileContents, DiffError> {
        let FileAtRev {
            rev: revision,
            content: cnt_id,
            path,
            perm,
        } = *file_at_rev;
        let resp: Option<Bytes> =
            content_retriever
                .get(cnt_id)
                .await
                .map_err(|source| DiffError::Download {
                    cnt: graph.properties().swhid(cnt_id),
                    rev: graph.properties().swhid(revision),
                    source: source.into(),
                })?;
        if let Some(contents) = resp {
            let line_indices = Self::compute_line_indices(&contents);
            let path_str_lossy = render_path(&graph, path);
            Ok(FileContents {
                swhid: graph.properties().swhid(cnt_id),
                contents,
                perm,
                line_indices,
                path: path.into(),
                path_str_lossy,
            })
        } else {
            Err(DiffError::NotFound {
                cnt: graph.properties().swhid(cnt_id),
                rev: graph.properties().swhid(revision),
            })
        }
    }

    /// Get the lines of this file if it can be decoded as text
    pub fn lines(&self) -> Option<FileLines<'_>> {
        let line_indices = self.line_indices.as_ref()?;
        let has_newline_at_end = self.contents.is_empty()
            || line_indices.is_empty()
            || line_indices[line_indices.len() - 1] == self.contents.len() - 1;
        Some(FileLines {
            contents: &self.contents,
            line_indices: if has_newline_at_end && !line_indices.is_empty() {
                &line_indices[0..(&line_indices.len() - 1)]
            } else {
                line_indices
            },
            has_newline_at_end,
        })
    }

    fn compute_line_indices(bytes: &[u8]) -> Option<Box<[usize]>> {
        // TODO: support more text encodings than UTF-8
        let decoded = std::str::from_utf8(bytes).ok()?;
        let indices: Vec<_> = decoded.match_indices('\n').map(|(i, _)| i).collect();
        Some(indices.into_boxed_slice())
    }
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct FileLines<'a> {
    contents: &'a Bytes,
    line_indices: &'a [usize],
    has_newline_at_end: bool,
}

impl<'a> FileLines<'a> {
    /// Get the number of lines in the file
    pub fn len(&self) -> usize {
        if self.contents.is_empty() {
            0
        } else {
            self.line_indices.len() + 1
        }
    }

    pub fn is_empty(&self) -> bool {
        self.contents.is_empty()
    }

    /// Get the nth line of the file
    pub fn get(&self, i: usize) -> Option<&'a [u8]> {
        if i > self.line_indices.len() {
            None
        } else {
            let start_index = if i == 0 {
                0
            } else {
                self.line_indices[i - 1] + 1
            };
            let end_index = if i == self.line_indices.len() {
                self.contents.len()
            } else {
                self.line_indices[i] + 1
            };
            Some(&self.contents[start_index..end_index])
        }
    }

    /// Iterate on the lines
    pub fn iter(&self) -> impl Iterator<Item = &'a [u8]> {
        self.tokenize()
    }

    /// Has this file got the conventional last newline at the end?
    /// If the file is empty, we consider it has it.
    pub fn has_newline_at_end(&self) -> bool {
        self.has_newline_at_end
    }
}

// to enable diffing with imara_diff
impl<'a> TokenSource for FileLines<'a> {
    type Token = &'a [u8];

    type Tokenizer = LineIterator<'a>;

    fn tokenize(&self) -> Self::Tokenizer {
        LineIterator {
            index: 0,
            file_lines: self.clone(),
        }
    }

    fn estimate_tokens(&self) -> u32 {
        self.len() as u32
    }
}

pub struct LineIterator<'a> {
    index: usize,
    file_lines: FileLines<'a>,
}

impl<'a> Iterator for LineIterator<'a> {
    type Item = &'a [u8];

    fn next(&mut self) -> Option<Self::Item> {
        let line = self.file_lines.get(self.index)?;
        self.index += 1;
        Some(line)
    }
}

fn render_path(
    graph: &impl SwhGraphWithProperties<LabelNames: properties::LabelNames>,
    path: &[LabelNameId],
) -> String {
    path.iter()
        .map(|&label_name| {
            String::from_utf8_lossy(&graph.properties().label_name(label_name)).into_owned()
        })
        .join("/")
}
