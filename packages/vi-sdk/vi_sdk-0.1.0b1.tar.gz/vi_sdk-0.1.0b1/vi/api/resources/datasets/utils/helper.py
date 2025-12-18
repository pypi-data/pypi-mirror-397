#!/usr/bin/env python

"""████
 ██    ██    Datature
   ██  ██    Powering Breakthrough AI
     ██

@File    :   helper.py
@Author  :   Wei Loon Cheng
@Contact :   developers@datature.io
@License :   Apache License 2.0
@Desc    :   Datature Vi SDK utils helper module.
"""

import struct
from base64 import b64encode
from pathlib import Path

import google_crc32c

DEFAULT_CHUNK_SIZE = 8 * 1024 * 1024  # 8MB


def calculate_crc32c(
    file_path: Path | str,
    base64_encoded: bool = False,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> int | str:
    """Calculate CRC32C checksum for a file using chunked reading.

    Reads the file in chunks to avoid loading the entire file into memory,
    which is important for large files.

    Args:
        file_path: Path to the file to checksum.
        base64_encoded: Whether to return base64-encoded checksum.
        chunk_size: Size of chunks to read at a time in bytes.
            Defaults to 8MB. Smaller values use less memory but may be slower.

    Returns:
        The CRC32C checksum as integer or base64 string.

    """
    checksum = google_crc32c.Checksum()

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            checksum.update(chunk)

    if base64_encoded:
        return b64encode(checksum.digest()).decode("utf-8")

    return struct.unpack(">l", checksum.digest())[0]


def build_dataset_id(organization_id: str, dataset_id: str) -> str:
    """Build dataset ID with organization ID prefix.

    Args:
        organization_id: The organization ID.
        dataset_id: The dataset ID.

    Returns:
        The combined dataset ID in format: {organization_id}_{dataset_id}.

    """
    return f"{organization_id}_{dataset_id}"
