// Copyright (C) 2025  The Software Heritage developers
// See the AUTHORS file at the top-level directory of this distribution
// License: GNU General Public License version 3, or any later version
// See top-level LICENSE file for more information

//! Implementation of --node2sha1 and --url CLI arguments to build an HTTP retriever

use std::path::PathBuf;
use std::sync::Arc;

use anyhow::{bail, Context, Result};
use swh_graph::graph::SwhGraph;

use super::*;
use crate::sha1::Sha1Table;

#[derive(clap::Args, Debug)]
pub struct DownloadArgs {
    #[arg(long)]
    /// Map from node ids to SHA1 hash, as produced by `build-sha1-table`
    pub node2sha1: PathBuf,
    #[arg(long)]
    /// Must start with either `plain:` or `gzip:` and contain `{sha1}` (which will be substituted
    /// by each content's SHA1 hash).
    pub url: Vec<String>,
}

impl DownloadArgs {
    pub fn build_retriever(&self, graph: &impl SwhGraph) -> Result<impl ContentRetriever> {
        let client = reqwest::Client::builder()
            .user_agent(format!(
                "{}/{} (download-contents.rs)",
                env!("CARGO_PKG_NAME"),
                env!("CARGO_PKG_VERSION"),
            ))
            .build()
            .context("Could not build HTTP client")?;

        // Wrap client in retry middleware
        let retry_policy =
            reqwest_retry::policies::ExponentialBackoff::builder().build_with_max_retries(10);
        let client = reqwest_middleware::ClientBuilder::new(client)
            .with(http::Http429Middleware)
            .with(reqwest_retry::RetryTransientMiddleware::new_with_policy(
                retry_policy,
            ))
            .build();

        log::info!("Loading SHA1 table...");
        let node2sha1 = Arc::new(
            Sha1Table::mmap(graph.num_nodes(), &self.node2sha1)
                .with_context(|| format!("Could not mmap {}", self.node2sha1.display()))?,
        );

        log::info!("Initializing HTTP backends...");
        let http_backends = self
            .url
            .clone()
            .into_iter()
            .map(move |url| {
                let url = url.clone();
                let (compression, url_pattern) = url.split_once(':').with_context(|| {
                    format!("Missing URL prefix in {url}. Each URL must start with plain: or gzip:")
                })?;
                let compression = match compression {
                    "plain" => http::Compression::None,
                    "gzip" => http::Compression::Gzip,
                    _ => bail!("Unsupported compression algorithm {compression}"),
                };
                http::HttpContentRetriever::new(
                    Arc::clone(&node2sha1),
                    client.clone(),
                    url_pattern.to_owned(),
                    compression,
                )
                .with_context(move || format!("Could not build HttpContentRetriever for {url}"))
            })
            .collect::<Result<_>>()?;

        Ok(NLayeredContentRetriever {
            backends: http_backends,
        })
    }
}
