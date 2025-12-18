import concurrent.futures
from contextlib import contextmanager
from pathlib import Path
import tempfile
from typing import Iterable, Optional, TYPE_CHECKING

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.config import Config
import fsspec  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client as Boto3S3Client

from conflux_s3_utils.s3uri import S3Uri

# If this gets _too_ high, we will start getting 503 (SlowDown) errors from S3.
_DEFAULT_DIRECTORY_UPLOAD_CONCURRENCY = 10

# For now we re-use the chunk size as the threshold as well, although we
# could separate them.
# In boto3, the default is 8MB for both.
_DEFAULT_MULTIPART_CHUNKSIZE_MB = 8
_DEFAULT_MULTIPART_CHUNKSIZE_BYTES = _DEFAULT_MULTIPART_CHUNKSIZE_MB * 1024 * 1024


class S3Client:
    """
    A S3 client that interacts with S3 using type-safe ``S3Uri`` objects
    and provides convenient methods for common operations.
    """

    def __init__(
        self,
        client: Optional["Boto3S3Client"] = None,
    ):
        """
        Initialize an S3Client.
        If ``client`` is not provided, a default boto3 S3 client will be created
        """
        if client is not None:
            self.client = client
            return
        # Don't rely on the default retry mode which is "legacy" with 5 attempts.
        # Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html#available-retry-modes
        config = Config(retries={"mode": "standard", "max_attempts": 5})
        self.client = boto3.client("s3", config=config)

    def open(self, s3uri: S3Uri, mode: str = "rb") -> fsspec.core.OpenFile:
        """Open an S3 object as a file-like object using fsspec.
        Note that this can be used with a context manager:

        .. code-block:: python

            s3 = S3Client()
            with s3.open(s3uri) as f:
                # Do stuff with `f`.
                # It will automatically be closed when exiting the block.
        """
        file = fsspec.open(str(s3uri), mode=mode)
        assert isinstance(file, fsspec.core.OpenFile)
        return file

    @contextmanager
    def open_local(
        self,
        s3uri: S3Uri,
        mode: str = "rb",
        multipart_chunksize: int = _DEFAULT_MULTIPART_CHUNKSIZE_BYTES,
    ):
        """
        Interact with an object in S3 by opening a corresponding file locally.

        With read mode (``mode`` contains "r"), the object is downloaded from S3 into
        a temporary directory and then a file handle to the local file is provided.
        The file and the temporary directory are cleaned up when the context manager exits.

        With write mode (``mode`` contains "w"), a file is created in a temporary directory
        and a file handle to the local file is provided. Upon exiting the context manager,
        the file is uploaded to S3.
        The file and temporary directry are cleaned up when the context manager exits.
        """
        assert mode in {"r", "rb", "rt", "w", "wb", "wt"}
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            local_filepath = tmpdir_path / s3uri.filename
            if "r" in mode:
                self.download_file(s3uri, local_filepath, multipart_chunksize)
                f = open(local_filepath, mode)
                try:
                    yield f
                finally:
                    f.close()
            elif "w" in mode:
                f = open(local_filepath, mode)
                try:
                    yield f
                finally:
                    f.close()
                    self.upload_file(local_filepath, s3uri, multipart_chunksize)

    def object_exists(self, s3uri: S3Uri) -> bool:
        """
        Check if an object exists in S3.
        """
        try:
            self.client.head_object(Bucket=s3uri.bucket, Key=s3uri.path)
            return True
        except self.client.exceptions.NoSuchKey:
            return False
        # HeadObject response with non-existing object generally yields a 404,
        # not a NoSuchKey error.
        except self.client.exceptions.ClientError as e:
            if (
                "Error" in e.response
                and "Code" in e.response["Error"]
                and e.response["Error"]["Code"] == "404"
            ):
                return False
            raise e

    def delete_object(self, s3uri: S3Uri):
        """
        Delete an object in S3.
        """
        self.client.delete_object(Bucket=s3uri.bucket, Key=s3uri.path)

    def list_objects(self, s3uri: S3Uri, recursive=False) -> Iterable[S3Uri]:
        """
        List objects under the given S3 URI, assuming it is a "directory".
        If ``recursive`` is ``False``, only list objects directly under the given path.
        """
        path = s3uri.path.rstrip("/")
        bucket = s3uri.bucket
        delimiter = "" if recursive else "/"
        prefix = "" if path == "" else f"{path}/"
        paginator = self.client.get_paginator("list_objects_v2")
        page_iterator = paginator.paginate(
            Bucket=bucket, Prefix=prefix, Delimiter=delimiter
        )
        for page in page_iterator:
            for obj in page.get("Contents", []):
                if "Key" in obj:
                    yield S3Uri(bucket, obj["Key"])

    def copy_object(self, src: S3Uri, dest: S3Uri) -> None:
        """
        Copy an object from ``src`` to ``dest``.
        """
        self.client.copy_object(
            Bucket=dest.bucket,
            Key=dest.path,
            CopySource={"Bucket": src.bucket, "Key": src.path},
        )

    def upload_file(
        self,
        filepath: Path,
        s3uri: S3Uri,
        multipart_chunksize: int = _DEFAULT_MULTIPART_CHUNKSIZE_BYTES,
    ) -> None:
        """
        Upload a file to the specified S3 URI.
        """
        config = TransferConfig(
            multipart_chunksize=multipart_chunksize,
            multipart_threshold=multipart_chunksize,
        )
        self.client.upload_file(str(filepath), s3uri.bucket, s3uri.path, Config=config)

    def download_file(
        self,
        s3uri: S3Uri,
        filepath: Path,
        multipart_chunksize: int = _DEFAULT_MULTIPART_CHUNKSIZE_BYTES,
    ) -> None:
        """
        Download a file from the specified S3 URI.
        """
        config = TransferConfig(
            multipart_chunksize=multipart_chunksize,
            multipart_threshold=multipart_chunksize,
        )
        self.client.download_file(
            s3uri.bucket, s3uri.path, str(filepath), Config=config
        )

    def upload_directory(
        self,
        dirpath: Path,
        s3uri: S3Uri,
        multipart_chunksize: int = _DEFAULT_MULTIPART_CHUNKSIZE_BYTES,
        concurrency: int = _DEFAULT_DIRECTORY_UPLOAD_CONCURRENCY,
        exclude: set[Path] = set(),
    ) -> None:
        """
        Upload a local directory to the specified S3 URI.
        The directory structure is preserved in S3.
        """
        if concurrency > 1:
            self._upload_directory_concurrent(
                dirpath, s3uri, multipart_chunksize, concurrency, exclude
            )
        else:
            self._upload_directory_single(dirpath, s3uri, multipart_chunksize, exclude)

    def _yield_upload_files(
        self,
        dirpath: Path,
        s3uri: S3Uri,
        exclude: set[Path] = set(),
    ) -> Iterable[tuple[Path, S3Uri]]:
        for root, _, files in dirpath.walk():
            for filename in files:
                filepath = root / filename
                relative_path = filepath.relative_to(dirpath)
                if relative_path in exclude:
                    continue
                yield filepath, s3uri.join_path(str(relative_path))

    def _upload_directory_single(
        self,
        dirpath: Path,
        s3uri: S3Uri,
        multipart_chunksize: int,
        exclude: set[Path] = set(),
    ) -> None:
        for filepath, upload_s3uri in self._yield_upload_files(dirpath, s3uri, exclude):
            self.upload_file(
                filepath, upload_s3uri, multipart_chunksize=multipart_chunksize
            )

    def _upload_directory_concurrent(
        self,
        dirpath: Path,
        s3uri: S3Uri,
        multipart_chunksize: int,
        concurrency: int,
        exclude: set[Path] = set(),
    ) -> None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for filepath, upload_s3uri in self._yield_upload_files(
                dirpath, s3uri, exclude
            ):
                future = executor.submit(
                    self.upload_file, filepath, upload_s3uri, multipart_chunksize
                )
                futures.append(future)

            for future in concurrent.futures.as_completed(futures):
                # Re-raise any exceptions that might have been thrown by `self.upload_file`
                future.result()
