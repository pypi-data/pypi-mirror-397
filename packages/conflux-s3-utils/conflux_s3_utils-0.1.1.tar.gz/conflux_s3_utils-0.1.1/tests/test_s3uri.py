import pytest  # type: ignore[import-untyped]

from conflux_s3_utils import S3Uri


def test_s3uri_from_str():
    s3uri = S3Uri.from_str("s3://bucket/path/to/file")
    assert s3uri.bucket == "bucket"
    assert s3uri.path == "path/to/file"


def test_bucket_s3uri_from_str():
    s3uri = S3Uri.from_str("s3://bucket/")
    assert s3uri.bucket == "bucket"
    assert s3uri.path == ""
    s3uri = S3Uri.from_str("s3://bucket")
    assert s3uri.bucket == "bucket"
    assert s3uri.path == ""


@pytest.mark.parametrize(
    "s3uri_str", ["/bucket", "bucket/path/to/file", "file://bucket/path/to/file"]
)
def test_s3uri_from_str_fail(s3uri_str):
    with pytest.raises(Exception):
        S3Uri.from_str(s3uri_str)


def test_s3uri_to_str():
    s3uri = S3Uri("bucket", "path/to/file")
    assert str(s3uri) == "s3://bucket/path/to/file"


def test_join_path():
    s3uri = S3Uri("bucket", "path/to")
    new_s3uri = s3uri.join_path("file")
    assert s3uri == S3Uri("bucket", "path/to")
    assert new_s3uri == S3Uri("bucket", "path/to/file")
    newer_s3uri = s3uri.join_path("another", "file")
    assert newer_s3uri == S3Uri("bucket", "path/to/another/file")


def test_true_div():
    s3uri = S3Uri("bucket", "path/to")
    new_s3uri = s3uri / "file"
    assert s3uri == S3Uri("bucket", "path/to")
    assert new_s3uri == S3Uri("bucket", "path/to/file")
    newer_s3uri = s3uri / "another" / "file"
    assert newer_s3uri == S3Uri("bucket", "path/to/another/file")


def test_with_path():
    s3uri = S3Uri("bucket", "path/to/file")
    new_s3uri = s3uri.with_path("other/path/to/file")
    assert s3uri == S3Uri("bucket", "path/to/file")
    assert new_s3uri == S3Uri("bucket", "other/path/to/file")


def test_filename():
    s3uri = S3Uri("bucket", "path/to/file.txt")
    assert s3uri.filename == "file.txt"
