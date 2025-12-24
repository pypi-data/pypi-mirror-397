"""
GCP Cloud Storage Module
Handles all GCP Cloud Storage upload operations and client initialization
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from typing import Optional, Tuple

from google.cloud import storage
from google.oauth2 import service_account

logger                   = logging.getLogger(__name__)

# Environment variables
GCP_CREDENTIALS_FILE     = os.getenv("GCP_CREDENTIALS_FILE")
GCP_BUCKET_NAME          = os.getenv("GCP_BUCKET_NAME")
GCP_PROJECT_ID           = os.getenv("GCP_PROJECT_ID")

# Configuration
UPLOAD_RETRY_COUNT       = 3
RETRY_DELAY_BASE         = 1

# Global client
storage_client           = None
bucket                   = None


def initialize_gcp(file_backend_url: Optional[str] = None) -> bool:
    """
    Initialize GCP Cloud Storage client using service account JSON file.

    Args:
        file_backend_url: Optional base URL for building public URLs

    Returns:
        bool: True if initialized successfully, False otherwise
    """
    global storage_client, bucket

    if not GCP_CREDENTIALS_FILE or not GCP_BUCKET_NAME:
        logger.warning("GCP not configured (missing credentials file or bucket)")
        return False

    if not os.path.exists(GCP_CREDENTIALS_FILE):
        logger.error(f"GCP credentials file not found: {GCP_CREDENTIALS_FILE}")
        return False

    try:
        credentials = service_account.Credentials.from_service_account_file(
            GCP_CREDENTIALS_FILE
        )
        storage_client = storage.Client(
            credentials=credentials,
            project=GCP_PROJECT_ID
        )
        bucket = storage_client.bucket(GCP_BUCKET_NAME)

        # Verify bucket exists
        if not bucket.exists():
            logger.error(f"GCP bucket not found: {GCP_BUCKET_NAME}")
            storage_client = None
            bucket = None
            return False

        logger.info(f"GCP Cloud Storage initialized, bucket: {GCP_BUCKET_NAME}")
        return True

    except Exception as e:
        logger.error(f"GCP init error: {e}")
        storage_client = None
        bucket = None
        return False


def is_initialized() -> bool:
    """Check if GCP Cloud Storage client is initialized."""
    return storage_client is not None and bucket is not None


def upload_to_gcp(
    local_file_path: Path,
    blob_name: Optional[str] = None,
    max_retries: int = UPLOAD_RETRY_COUNT,
    file_backend_url: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Upload a file to GCP Cloud Storage.

    Args:
        local_file_path: Path to the local file
        blob_name: Object name (defaults to filename with date prefix)
        max_retries: Number of retry attempts
        file_backend_url: Optional base URL for building public URLs

    Returns:
        Tuple of (success, public_url, gcs_url)
    """
    if not storage_client or not bucket:
        logger.error("GCP Cloud Storage not initialized")
        return False, None, None

    if not blob_name:
        blob_name = local_file_path.name

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(
                f"GCP upload attempt {attempt}/{max_retries}: {local_file_path} -> gs://{GCP_BUCKET_NAME}/{blob_name}"
            )

            blob = bucket.blob(blob_name)
            blob.upload_from_filename(str(local_file_path))

            quoted_name = quote(blob_name)
            gcs_url = f"https://storage.googleapis.com/{GCP_BUCKET_NAME}/{quoted_name}"

            if file_backend_url:
                public_url = f"{file_backend_url}/{quoted_name}"
            else:
                public_url = gcs_url

            logger.info(f"Successfully uploaded to GCP: {gcs_url}")
            return True, public_url, gcs_url

        except Exception as e:
            logger.error(f"GCP upload failed on attempt {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(RETRY_DELAY_BASE * (2 ** (attempt - 1)))

    quoted_name = quote(blob_name)
    expected_url = f"https://storage.googleapis.com/{GCP_BUCKET_NAME}/{quoted_name}"
    return False, None, expected_url


def get_storage_client():
    """Get the initialized GCP storage client."""
    return storage_client


def get_bucket():
    """Get the initialized bucket object."""
    return bucket


def get_bucket_name() -> Optional[str]:
    """Get the configured bucket name."""
    return GCP_BUCKET_NAME


def get_project_id() -> Optional[str]:
    """Get the configured project ID."""
    return GCP_PROJECT_ID
