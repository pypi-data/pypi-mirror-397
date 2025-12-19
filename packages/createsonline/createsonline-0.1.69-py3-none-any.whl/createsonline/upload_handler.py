"""
CREATESONLINE File Upload Handler
Simple image/file upload handler for rich text editor

Pure Python - Zero external dependencies
"""
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Optional, Tuple, List
from datetime import datetime


class UploadHandler:
    """
    Handle file uploads for the rich text editor.

    Features:
    - Image validation (type, size)
    - Secure filename generation
    - Automatic directory creation
    - Multiple upload directory strategies
    - URL generation
    """

    def __init__(
        self,
        upload_dir: str = "uploads",
        allowed_extensions: Optional[List[str]] = None,
        max_size: int = 5 * 1024 * 1024,  # 5MB
        organize_by: str = "date",  # "date", "hash", "flat"
        base_url: str = "/uploads"
    ):
        """
        Initialize upload handler.

        Args:
            upload_dir: Base directory for uploads (default: "uploads")
            allowed_extensions: List of allowed file extensions (default: images only)
            max_size: Maximum file size in bytes (default: 5MB)
            organize_by: How to organize uploaded files ("date", "hash", "flat")
            base_url: Base URL for serving uploaded files (default: "/uploads")
        """
        self.upload_dir = Path(upload_dir)
        self.allowed_extensions = allowed_extensions or [
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'
        ]
        self.max_size = max_size
        self.organize_by = organize_by
        self.base_url = base_url.rstrip('/')

        # Ensure upload directory exists
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, filename: str, file_data: bytes) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file.

        Args:
            filename: Original filename
            file_data: File content as bytes

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(file_data) > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            return False, f"File too large (max {max_mb:.1f}MB)"

        # Check extension
        ext = Path(filename).suffix.lower()
        if ext not in self.allowed_extensions:
            return False, f"File type not allowed (allowed: {', '.join(self.allowed_extensions)})"

        # Check if it's actually an image (basic check)
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type and not mime_type.startswith(('image/', 'application/octet-stream')):
            if ext not in ['.svg']:  # SVG is text/xml
                return False, "Invalid file type"

        return True, None

    def generate_filename(self, original_filename: str, file_data: bytes) -> str:
        """
        Generate a secure, unique filename.

        Args:
            original_filename: Original filename from upload
            file_data: File content for hash generation

        Returns:
            Secure filename
        """
        # Get extension
        ext = Path(original_filename).suffix.lower()

        # Generate hash from content
        file_hash = hashlib.md5(file_data).hexdigest()[:12]

        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Combine for unique filename
        return f"{timestamp}_{file_hash}{ext}"

    def get_upload_path(self, filename: str) -> Path:
        """
        Get the full upload path based on organization strategy.

        Args:
            filename: Filename to upload

        Returns:
            Full path where file should be saved
        """
        if self.organize_by == "date":
            # Organize by year/month/day
            now = datetime.now()
            subdir = self.upload_dir / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}"
        elif self.organize_by == "hash":
            # Organize by first 2 chars of filename hash
            file_hash = hashlib.md5(filename.encode()).hexdigest()
            subdir = self.upload_dir / file_hash[:2] / file_hash[2:4]
        else:  # flat
            subdir = self.upload_dir

        # Create subdirectory if needed
        subdir.mkdir(parents=True, exist_ok=True)

        return subdir / filename

    def save_file(self, filename: str, file_data: bytes) -> Tuple[bool, str, Optional[str]]:
        """
        Save uploaded file.

        Args:
            filename: Original filename
            file_data: File content as bytes

        Returns:
            Tuple of (success, url_or_error, filepath)
        """
        # Validate file
        is_valid, error = self.validate_file(filename, file_data)
        if not is_valid:
            return False, error, None

        # Generate secure filename
        secure_name = self.generate_filename(filename, file_data)

        # Get upload path
        upload_path = self.get_upload_path(secure_name)

        try:
            # Save file
            with open(upload_path, 'wb') as f:
                f.write(file_data)

            # Generate URL
            relative_path = upload_path.relative_to(self.upload_dir)
            url = f"{self.base_url}/{relative_path.as_posix()}"

            return True, url, str(upload_path)

        except Exception as e:
            return False, f"Failed to save file: {str(e)}", None

    def handle_upload(self, file_field) -> dict:
        """
        Handle file upload from request.

        Args:
            file_field: File field from request (must have .filename and .read())

        Returns:
            Dictionary with 'success', 'url', and optional 'error' keys
        """
        try:
            filename = getattr(file_field, 'filename', 'unknown.jpg')
            file_data = file_field.read()

            success, result, filepath = self.save_file(filename, file_data)

            if success:
                return {
                    'success': True,
                    'url': result,
                    'filepath': filepath
                }
            else:
                return {
                    'success': False,
                    'error': result
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Upload failed: {str(e)}"
            }


def create_upload_route(app, upload_handler: Optional[UploadHandler] = None):
    """
    Create an upload route for the CREATESONLINE app.

    Usage:
        >>> from createsonline import create_app
        >>> from createsonline.upload_handler import create_upload_route, UploadHandler
        >>>
        >>> app = create_app()
        >>>
        >>> # Use default handler
        >>> create_upload_route(app)
        >>>
        >>> # Or custom handler
        >>> handler = UploadHandler(
        ...     upload_dir="media/images",
        ...     max_size=10 * 1024 * 1024,  # 10MB
        ...     organize_by="date"
        ... )
        >>> create_upload_route(app, handler)
    """
    if upload_handler is None:
        upload_handler = UploadHandler()

    @app.post("/api/uploads")
    async def handle_upload(request):
        """Handle file upload from rich text editor."""
        try:
            # Get file from request
            form = await request.form()
            file_field = form.get('file')

            if not file_field:
                return {'success': False, 'error': 'No file provided'}, 400

            # Handle upload
            result = upload_handler.handle_upload(file_field)

            if result['success']:
                return {'url': result['url']}, 200
            else:
                return {'error': result['error']}, 400

        except Exception as e:
            return {'error': f'Upload failed: {str(e)}'}, 500


__all__ = [
    'UploadHandler',
    'create_upload_route',
]