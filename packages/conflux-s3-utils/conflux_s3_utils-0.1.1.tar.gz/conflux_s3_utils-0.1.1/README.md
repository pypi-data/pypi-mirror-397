# Conflux S3 Utils

A Python library providing type-safe interfaces and convenient utilities for interacting with objects in S3.

## Installation

```
pip install conflux-s3-utils
```

## Usage

The primitives in this library are [`S3Uri`](./conflux_s3_utils/s3uri.py) and [`S3Client`](./conflux_s3_utils/s3client.py).

* `S3Uri` provides a type-safe way to specify S3 URIs, in the spirit of [parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/).
* `S3Client` is a client that provides convenient methods for interacting with S3 objects specified via their `S3Uri`.

### `S3Uri`

`S3Uri` is a type-safe representation of an S3 URI that provides convenient methods for path manipulation.

#### Parsing and String Conversion

```python
from conflux_s3_utils import S3Uri

# Parse from a S3 URI string
s3uri = S3Uri.from_str("s3://bucket/path/to/object.txt")

# Access bucket and path components
assert s3uri.bucket == "bucket"
assert s3uri.path == "path/to/object.txt"

# Get just the filename
assert s3uri.filename == "object.txt"

# Convert back to a S3 URI string
assert str(s3uri) == "s3://bucket/path/to/object.txt"
```

#### Path Manipulation

```python
# Replace the entire path
s3uri_dir = s3uri.with_path("new/path/directory")
assert s3uri_dir.bucket == "bucket"
assert s3uri_dir.path == "new/path/directory"

# Join paths using the slash operator
child_s3uri = s3uri_dir / "subfolder" / "file.txt"
assert child_s3uri.path == "new/path/directory/subfolder/file.txt"

# Join paths using join_path method
child_s3uri = s3uri_dir.join_path("subfolder", "file.txt")
assert child_s3uri.path == "new/path/directory/subfolder/file.txt"
```

### `S3Client`

`S3Client` provides convenient methods for interacting with S3 objects using type-safe `S3Uri` objects.

#### Initialization

```python
from conflux_s3_utils import S3Client, S3Uri

# Create a client with default boto3 configuration
s3 = S3Client()

# Or provide your own boto3 client
import boto3
custom_client = boto3.client('s3', region_name='us-west-2')
s3 = S3Client(client=custom_client)
```

#### Opening Files

```python
# Open an S3 object directly using fsspec
s3uri = S3Uri.from_str("s3://bucket/data.json")
with s3.open(s3uri, mode="rb") as f:
    data = f.read()

# Open with write mode
with s3.open(s3uri, mode="wb") as f:
    f.write(b"Hello, S3!")
```

#### Working with Local Files

The `open_local` method downloads or uploads S3 objects via temporary local files, which is useful for libraries that require local file paths.

```python
# Read mode: Download from S3, work with local file
s3uri = S3Uri.from_str("s3://bucket/data.csv")
with s3.open_local(s3uri, mode="rb") as f:
    # File is downloaded to a temporary location
    # f is a standard Python file handle
    data = f.read()
# Temporary file is automatically cleaned up

# Write mode: Work with local file, upload to S3
with s3.open_local(s3uri, mode="wb") as f:
    # f is a standard Python file handle to a temporary file
    f.write(b"New data")
# File is automatically uploaded to S3 and cleaned up
```

#### Checking Object Existence

```python
s3uri = S3Uri.from_str("s3://bucket/path/to/object.txt")
if s3.object_exists(s3uri):
    print("Object exists!")
```

#### Listing Objects

```python
# List objects directly under a path (non-recursive)
s3uri = S3Uri.from_str("s3://bucket/path/to/directory")
for obj_uri in s3.list_objects(s3uri):
    print(obj_uri)

# List all objects recursively
for obj_uri in s3.list_objects(s3uri, recursive=True):
    print(obj_uri)
```

#### Uploading and Downloading Files

```python
from pathlib import Path

# Upload a local file
local_file = Path("./local/data.txt")
s3uri = S3Uri.from_str("s3://bucket/remote/data.txt")
s3.upload_file(local_file, s3uri)

# Download a file
s3.download_file(s3uri, local_file)

# Customize multipart upload/download chunk size (default 8MB)
s3.upload_file(local_file, s3uri, multipart_chunksize=16*1024*1024)  # 16MB chunks
```

#### Uploading Directories

```python
from pathlib import Path

# Upload an entire directory
local_dir = Path("./local/directory")
s3uri = S3Uri.from_str("s3://bucket/remote/directory")
s3.upload_directory(local_dir, s3uri)

# Upload with custom concurrency (default is 10 concurrent uploads)
s3.upload_directory(local_dir, s3uri, concurrency=5)

# Exclude specific files
exclude = {Path("secret.txt"), Path("cache/temp.dat")}
s3.upload_directory(local_dir, s3uri, exclude=exclude)
```

#### Copying and Deleting Objects

```python
# Copy an object within S3
src = S3Uri.from_str("s3://bucket/source/file.txt")
dest = S3Uri.from_str("s3://bucket/destination/file.txt")
s3.copy_object(src, dest)

# Delete an object
s3.delete_object(s3uri)
```

### Complete Example

```python
from pathlib import Path
from conflux_s3_utils import S3Client, S3Uri

# Initialize client
s3 = S3Client()

# Parse S3 URIs
base_uri = S3Uri.from_str("s3://my-bucket/data")
input_uri = base_uri / "input" / "data.csv"
output_uri = base_uri / "output" / "results.txt"

# Check if input exists
if not s3.object_exists(input_uri):
    raise ValueError(f"Input file not found: {input_uri}")

# Download and process
local_input = Path("./temp/input.csv")
s3.download_file(input_uri, local_input)

# Process the file
with open(local_input, "r") as f:
    # Your processing logic here
    processed_data = f.read().upper()

# Upload results
local_output = Path("./temp/output.txt")
with open(local_output, "w") as f:
    f.write(processed_data)
s3.upload_file(local_output, output_uri)

print(f"Results uploaded to: {output_uri}")
```