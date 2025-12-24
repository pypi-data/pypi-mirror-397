# OS.py Cloud Storage Library

A unified Python library for AWS S3, Azure Blob Storage, and GCP Cloud Storage operations with built-in retry logic, error handling, and CDN verification.

**Author:** Oleg Smirnov
**Repository:** https://github.com/BestianCode/os.py.lib.cloud

## Features

- **AWS S3 Support**: Upload files to S3 with automatic retry logic
- **Azure Blob Storage Support**: Upload to Azure with CDN verification
- **GCP Cloud Storage Support**: Upload to GCP using service account JSON
- **Unified Interface**: Consistent API for all storage providers
- **Automatic Retries**: Exponential backoff for resilient uploads
- **Environment-based Configuration**: Easy setup via environment variables

## Installation

### From GitHub

```bash
pip install git+https://github.com/BestianCode/os.py.lib.cloud.git
```

### From PyPI (once published)

```bash
pip install os-py-lib-cloud
```

### Development Installation

```bash
git clone https://github.com/BestianCode/os.py.lib.cloud.git
cd os.py.lib.cloud
pip install -e .
```

## Configuration

### AWS S3

Set the following environment variables:

```bash
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AWS_REGION="us-east-1"
export AWS_S3_BUCKET="your-bucket-name"
```

### Azure Blob Storage

```bash
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
export AZURE_CONTAINER_NAME="your-container-name"
```

### GCP Cloud Storage

```bash
export GCP_CREDENTIALS_FILE="/path/to/service-account.json"
export GCP_BUCKET_NAME="your-bucket-name"
export GCP_PROJECT_ID="your-project-id"  # optional
```

## Usage

### Basic S3 Example

```python
from os_cloud_storage import os_s3
from pathlib import Path

s3_initialized = os_s3.initialize_s3()

if s3_initialized:
    success, public_url, s3_url = os_s3.upload_to_s3(
        Path("/path/to/file.mp4"),
        s3_key="videos/my-video.mp4"
    )
    if success:
        print(f"Uploaded: {public_url}")
```

### Azure Blob Storage Example

```python
from os_cloud_storage import os_azure
from pathlib import Path

azure_initialized = os_azure.initialize_azure()

if azure_initialized:
    success, public_url, blob_url = os_azure.upload_to_azure(
        Path("/path/to/file.mp4"),
        blob_name="videos/my-video.mp4"
    )
    if success:
        print(f"Uploaded: {public_url}")
```

### GCP Cloud Storage Example

```python
from os_cloud_storage import os_gcp
from pathlib import Path

gcp_initialized = os_gcp.initialize_gcp()

if gcp_initialized:
    success, public_url, gcs_url = os_gcp.upload_to_gcp(
        Path("/path/to/file.mp4"),
        blob_name="videos/my-video.mp4"
    )
    if success:
        print(f"Uploaded: {public_url}")
```

### Multi-Provider Example

```python
from os_cloud_storage import os_s3, os_azure, os_gcp
from pathlib import Path

# Initialize providers
os_s3.initialize_s3()
os_azure.initialize_azure()
os_gcp.initialize_gcp()

# Upload with fallback
def upload_file(file_path):
    if os_s3.is_initialized():
        return os_s3.upload_to_s3(Path(file_path))
    elif os_azure.is_initialized():
        return os_azure.upload_to_azure(Path(file_path))
    elif os_gcp.is_initialized():
        return os_gcp.upload_to_gcp(Path(file_path))
    return False, None, None
```

## API Reference

### S3 Module (`os_s3`)

#### Functions

- **`initialize_s3(file_backend_url: str) -> bool`**
  - Initialize S3 client with environment variables
  - Returns: True if successful, False otherwise

- **`upload_to_s3(local_file_path: Path, s3_key: str = None, max_retries: int = 3, file_backend_url: str = None) -> Tuple[bool, str, str]`**
  - Upload a file to S3
  - Returns: (success, public_url, s3_url)

- **`is_initialized() -> bool`**
  - Check if S3 is initialized

- **`get_s3_client()`**
  - Get the boto3 S3 client

- **`get_bucket_name() -> str`**
  - Get the configured bucket name

- **`get_region() -> str`**
  - Get the configured AWS region

### Azure Module (`os_azure`)

#### Functions

- **`initialize_azure(file_backend_url: str) -> bool`**
  - Initialize Azure Blob Storage client with environment variables
  - Returns: True if successful, False otherwise

- **`upload_to_azure(local_file_path: Path, blob_name: str = None, max_retries: int = 3, file_backend_url: str = None) -> Tuple[bool, str, str]`**
  - Upload a file to Azure Blob Storage
  - Returns: (success, public_url, blob_url)

- **`is_initialized() -> bool`**
  - Check if Azure is initialized

- **`get_blob_service_client()`**
  - Get the BlobServiceClient

- **`get_container_client()`**
  - Get the ContainerClient

- **`get_container_name() -> str`**
  - Get the configured container name

### GCP Module (`os_gcp`)

#### Functions

- **`initialize_gcp(file_backend_url: str = None) -> bool`**
  - Initialize GCP client using service account JSON
  - Returns: True if successful, False otherwise

- **`upload_to_gcp(local_file_path: Path, blob_name: str = None, max_retries: int = 3, file_backend_url: str = None) -> Tuple[bool, str, str]`**
  - Upload a file to GCP Cloud Storage
  - Returns: (success, public_url, gcs_url)

- **`is_initialized() -> bool`**
  - Check if GCP is initialized

- **`get_storage_client()`**
  - Get the GCP storage client

- **`get_bucket()`**
  - Get the bucket object

- **`get_bucket_name() -> str`**
  - Get the configured bucket name

- **`get_project_id() -> str`**
  - Get the configured project ID

## Features in Detail

### Retry Logic

All providers include automatic retry with exponential backoff:
- Default: 3 retry attempts
- Configurable via `max_retries` parameter

### CDN Verification (Azure)

Azure uploads include automatic CDN verification:
- Checks if the uploaded blob is accessible via CDN
- Up to 32 retry attempts with 2-second delays
- Ensures the file is properly cached and accessible

### Path Management

- **Azure $web containers**: Uses flat paths
- **Azure/GCP regular containers**: Adds date-based paths (YYYY/MM/DD)
- **S3**: Preserves your specified key structure

### Error Handling

All functions return: `(success: bool, public_url: str, cloud_url: str)`

## Requirements

- Python >= 3.8
- boto3 >= 1.26.0
- azure-storage-blob >= 12.19.0
- google-cloud-storage >= 2.10.0
- requests >= 2.28.0

## License

BSD License

## Author

**Oleg Smirnov** - [@BestianCode](https://github.com/BestianCode)

## Changelog

### 1.0.2 (2025-12-19)
- Fixed GCP Cloud Storage file prefix

### 1.0.1 (2025-12-18)
- Added GCP Cloud Storage support
- Unified interface for all three providers

### 1.0.0 (2025-10-20)
- Initial release with S3 and Azure support
