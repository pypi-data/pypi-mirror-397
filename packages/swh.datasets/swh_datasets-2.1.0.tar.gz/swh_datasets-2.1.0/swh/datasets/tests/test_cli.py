# Copyright (C) 2019-2025  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
from pathlib import Path

from click.testing import CliRunner
import pytest

from swh.datasets.cli import datasets_cli_group


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.mark.parametrize("exit_code", [0, 1])
def test_luigi(mocker, tmp_path, exit_code, cli_runner):
    """calls Luigi with the given configuration"""
    # bare bone configuration, to allow testing the compression pipeline
    # with minimum RAM requirements on trivial graphs

    subprocess_run = mocker.patch("subprocess.run")
    subprocess_run.return_value.returncode = exit_code

    result = cli_runner.invoke(
        datasets_cli_group,
        [
            "luigi",
            "--base-directory",
            f"{tmp_path}/base_dir",
            "--dataset-name",
            "2022-12-07",
            "--",
            "foo",
            "bar",
            "--baz",
            "qux",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == exit_code, result.output

    luigi_config_path = subprocess_run.mock_calls[0][2]["env"]["LUIGI_CONFIG_PATH"]
    subprocess_run.assert_called_once_with(
        [
            "luigi",
            "--module",
            "swh.export.luigi",
            "--module",
            "swh.graph.luigi",
            "--module",
            "swh.datasets.luigi",
            "foo",
            "bar",
            "--baz",
            "qux",
        ],
        env={"LUIGI_CONFIG_PATH": luigi_config_path, **os.environ},
    )


def test_download_graph(cli_runner, s3_graph_dataset_name, tmp_path, mocked_aws):
    result = cli_runner.invoke(
        datasets_cli_group,
        [
            "download-graph",
            "--name",
            s3_graph_dataset_name,
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.output
    assert Path(tmp_path / "example.graph").exists()
    assert Path(tmp_path / "meta/compression.json").exists()


def test_download_export_ok(cli_runner, s3_graph_dataset_name, tmp_path, mocked_aws):
    result = cli_runner.invoke(
        datasets_cli_group,
        [
            "download-export",
            "--name",
            s3_graph_dataset_name,
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.output

    assert Path(tmp_path / "content/content-all.orc").exists()
    assert Path(tmp_path / "meta/export.json").exists()
    assert Path(tmp_path / "meta/foo/bar.json").exists()

    assert (
        f"ORC dataset {s3_graph_dataset_name} successfully downloaded to path {tmp_path}."
    ) in result.output


def test_download_export_resumption(
    cli_runner, s3_graph_dataset_name, mocker, tmp_path, mocked_aws
):
    mocker.patch("swh.datasets.download.DatasetDownloader.download").side_effect = [
        False,
        True,
    ]
    result = cli_runner.invoke(
        datasets_cli_group,
        [
            "download-export",
            "--name",
            s3_graph_dataset_name,
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.output

    assert (
        f"ORC dataset {s3_graph_dataset_name} successfully downloaded to path {tmp_path}."
    ) in result.output
