# Copyright (C) 2025 The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List

from swh.core.s3.downloader import S3Downloader

if TYPE_CHECKING:
    from types_boto3_s3.service_resource import ObjectSummary

logger = logging.getLogger(__name__)


class DatasetDownloader(S3Downloader):
    """Utility class to help downloading SWH datasets (ORC exports for instance)
    from S3.

    It also implements a download resumption feature in case some files fail to
    be downloaded (when connection errors happen for instance).

    Example of use::

        from swh.datasets.download import DatasetDownloader

        # download "2025-05-18-popular-1k" ORC dataset into a sub-directory of the
        # current working directory named "2025-05-18-popular-1k-orc"

        dataset_downloader = DatasetDownloader(
            local_path="2025-05-18-popular-1k-orc",
            s3_url="s3://softareheritage/graph/2025-05-18-popular-1k/orc/",
        )

        while not dataset_downloader.download():
            continue
    """

    def filter_objects(self, objects: List[ObjectSummary]) -> List[ObjectSummary]:
        # filter out JSON metadata files, they will be downloaded after all other files
        return [obj for obj in objects if not obj.key.endswith(".json")]

    def post_downloads(self) -> None:
        # download JSON metadata files as stamps after data files
        for obj in self.bucket.objects.filter(Prefix=self.prefix):
            if obj.key.endswith(".json"):
                self._download_file(obj.key)

        # also download {s3_url}/../meta/ contents if available
        prefix = self.prefix.rsplit("/", 2)[0] + "/meta/"
        for obj in self.bucket.objects.filter(Prefix=prefix):
            sub_path = obj.key.split("/meta/")[-1]
            self._download_file(
                obj.key,
                local_file_path=self.local_path / "meta" / sub_path,
                prefix=prefix,
            )
