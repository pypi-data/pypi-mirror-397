// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

use std::cmp::min;
use std::fmt::Display;
use std::ops::Range;

use anyhow::Result;
use swh_graph::labels::Permission;
use swh_graph::SWHID;

use crate::diff::contents::{FileContents, FileLines};

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
/// The diff between two revisions
pub struct RevisionDiff {
    changes: Vec<FileDiff>,
}

impl Display for RevisionDiff {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.display(&DisplaySettings::default(), f)
    }
}

impl RevisionDiff {
    pub fn new(changes: Vec<FileDiff>) -> Self {
        RevisionDiff { changes }
    }

    pub fn changes(&self) -> impl Iterator<Item = &FileDiff> + use<'_> {
        self.changes.iter()
    }

    fn display(
        &self,
        settings: &DisplaySettings,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        for change in &self.changes {
            change.display(settings, f)?;
        }
        Result::Ok(())
    }
}

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
/// Changes of a file between two revisions
pub enum FileDiff {
    /// The file is present in the new revision, not the old one
    Added { new_file: FileContents },
    /// The file is present in the old revision, not in the new one
    Removed { old_file: FileContents },
    /// The file is present in both revision (possibly at different paths).
    Modified {
        old_file: FileContents,
        new_file: FileContents,
        /// The differences between the contents, if both contents could be decoded as text.
        hunks: Option<Box<[DiffHunk]>>,
    },
}

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
/// A chunk in a diff of textual files
pub struct DiffHunk {
    /// The range of lines in the old revision (possibly empty)
    pub old_range: Range<u32>,
    /// The range of lines in the new revision (possibly empty)
    pub new_range: Range<u32>,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct DisplaySettings {
    /// Length of file hash sizes to show in diffs
    file_hash_length: usize,
    /// Number of context lines to show around changed lines
    context_lines: u32,
}

impl Default for DisplaySettings {
    fn default() -> Self {
        Self {
            file_hash_length: 8,
            context_lines: 3,
        }
    }
}

impl FileDiff {
    fn display(
        &self,
        settings: &DisplaySettings,
        f: &mut std::fmt::Formatter<'_>,
    ) -> std::fmt::Result {
        match self {
            FileDiff::Added { new_file } => {
                let path = &new_file.path_str_lossy;
                writeln!(f, "diff --git a/{path} b/{path}")?;
                writeln!(
                    f,
                    "new file mode {}",
                    new_file.perm.unwrap_or(Permission::Content).to_git()
                )?;
                writeln!(
                    f,
                    "index {}..{}",
                    CommitHash::new(None, settings.file_hash_length),
                    CommitHash::new(Some(new_file.swhid), settings.file_hash_length)
                )?;

                let new_path = format!("b/{path}");
                Self::display_file_creation_or_deletion(
                    f,
                    "/dev/null",
                    &new_path,
                    '+',
                    new_file.lines(),
                )
            }
            FileDiff::Removed { old_file } => {
                let path = &old_file.path_str_lossy;
                writeln!(f, "diff --git a/{path} b/{path}")?;
                writeln!(
                    f,
                    "deleted file mode {}",
                    old_file.perm.unwrap_or(Permission::Content).to_git()
                )?;
                writeln!(
                    f,
                    "index {}..{}",
                    CommitHash::new(Some(old_file.swhid), settings.file_hash_length),
                    CommitHash::new(None, settings.file_hash_length),
                )?;

                let old_path = format!("a/{path}");
                Self::display_file_creation_or_deletion(
                    f,
                    &old_path,
                    "/dev/null",
                    '-',
                    old_file.lines(),
                )
            }
            FileDiff::Modified {
                old_file,
                new_file,
                hunks,
            } => {
                let old_path = &old_file.path_str_lossy;
                let new_path = &new_file.path_str_lossy;
                writeln!(f, "diff --git a/{old_path} b/{new_path}")?;
                writeln!(
                    f,
                    "index {}..{}",
                    CommitHash::new(Some(old_file.swhid), settings.file_hash_length),
                    CommitHash::new(Some(new_file.swhid), settings.file_hash_length),
                )?;
                if let (Some(hunks), Some(old_lines), Some(new_lines)) =
                    (hunks, old_file.lines(), new_file.lines())
                {
                    writeln!(f, "--- a/{}", old_file.path_str_lossy)?;
                    writeln!(f, "+++ b/{}", new_file.path_str_lossy)?;
                    // group neighbouring hunks together
                    let grouped_hunks = GroupedHunkIterator {
                        hunks,
                        next_hunk: 0,
                        max_distance: (settings.context_lines * 2),
                    };
                    // print grouped hunks
                    for group in grouped_hunks {
                        let first_hunk = group.first().expect("Groups of DiffHunks are non-empty");
                        let last_hunk = group.last().expect("Groups of DiffHunks are non-empty");
                        let old_start = first_hunk
                            .old_range
                            .start
                            .saturating_sub(settings.context_lines);
                        let new_start = first_hunk
                            .new_range
                            .start
                            .saturating_sub(settings.context_lines);
                        let old_end = min(
                            old_lines.len() as u32,
                            last_hunk.old_range.end + settings.context_lines,
                        );
                        let new_end = min(
                            new_lines.len() as u32,
                            last_hunk.new_range.end + settings.context_lines,
                        );
                        let old_range = HunkRange(old_start..old_end);
                        let new_range = HunkRange(new_start..new_end);
                        writeln!(f, "@@ -{} +{} @@", old_range, new_range)?;
                        let mut context_start = old_start;
                        for hunk in group {
                            prepend_diff_sign_to_lines(
                                f,
                                ' ',
                                &old_lines,
                                (context_start as usize)..(hunk.old_range.start as usize),
                            )?;
                            prepend_diff_sign_to_lines(
                                f,
                                '-',
                                &old_lines,
                                (hunk.old_range.start as usize)..(hunk.old_range.end as usize),
                            )?;
                            prepend_diff_sign_to_lines(
                                f,
                                '+',
                                &new_lines,
                                (hunk.new_range.start as usize)..(hunk.new_range.end as usize),
                            )?;
                            context_start = hunk.old_range.end;
                        }
                        prepend_diff_sign_to_lines(
                            f,
                            ' ',
                            &old_lines,
                            (context_start as usize)..(old_end as usize),
                        )?;
                    }
                } else {
                    writeln!(f, "Binary files a/{old_path} and b/{new_path} differ")?;
                }
                Result::Ok(())
            }
        }
    }

    fn display_file_creation_or_deletion(
        f: &mut std::fmt::Formatter<'_>,
        old_path: &str,
        new_path: &str,
        line_prefix: char,
        lines: Option<FileLines<'_>>,
    ) -> std::fmt::Result {
        if let Some(lines) = lines {
            let range = HunkRange(0..(lines.len() as u32));
            if range.0.is_empty() {
                Result::Ok(())
            } else {
                writeln!(f, "--- {old_path}")?;
                writeln!(f, "+++ {new_path}")?;
                if line_prefix == '+' {
                    writeln!(f, "@@ -0,0 +{} @@", range)?;
                } else {
                    writeln!(f, "@@ -{} +0,0 @@", range)?;
                }
                prepend_diff_sign_to_lines(f, line_prefix, &lines, 0..(lines.len()))
            }
        } else {
            writeln!(f, "Binary files {old_path} and {new_path} differ")
        }
    }
}

fn prepend_diff_sign_to_lines(
    f: &mut std::fmt::Formatter<'_>,
    sign: char,
    lines: &FileLines<'_>,
    range: Range<usize>,
) -> std::fmt::Result {
    for i in range.into_iter() {
        let line = lines
            .get(i)
            .expect("Line range exceeds the lines in the file");
        let stripped = line.strip_suffix(b"\n").unwrap_or(line);
        let as_string = std::str::from_utf8(stripped).map_err(|_| std::fmt::Error {})?;
        writeln!(f, "{sign}{}", as_string)?;
        // If the last line is missing a newline character at the end, flag it
        if stripped.len() == line.len() && i == lines.len() - 1 {
            writeln!(f, "\\ No newline at end of file")?;
        }
    }
    Result::Ok(())
}

impl Display for FileDiff {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        self.display(&DisplaySettings::default(), f)
    }
}

struct GroupedHunkIterator<'a> {
    hunks: &'a [DiffHunk],
    next_hunk: usize,
    max_distance: u32,
}

impl<'a> Iterator for GroupedHunkIterator<'a> {
    type Item = Vec<&'a DiffHunk>;

    fn next(&mut self) -> Option<Self::Item> {
        let mut result = Vec::new();
        let mut last_line = None;
        while self.next_hunk < self.hunks.len() {
            let hunk = &self.hunks[self.next_hunk];
            if let Some(last_line) = last_line {
                if hunk.old_range.start - last_line > self.max_distance {
                    break;
                }
            }
            result.push(hunk);
            last_line = Some(hunk.old_range.end);
            self.next_hunk += 1;
        }
        if result.is_empty() {
            None
        } else {
            Some(result)
        }
    }
}

/// Internal wrapper to display a commit hash with a set length
struct CommitHash {
    swhid: Option<SWHID>,
    length: usize,
}

impl CommitHash {
    fn new(swhid: Option<SWHID>, length: usize) -> Self {
        Self { swhid, length }
    }
}

impl Display for CommitHash {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self.swhid {
            Some(swhid) => {
                for byte in swhid.hash.iter().take(self.length / 2) {
                    write!(f, "{byte:02x}")?;
                }
                Result::Ok(())
            }
            None => {
                write!(f, "{}", "0".repeat(self.length))
            }
        }
    }
}

/// Internal wrapper to display a line range like Git does
struct HunkRange(Range<u32>);

impl Display for HunkRange {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if self.0.start + 1 == self.0.end {
            write!(f, "{}", self.0.start + 1)
        } else {
            write!(f, "{},{}", self.0.start + 1, self.0.end - self.0.start)
        }
    }
}
