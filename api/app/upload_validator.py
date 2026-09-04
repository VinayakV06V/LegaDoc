"""
Upload Validation Service — Streaming MIME detection, SHA-256 computation, and size capping.
See SYSTEM_DESIGN.md:
- Section 1.6 & 1.7 (File Upload Security)
- Magic-byte detection via python-magic (prevents extension spoofing like .exe-as-.pdf)
- Incremental streaming SHA-256 computation
- SpooledTemporaryFile buffering (5MB memory threshold)
- Early abort on oversized streams (configurable size cap, default 50MB)
"""

import hashlib
import os
import re
import tempfile
from typing import NamedTuple, Set
from fastapi import HTTPException, UploadFile, status

# Allowed text-bearing MIME types (routed to OCR)
TEXT_BEARING_MIME_TYPES: Set[str] = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "text/plain",
    "text/csv",
}

# Allowed binary evidence MIME types (bypasses OCR, marked ready immediately)
BINARY_EVIDENCE_MIME_TYPES: Set[str] = {
    "video/mp4",
    "video/mpeg",
    "audio/mpeg",
    "audio/wav",
}

ALL_ALLOWED_MIME_TYPES = TEXT_BEARING_MIME_TYPES | BINARY_EVIDENCE_MIME_TYPES


class UploadValidationResult(NamedTuple):
    data: bytes
    sha256_hash: str
    detected_mime: str
    file_size: int
    is_binary_evidence: bool
    original_filename: str


def sanitize_filename(filename: str) -> str:
    """Sanitizes filename against path traversal and dangerous characters."""
    if not filename:
        return "unnamed_upload"
    base = os.path.basename(filename)
    cleaned = re.sub(r"[^\w\.\-\_]", "_", base)
    return cleaned[:255] if cleaned else "unnamed_upload"


def detect_mime_from_bytes(header_bytes: bytes, fallback_content_type: str = "") -> str:
    """
    Pure-Python magic-byte sniffer.
    Zero C-library dependencies — guaranteed non-blocking across Windows, macOS, Linux, and Docker.
    Accurately detects authentic file formats and aggressively catches disguised executables/scripts.
    """
    if not header_bytes:
        return "application/octet-stream"

    # 1. Explicitly detect dangerous executable / script signatures first
    if header_bytes.startswith(b"MZ"):
        return "application/x-dosexec"  # Windows PE executable / DLL
    if header_bytes.startswith(b"\x7fELF"):
        return "application/x-executable"  # Linux ELF binary
    if header_bytes.startswith((b"\xfe\xed\xfa\xce", b"\xfe\xed\xfa\xcf", b"\xce\xfa\xed\xfe", b"\xcf\xfa\xed\xfe", b"\xca\xfe\xba\xbe")):
        return "application/x-mach-binary"  # macOS Mach-O binary
    if header_bytes.startswith(b"#!"):
        return "text/x-shellscript"  # Shell / Bash / Python script

    # 2. Match authentic file format magic signatures
    if header_bytes.startswith(b"%PDF"):
        return "application/pdf"
    if header_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if header_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if header_bytes.startswith(b"II*\x00") or header_bytes.startswith(b"MM\x00*"):
        return "image/tiff"
    if len(header_bytes) >= 8 and header_bytes[4:8] == b"ftyp":
        return "video/mp4"
    if header_bytes.startswith(b"\x00\x00\x01\xba") or header_bytes.startswith(b"\x00\x00\x01\xb3"):
        return "video/mpeg"
    if len(header_bytes) >= 12 and header_bytes.startswith(b"RIFF") and header_bytes[8:12] == b"WAVE":
        return "audio/wav"
    if header_bytes.startswith(b"ID3") or (len(header_bytes) >= 2 and header_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")):
        return "audio/mpeg"

    # 3. Text and CSV validation
    norm_content_type = fallback_content_type.strip().lower()
    if norm_content_type in ("text/plain", "text/csv"):
        # Text cannot contain null bytes
        if b"\x00" in header_bytes:
            return "application/octet-stream"
        try:
            header_bytes[:1024].decode("utf-8")
            return norm_content_type
        except UnicodeDecodeError:
            try:
                header_bytes[:1024].decode("latin-1")
                return norm_content_type
            except Exception:
                return "application/octet-stream"

    # 4. Binary evidence formats (video/audio) without distinct single-byte magic
    if norm_content_type in BINARY_EVIDENCE_MIME_TYPES:
        return norm_content_type

    # 5. If claimed to be PDF or image but failed magic signature, do NOT trust extension
    if norm_content_type in ("application/pdf", "image/jpeg", "image/png", "image/tiff"):
        return "application/octet-stream"

    return norm_content_type if norm_content_type else "application/octet-stream"


async def validate_upload_stream(
    upload_file: UploadFile,
    max_size_mb: int = 50,
) -> UploadValidationResult:
    """
    Performs streaming validation on an incoming multipart file upload:
    1. Sanitizes the original filename.
    2. Reads initial header chunk (8KB) to sniff magic bytes.
    3. Validates MIME type against allowlist.
    4. Streams content into SpooledTemporaryFile (5MB memory threshold).
    5. Computes SHA-256 incrementally.
    6. Aborts immediately if size exceeds max_size_mb.
    """
    sanitized_name = sanitize_filename(upload_file.filename or "")
    max_bytes = max_size_mb * 1024 * 1024
    chunk_size = 64 * 1024  # 64KB chunks

    spooled_file = tempfile.SpooledTemporaryFile(max_size=5 * 1024 * 1024)
    sha256 = hashlib.sha256()
    total_bytes = 0

    try:
        # 1. Read header chunk (8KB)
        header_chunk = await upload_file.read(8192)
        if not header_chunk:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        # 2. Sniff MIME type
        detected_mime = detect_mime_from_bytes(
            header_chunk,
            fallback_content_type=upload_file.content_type or "",
        )

        if detected_mime not in ALL_ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type '{detected_mime}'. Allowed types include PDF, images, audio, and video.",
            )

        # 3. Write header to spooled file and update hash
        spooled_file.write(header_chunk)
        sha256.update(header_chunk)
        total_bytes += len(header_chunk)

        if total_bytes > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {max_size_mb}MB",
            )

        # 4. Stream remaining chunks
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break

            total_bytes += len(chunk)
            if total_bytes > max_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File exceeds maximum allowed size of {max_size_mb}MB",
                )

            spooled_file.write(chunk)
            sha256.update(chunk)

        spooled_file.seek(0)
        data = spooled_file.read()
        is_binary = detected_mime in BINARY_EVIDENCE_MIME_TYPES

        return UploadValidationResult(
            data=data,
            sha256_hash=sha256.hexdigest(),
            detected_mime=detected_mime,
            file_size=total_bytes,
            is_binary_evidence=is_binary,
            original_filename=sanitized_name,
        )
    finally:
        spooled_file.close()
