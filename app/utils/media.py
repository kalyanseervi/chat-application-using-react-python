import os
import magic


def validate_media(file_path: str, mime_type: str):
    """Validate file existence, size, and MIME type."""
    allowed_mime_types = {"image/jpeg", "image/png", "video/mp4"}
    if not os.path.exists(file_path):
        raise ValueError("File not found.")
    if os.path.getsize(file_path) > 10 * 1024 * 1024:  # 10 MB size limit
        raise ValueError("File exceeds size limit.")
    file_mime = magic.Magic(mime=True).from_file(file_path)
    if file_mime != mime_type or file_mime not in allowed_mime_types:
        raise ValueError(f"Unsupported media type: {file_mime}")