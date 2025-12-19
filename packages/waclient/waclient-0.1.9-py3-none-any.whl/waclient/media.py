"""
File: waclient/media.py
Media upload, download, and handling for WhatsApp Business API
"""

import requests
from pathlib import Path
from typing import Optional, Dict
from .exceptions import MediaError


class MediaHandler:
    """
    Handle media uploads and downloads for WhatsApp Business API
    
    Supports:
    - Images (JPEG, PNG)
    - Videos (MP4, 3GP)
    - Audio (AAC, MP3, AMR, OGG)
    - Documents (PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX)
    """
    
    # Supported media types and their MIME types
    SUPPORTED_TYPES = {
        'image': ['image/jpeg', 'image/png'],
        'video': ['video/mp4', 'video/3gpp'],
        'audio': ['audio/aac', 'audio/mp4', 'audio/mpeg', 'audio/amr', 'audio/ogg'],
        'document': [
            'application/pdf',
            'application/vnd.ms-powerpoint',
            'application/msword',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'text/plain'
        ]
    }
    
    # Maximum file sizes (in MB)
    MAX_SIZES = {
        'image': 5,      # 5 MB
        'video': 16,     # 16 MB
        'audio': 16,     # 16 MB
        'document': 100  # 100 MB
    }
    
    def __init__(self, client):
        """
        Initialize MediaHandler
        
        Args:
            client: WhatsAppClient instance
        """
        self.client = client
    
    def upload(self, file_path: str, mime_type: str) -> str:
        """
        Upload a media file to WhatsApp servers
        
        Args:
            file_path: Path to the media file
            mime_type: MIME type (e.g., 'image/jpeg', 'application/pdf')
            
        Returns:
            Media ID that can be used to send the media
            
        Raises:
            MediaError: If upload fails or file is invalid
            
        Example:
            media_id = handler.upload('invoice.pdf', 'application/pdf')
            client.send_document(to="...", document_id=media_id)
        """
        # Validate file exists
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise MediaError(f"File not found: {file_path}")
        
        if not file_path_obj.is_file():
            raise MediaError(f"Not a file: {file_path}")
        
        # Validate MIME type
        if not self._is_mime_type_supported(mime_type):
            raise MediaError(f"Unsupported MIME type: {mime_type}")
        
        # Validate file size
        file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
        media_type = self._get_media_type(mime_type)
        max_size = self.MAX_SIZES.get(media_type, 100)
        
        if file_size_mb > max_size:
            raise MediaError(
                f"File too large: {file_size_mb:.2f}MB "
                f"(max {max_size}MB for {media_type})"
            )
        
        # Prepare upload
        url = f"{self.client.base_url}/{self.client.phone_number_id}/media"
        file_name = file_path_obj.name
        
        try:
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_name, f, mime_type)
                }
                data = {
                    'messaging_product': 'whatsapp'
                }
                headers = {
                    'Authorization': f'Bearer {self.client.access_token}'
                }
                
                response = requests.post(
                    url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=120  # Increased timeout for large files
                )
                
                response.raise_for_status()
                
                result = response.json()
                media_id = result.get('id')
                
                if not media_id:
                    raise MediaError("Upload succeeded but no media ID returned")
                
                return media_id
                
        except requests.exceptions.Timeout:
            raise MediaError("Upload timed out - file may be too large")
        except requests.exceptions.RequestException as e:
            # Fixed: Check if response exists and is not None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error = e.response.json().get('error', {})
                    error_msg = error.get('message', str(e))
                    raise MediaError(f"Upload failed: {error_msg}")
                except (ValueError, AttributeError):
                    pass
            raise MediaError(f"Upload failed: {str(e)}")
        except Exception as e:
            raise MediaError(f"Upload failed: {str(e)}")
    
    def get_url(self, media_id: str) -> str:
        """
        Get the download URL for a media ID
        
        Args:
            media_id: Media ID from WhatsApp (from upload or incoming message)
            
        Returns:
            Download URL (valid for a limited time)
            
        Raises:
            MediaError: If retrieval fails
            
        Example:
            url = handler.get_url(media_id)
            handler.download(url, 'downloaded_image.jpg')
        """
        url = f"{self.client.base_url}/{media_id}"
        
        try:
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {self.client.access_token}'},
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            media_url = result.get('url')
            
            if not media_url:
                raise MediaError("No URL in response")
            
            return media_url
            
        except requests.exceptions.RequestException as e:
            # Fixed: Check if response exists and is not None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error = e.response.json().get('error', {})
                    error_msg = error.get('message', str(e))
                    raise MediaError(f"Failed to get media URL: {error_msg}")
                except (ValueError, AttributeError):
                    pass
            raise MediaError(f"Failed to get media URL: {str(e)}")
    
    def download(self, media_url: str, save_path: str) -> str:
        """
        Download media from WhatsApp URL
        
        Args:
            media_url: URL from get_url() method
            save_path: Local path where file should be saved
            
        Returns:
            Path to the saved file
            
        Raises:
            MediaError: If download fails
            
        Example:
            # Download image from incoming message
            media_url = handler.get_url(message['image']['id'])
            handler.download(media_url, 'received_image.jpg')
        """
        try:
            response = requests.get(
                media_url,
                headers={'Authorization': f'Bearer {self.client.access_token}'},
                timeout=120,
                stream=True
            )
            
            response.raise_for_status()
            
            # Create directory if it doesn't exist
            save_path_obj = Path(save_path)
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Download in chunks
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            return save_path
            
        except requests.exceptions.RequestException as e:
            raise MediaError(f"Download failed: {str(e)}")
        except IOError as e:
            raise MediaError(f"Failed to save file: {str(e)}")
    
    def delete(self, media_id: str) -> bool:
        """
        Delete a media file from WhatsApp servers
        
        Args:
            media_id: Media ID to delete
            
        Returns:
            True if deletion was successful
            
        Raises:
            MediaError: If deletion fails
        """
        url = f"{self.client.base_url}/{media_id}"
        
        try:
            response = requests.delete(
                url,
                headers={'Authorization': f'Bearer {self.client.access_token}'},
                timeout=30
            )
            
            response.raise_for_status()
            
            result = response.json()
            return result.get('success', False)
            
        except requests.exceptions.RequestException as e:
            # Fixed: Check if response exists and is not None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error = e.response.json().get('error', {})
                    error_msg = error.get('message', str(e))
                    raise MediaError(f"Failed to delete media: {error_msg}")
                except (ValueError, AttributeError):
                    pass
            raise MediaError(f"Failed to delete media: {str(e)}")
    
    def get_info(self, media_id: str) -> Dict:
        """
        Get information about a media file
        
        Args:
            media_id: Media ID
            
        Returns:
            Dict with media information (url, mime_type, sha256, file_size)
            
        Raises:
            MediaError: If retrieval fails
        """
        url = f"{self.client.base_url}/{media_id}"
        
        try:
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {self.client.access_token}'},
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise MediaError(f"Failed to get media info: {str(e)}")
    
    def _is_mime_type_supported(self, mime_type: str) -> bool:
        """Check if MIME type is supported"""
        for media_types in self.SUPPORTED_TYPES.values():
            if mime_type in media_types:
                return True
        return False
    
    def _get_media_type(self, mime_type: str) -> Optional[str]:
        """Get media type category from MIME type"""
        for media_type, mime_types in self.SUPPORTED_TYPES.items():
            if mime_type in mime_types:
                return media_type
        return None
    
    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """
        Guess MIME type from file extension
        
        Args:
            file_path: Path to file
            
        Returns:
            MIME type string
            
        Example:
            mime_type = MediaHandler.get_mime_type('document.pdf')
            # Returns: 'application/pdf'
        """
        import mimetypes
        
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type:
            return mime_type
        
        # Fallback for common extensions
        ext_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.mp4': 'video/mp4',
            '.3gp': 'video/3gpp',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.txt': 'text/plain',
            '.mp3': 'audio/mpeg',
            '.ogg': 'audio/ogg',
            '.aac': 'audio/aac',
            '.amr': 'audio/amr'
        }
        
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, 'application/octet-stream')


# ============================================
# Utility Functions for Media Handling
# ============================================

def upload_media_from_url(client, media_url: str, save_temp: bool = False) -> str:
    """
    Download media from external URL and upload to WhatsApp
    
    Args:
        client: WhatsAppClient instance
        media_url: External URL to download from
        save_temp: Whether to keep temporary file after upload
        
    Returns:
        Media ID
        
    Example:
        from waclient.media import upload_media_from_url
        
        media_id = upload_media_from_url(
            client,
            "https://example.com/image.jpg"
        )
        client.send_image("919876543210", image_id=media_id)
    """
    import tempfile
    import os
    
    try:
        # Download from URL
        response = requests.get(media_url, timeout=60, stream=True)
        response.raise_for_status()
        
        # Get content type
        mime_type = response.headers.get('content-type', 'application/octet-stream')
        
        # Get file extension
        from urllib.parse import urlparse
        parsed = urlparse(media_url)
        ext = Path(parsed.path).suffix or '.tmp'
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                tmp_file.write(chunk)
            tmp_path = tmp_file.name
        
        # Upload to WhatsApp
        handler = MediaHandler(client)
        media_id = handler.upload(tmp_path, mime_type)
        
        # Clean up temp file
        if not save_temp:
            os.unlink(tmp_path)
        
        return media_id
        
    except Exception as e:
        raise MediaError(f"Failed to upload from URL: {str(e)}")


def validate_media_file(file_path: str, media_type: str = None) -> Dict:
    """
    Validate media file before upload
    
    Args:
        file_path: Path to file
        media_type: Expected media type (image, video, audio, document)
        
    Returns:
        Dict with validation results:
        {
            'valid': bool,
            'errors': list,
            'mime_type': str,
            'file_size_mb': float,
            'media_type': str
        }
        
    Example:
        from waclient.media import validate_media_file
        
        result = validate_media_file('photo.jpg', 'image')
        if result['valid']:
            media_id = handler.upload(file_path, result['mime_type'])
        else:
            print(f"Invalid file: {result['errors']}")
    """
    file_path_obj = Path(file_path)
    
    result = {
        'valid': False,
        'errors': [],
        'mime_type': None,
        'file_size_mb': 0,
        'media_type': None
    }
    
    # Check file exists
    if not file_path_obj.exists():
        result['errors'].append("File does not exist")
        return result
    
    # Get MIME type
    mime_type = MediaHandler.get_mime_type(file_path)
    result['mime_type'] = mime_type
    
    # Get file size
    file_size_mb = file_path_obj.stat().st_size / (1024 * 1024)
    result['file_size_mb'] = round(file_size_mb, 2)
    
    # Determine media type
    handler = MediaHandler(None)
    detected_type = handler._get_media_type(mime_type)
    result['media_type'] = detected_type
    
    # Check if supported
    if not detected_type:
        result['errors'].append(f"Unsupported MIME type: {mime_type}")
        return result
    
    # Check media type matches expected
    if media_type and detected_type != media_type:
        result['errors'].append(
            f"Expected {media_type} but file is {detected_type}"
        )
        return result
    
    # Check file size
    max_size = MediaHandler.MAX_SIZES.get(detected_type, 100)
    if file_size_mb > max_size:
        result['errors'].append(
            f"File too large: {file_size_mb:.2f}MB (max {max_size}MB)"
        )
        return result
    
    # All checks passed
    result['valid'] = True
    return result


def batch_upload_media(client, file_paths: list) -> Dict[str, str]:
    """
    Upload multiple media files at once
    
    Args:
        client: WhatsAppClient instance
        file_paths: List of file paths to upload
        
    Returns:
        Dict mapping file paths to media IDs
        
    Example:
        from waclient.media import batch_upload_media
        
        files = ['image1.jpg', 'image2.jpg', 'doc.pdf']
        media_ids = batch_upload_media(client, files)
        
        for file_path, media_id in media_ids.items():
            print(f"{file_path} -> {media_id}")
    """
    handler = MediaHandler(client)
    results = {}
    
    for file_path in file_paths:
        try:
            mime_type = MediaHandler.get_mime_type(file_path)
            media_id = handler.upload(file_path, mime_type)
            results[file_path] = media_id
        except MediaError as e:
            results[file_path] = f"ERROR: {str(e)}"
    
    return results
