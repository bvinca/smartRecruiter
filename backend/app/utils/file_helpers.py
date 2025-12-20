"""
Temporary file handling utilities
"""
import os
import uuid
import tempfile
from typing import Optional
from pathlib import Path


class FileHelper:
    """Helper class for managing temporary files"""
    
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def save_uploaded_file(
        self,
        file_content: bytes,
        filename: str,
        prefix: Optional[str] = None
    ) -> str:
        """
        Save uploaded file to disk
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            prefix: Optional prefix for the saved file
        
        Returns:
            Path to saved file
        """
        file_ext = Path(filename).suffix or '.pdf'
        file_id = str(uuid.uuid4())
        
        if prefix:
            saved_filename = f"{prefix}_{file_id}{file_ext}"
        else:
            saved_filename = f"{file_id}{file_ext}"
        
        file_path = os.path.join(self.base_dir, saved_filename)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return file_path
    
    def create_temp_file(self, content: bytes, suffix: str = ".tmp") -> str:
        """
        Create a temporary file
        
        Args:
            content: File content
            suffix: File suffix
        
        Returns:
            Path to temporary file
        """
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            dir=self.base_dir
        )
        temp_file.write(content)
        temp_file.close()
        
        return temp_file.name
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path: Path to file to delete
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {file_path}: {e}")
            return False
    
    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0
    
    def validate_file_type(self, filename: str, allowed_types: list = None) -> bool:
        """
        Validate file type
        
        Args:
            filename: Name of the file
            allowed_types: List of allowed file extensions (default: pdf, docx, txt)
        
        Returns:
            True if file type is allowed
        """
        if allowed_types is None:
            allowed_types = ['.pdf', '.docx', '.doc', '.txt']
        
        file_ext = Path(filename).suffix.lower()
        return file_ext in allowed_types
    
    def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """
        Clean up old files in upload directory
        
        Args:
            max_age_days: Maximum age of files in days
        
        Returns:
            Number of files deleted
        """
        import time
        deleted_count = 0
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        for filename in os.listdir(self.base_dir):
            file_path = os.path.join(self.base_dir, filename)
            try:
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    if self.delete_file(file_path):
                        deleted_count += 1
            except Exception as e:
                print(f"Error checking file {file_path}: {e}")
        
        return deleted_count

