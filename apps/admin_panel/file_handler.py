"""
File upload handler for the Helpdesk application
Handles file uploads with validation based on admin settings
"""
import os
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import SystemSettings


class FileUploadHandler:
    """Handles file uploads with validation"""

    def __init__(self):
        self.settings = SystemSettings.get_settings()

    def validate_file(self, file_obj):
        """
        Validate uploaded file based on admin settings
        Returns: (is_valid, error_message)
        """
        if not file_obj:
            return False, "No file provided"

        # Get file extension
        file_name = file_obj.name
        file_ext = os.path.splitext(file_name)[1].lstrip('.').lower()

        # Check file size
        max_size = self.settings.max_upload_size_mb * 1024 * 1024
        if file_obj.size > max_size:
            return False, f"File size exceeds {self.settings.max_upload_size_mb}MB limit"

        # Check file extension
        allowed_types = self.settings.get_allowed_extensions()
        if file_ext not in allowed_types:
            return False, f"File type '.{file_ext}' is not allowed. Allowed types: {', '.join(allowed_types)}"

        # Additional validation for specific file types
        if file_ext in ['jpg', 'jpeg', 'png', 'gif']:
            return self._validate_image(file_obj, file_ext)
        elif file_ext == 'pdf':
            return self._validate_pdf(file_obj)

        return True, None

    def _validate_image(self, file_obj, ext):
        """Validate image file"""
        try:
            from PIL import Image

            # Check if file is a valid image
            img = Image.open(file_obj)
            img.verify()

            # Reset file pointer
            file_obj.seek(0)

            return True, None
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"

    def _validate_pdf(self, file_obj):
        """Validate PDF file"""
        try:
            # Check PDF magic bytes
            file_obj.seek(0)
            header = file_obj.read(4)
            file_obj.seek(0)

            if header != b'%PDF':
                return False, "Invalid PDF file"

            return True, None
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"

    @staticmethod
    def get_upload_path(file_type):
        """Get upload directory path for file type"""
        paths = {
            'ticket_attachment': 'tickets/attachments/',
            'logo': 'logos/',
            'user_avatar': 'users/avatars/',
            'knowledge_attachment': 'knowledge/attachments/',
        }
        return paths.get(file_type, 'uploads/')

    @staticmethod
    def format_file_size(size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f}TB"


class LogoUploadHandler:
    """Specialized handler for logo uploads"""

    MAX_LOGO_SIZE = 2 * 1024 * 1024  # 2MB
    ALLOWED_FORMATS = ['image/png', 'image/jpeg', 'image/gif', 'image/webp']

    @classmethod
    def validate_logo(cls, file_obj):
        """Validate logo file"""
        if not file_obj:
            return False, "No file provided"

        # Check file size
        if file_obj.size > cls.MAX_LOGO_SIZE:
            return False, f"Logo file too large. Maximum size: 2MB"

        # Check MIME type
        if file_obj.content_type not in cls.ALLOWED_FORMATS:
            return False, f"Invalid logo format. Allowed: PNG, JPEG, GIF"

        # Validate as image
        try:
            from PIL import Image
            img = Image.open(file_obj)
            img.verify()
            file_obj.seek(0)
            return True, None
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
