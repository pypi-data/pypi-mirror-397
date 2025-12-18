// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

#![allow(dead_code)]

use swh_graph::graph_builder::{BuiltGraph, GraphBuilder};
use swh_graph::labels::Permission;
use swh_graph::swhid;

pub fn get_4rev_graph() -> GraphBuilder {
    let mut builder = GraphBuilder::default();
    let snp = builder
        .node(swhid!(swh:1:snp:0000000000000000000000000000000000000000))
        .unwrap()
        .done();
    let rev1 = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000001))
        .unwrap()
        .done();
    let rev2 = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000002))
        .unwrap()
        .done();
    let rev3 = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000003))
        .unwrap()
        .done();
    let rev4 = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000004))
        .unwrap()
        .done();
    let dir1 = builder
        .node(swhid!(swh:1:dir:0000000000000000000000000000000000000011))
        .unwrap()
        .done();
    let dir2 = builder
        .node(swhid!(swh:1:dir:0000000000000000000000000000000000000012))
        .unwrap()
        .done();
    let dir3 = builder
        .node(swhid!(swh:1:dir:0000000000000000000000000000000000000013))
        .unwrap()
        .done();
    let dir4 = builder
        .node(swhid!(swh:1:dir:0000000000000000000000000000000000000014))
        .unwrap()
        .done();
    let cnt1 = builder
        .node(swhid!(swh:1:cnt:2100000000000000000000000000000000000000))
        .unwrap()
        .done();
    let cnt2 = builder
        .node(swhid!(swh:1:cnt:2200000000000000000000000000000000000000))
        .unwrap()
        .done();
    let cnt3 = builder
        .node(swhid!(swh:1:cnt:2300000000000000000000000000000000000000))
        .unwrap()
        .done();
    let cnt4 = builder
        .node(swhid!(swh:1:cnt:2400000000000000000000000000000000000000))
        .unwrap()
        .done();

    // snapshot
    builder.arc(snp, rev1);
    builder.arc(snp, rev2);
    builder.arc(snp, rev3);
    builder.arc(snp, rev4);

    // rev1's tree
    builder.arc(rev1, dir1);
    builder.dir_arc(dir1, cnt1, Permission::Content, b"test.txt");

    // rev2's tree
    builder.arc(rev2, dir2);
    builder.dir_arc(dir2, cnt2, Permission::Content, b"test.txt");

    // rev3's tree
    builder.arc(rev3, dir3);
    builder.dir_arc(dir3, cnt3, Permission::Content, b"test.txt");

    // rev4's tree
    builder.arc(rev4, dir4);
    builder.dir_arc(dir4, cnt4, Permission::Content, b"test.txt");

    builder
}

pub fn get_merge_graph() -> BuiltGraph {
    let mut builder = get_4rev_graph();

    // rev3 is a merge of rev1 and rev2
    builder.arc(3, 1);
    builder.arc(3, 2);

    builder.done().unwrap()
}

pub fn get_3_way_merge_graph() -> BuiltGraph {
    let mut builder = get_4rev_graph();

    // rev4 is a merge of rev1, rev2, and rev3
    builder.arc(4, 1);
    builder.arc(4, 2);
    builder.arc(4, 3);

    builder.done().unwrap()
}

pub fn get_diamond_graph() -> BuiltGraph {
    let mut builder = get_4rev_graph();

    // rev4 is a merge of rev2 and rev3
    builder.arc(4, 2);
    builder.arc(4, 3);
    // rev2 and rev3 are both based on rev1
    builder.arc(2, 1);
    builder.arc(3, 1);

    builder.done().unwrap()
}

pub fn get_linear_graph() -> BuiltGraph {
    let mut builder = get_4rev_graph();

    // rev1 is parent of rev2, itself parent of rev3, itself parent of rev4
    builder.arc(4, 3);
    builder.arc(3, 2);
    builder.arc(2, 1);

    builder.done().unwrap()
}

pub fn get_file_creation_graph() -> (usize, usize, BuiltGraph) {
    let mut builder = GraphBuilder::default();
    let rev1 = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000001))
        .unwrap()
        .done();
    let rev2 = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000002))
        .unwrap()
        .done();
    let dir1 = builder
        .node(swhid!(swh:1:dir:0000000000000000000000000000000000000011))
        .unwrap()
        .done();
    let dir2 = builder
        .node(swhid!(swh:1:dir:0000000000000000000000000000000000000012))
        .unwrap()
        .done();
    let cnt1 = builder
        .node(swhid!(swh:1:cnt:2100000000000000000000000000000000000000))
        .unwrap()
        .done();

    // rev1's tree
    builder.arc(rev1, dir1);

    // rev2's tree
    builder.arc(rev2, dir2);
    builder.dir_arc(dir2, cnt1, Permission::Content, b"test.txt");

    // rev1 is parent of rev2
    builder.arc(rev2, rev1);

    (rev1, rev2, builder.done().unwrap())
}

pub fn get_1rev_graph() -> BuiltGraph {
    let mut builder = GraphBuilder::default();
    let snp = builder
        .node(swhid!(swh:1:snp:0000000000000000000000000000000000000000))
        .unwrap()
        .done();
    let rev1 = builder
        .node(swhid!(swh:1:rev:0000000000000000000000000000000000000001))
        .unwrap()
        .done();
    let dir1 = builder
        .node(swhid!(swh:1:dir:0000000000000000000000000000000000000011))
        .unwrap()
        .done();
    let cnt1 = builder
        .node(swhid!(swh:1:cnt:2100000000000000000000000000000000000000))
        .unwrap()
        .done();

    builder.arc(snp, rev1);
    builder.arc(rev1, dir1);
    builder.dir_arc(dir1, cnt1, Permission::Content, b"test.txt");
    builder.done().unwrap()
}

#[allow(unused_macros)]
macro_rules! get_content_retriever {
    ($graph:expr, [$($content:expr),* $(,)?]) => {{
        use swh_contents::retriever::{ContentCache, InMemoryContentCache};

        let mut swhid = SWHID {
            namespace_version: 1,
            node_type: NodeType::Content,
            hash: [0; 20],
        };
        let content_retriever = InMemoryContentCache::default();

        let i = 0x20;
        $(
            let i = i+1;
            swhid.hash[0] = i;
            let node_id = $graph.properties().node_id(swhid).unwrap();
            content_retriever.set(node_id, $content).await.unwrap();
        )*

        std::sync::Arc::new(content_retriever)
    }}
}

#[allow(unused_imports)]
pub(crate) use get_content_retriever;
