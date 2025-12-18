"""
File: waclient/exceptions.py
Custom exceptions for WhatsApp Business API
"""


class WhatsAppError(Exception):
    """Base exception for WhatsApp Business API errors"""
    pass


class AuthenticationError(WhatsAppError):
    """Raised when authentication fails"""
    pass


class MessageError(WhatsAppError):
    """Raised when message sending fails"""
    pass


class MediaError(WhatsAppError):
    """Raised when media upload/download fails"""
    pass


class WebhookError(WhatsAppError):
    """Raised when webhook verification fails"""
    pass


class ValidationError(WhatsAppError):
    """Raised when input validation fails"""
    pass


# ============================================
# File: waclient/utils.py
# Utility functions
# ============================================

import re
from typing import Optional


def format_phone_number(phone: str, country_code: str = "91") -> str:
    """
    Format phone number for WhatsApp API
    
    Args:
        phone: Phone number (with or without country code)
        country_code: Default country code if not in phone
        
    Returns:
        Formatted phone number (e.g., 919876543210)
        
    Example:
        format_phone_number("9876543210")  # Returns: 919876543210
        format_phone_number("+91 98765 43210")  # Returns: 919876543210
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If doesn't start with country code, add it
    if not digits.startswith(country_code):
        digits = country_code + digits
    
    return digits


def validate_phone_number(phone: str) -> bool:
    """
    Validate if phone number is in correct format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Should be between 10-15 digits
    return 10 <= len(digits) <= 15


def truncate_message(text: str, max_length: int = 4096) -> str:
    """
    Truncate message to WhatsApp's max length
    
    Args:
        text: Message text
        max_length: Maximum allowed length (default: 4096)
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def parse_webhook_payload(payload: dict) -> Optional[dict]:
    """
    Parse incoming webhook payload
    
    Args:
        payload: Raw webhook payload from WhatsApp
        
    Returns:
        Parsed message data or None
    """
    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        # Get messages
        messages = value.get("messages", [])
        if not messages:
            return None
        
        message = messages[0]
        
        return {
            "from": message.get("from"),
            "id": message.get("id"),
            "timestamp": message.get("timestamp"),
            "type": message.get("type"),
            "text": message.get("text", {}).get("body"),
            "image": message.get("image"),
            "video": message.get("video"),
            "document": message.get("document"),
            "audio": message.get("audio"),
            "location": message.get("location"),
            "contacts": message.get("contacts"),
            "button": message.get("button"),
            "interactive": message.get("interactive")
        }
    except (KeyError, IndexError, TypeError):
        return None


# ============================================
# File: waclient/media.py
# Media handling
# ============================================

import requests
from pathlib import Path
from .exceptions import MediaError


class MediaHandler:
    """Handle media uploads and downloads"""
    
    def __init__(self, client):
        self.client = client
    
    def upload(self, file_path: str, mime_type: str) -> str:
        """
        Upload a media file
        
        Args:
            file_path: Path to the file
            mime_type: MIME type (e.g., 'image/jpeg')
            
        Returns:
            Media ID
        """
        url = f"{self.client.base_url}/{self.client.phone_number_id}/media"
        
        file_name = Path(file_path).name
        
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
                    timeout=60
                )
                
                if response.status_code != 200:
                    error = response.json().get('error', {})
                    raise MediaError(f"Upload failed: {error.get('message', 'Unknown error')}")
                
                return response.json().get('id')
                
        except FileNotFoundError:
            raise MediaError(f"File not found: {file_path}")
        except Exception as e:
            raise MediaError(f"Upload failed: {str(e)}")
    
    def get_url(self, media_id: str) -> str:
        """
        Get download URL for a media ID
        
        Args:
            media_id: Media ID from WhatsApp
            
        Returns:
            Download URL
        """
        url = f"{self.client.base_url}/{media_id}"
        
        try:
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {self.client.access_token}'},
                timeout=30
            )
            
            if response.status_code != 200:
                raise MediaError("Failed to get media URL")
            
            return response.json().get('url')
            
        except Exception as e:
            raise MediaError(f"Failed to get media URL: {str(e)}")
    
    def download(self, media_url: str, save_path: str) -> str:
        """
        Download media from WhatsApp URL
        
        Args:
            media_url: URL from get_url()
            save_path: Where to save the file
            
        Returns:
            Path to saved file
        """
        try:
            response = requests.get(
                media_url,
                headers={'Authorization': f'Bearer {self.client.access_token}'},
                timeout=60,
                stream=True
            )
            
            if response.status_code != 200:
                raise MediaError("Failed to download media")
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return save_path
            
        except Exception as e:
            raise MediaError(f"Download failed: {str(e)}")
