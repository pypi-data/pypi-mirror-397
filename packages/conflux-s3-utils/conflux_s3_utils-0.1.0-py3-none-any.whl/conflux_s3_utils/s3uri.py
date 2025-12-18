from pathlib import PurePosixPath
from typing import NamedTuple
from urllib.parse import urlparse


__all__ = ["S3Uri"]


class S3Uri(NamedTuple):
    """
    A type-safe representation of an S3 URI.
    """

    bucket: str
    path: str

    @staticmethod
    def from_str(s3_uri_str: str) -> "S3Uri":
        """
        Parse an S3 URI string into an S3Uri object.
        S3 URI format: ``s3://bucket_name/path/to/object``
        """
        parsed = urlparse(s3_uri_str)
        assert parsed.scheme == "s3"
        path = parsed.path.lstrip("/")
        return S3Uri(bucket=parsed.netloc, path=path)

    def __str__(self) -> str:
        """
        Convert the S3Uri object back to an S3 URI string.
        S3 URI format: ``s3://bucket_name/path/to/object``
        """
        return f"s3://{self.bucket}/{self.path}"

    def join_path(self, *paths: str) -> "S3Uri":
        current_path = self.path.rstrip("/")
        suffix_path = "/".join(paths)
        return S3Uri(bucket=self.bucket, path=f"{current_path}/{suffix_path}")

    def __truediv__(self, path: str) -> "S3Uri":
        return self.join_path(path)

    def with_path(self, path: str) -> "S3Uri":
        return S3Uri(bucket=self.bucket, path=path.lstrip("/"))

    @property
    def filename(self) -> str:
        return PurePosixPath(self.path).name
