// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

//! Computing changes a revision made within a file
//!
//! See also [`swh_graph_stdlib::diff`] for changes of the directory trees if you do not need
//! access to textual changes.

pub mod contents;
#[allow(clippy::module_inception)] // module structure not final, to be reworked in swh-graph-libs
pub mod diff;
pub mod differ;
