"""
File: waclient/utils.py
Utility functions for WhatsApp Business API
"""

import re
from typing import Optional, Dict


def format_phone_number(phone: str, country_code: str = "91") -> str:
    """
    Format phone number for WhatsApp API
    
    Args:
        phone: Phone number (with or without country code)
        country_code: Default country code if not in phone
        
    Returns:
        Formatted phone number (e.g., 919342585854)
        
    Example:
        >>> format_phone_number("9342585854")
        '919342585854'
        >>> format_phone_number("+91 93425 85854")
        '919342585854'
        >>> format_phone_number("93425-85854", "91")
        '919342585854'
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If doesn't start with country code, add it
    if not digits.startswith(country_code):
        digits = country_code + digits
    
    return digits


def validate_phone_number(phone: str, min_length: int = 10, max_length: int = 15) -> bool:
    """
    Validate if phone number is in correct format
    
    Args:
        phone: Phone number to validate
        min_length: Minimum number of digits (default: 10)
        max_length: Maximum number of digits (default: 15)
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> validate_phone_number("919342585854")
        True
        >>> validate_phone_number("123")
        False
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Should be between min and max digits
    return min_length <= len(digits) <= max_length


def truncate_message(text: str, max_length: int = 4096) -> str:
    """
    Truncate message to WhatsApp's max length
    
    WhatsApp limits:
    - Text messages: 4096 characters
    - Caption for media: 1024 characters
    
    Args:
        text: Message text
        max_length: Maximum allowed length (default: 4096)
        
    Returns:
        Truncated text with ellipsis if needed
        
    Example:
        >>> truncate_message("A" * 5000)
        'AAA...AAA'  # 4096 chars total
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def parse_webhook_payload(payload: dict) -> Optional[Dict]:
    """
    Parse incoming webhook payload to extract message data
    
    Args:
        payload: Raw webhook payload from WhatsApp
        
    Returns:
        Parsed message dict with keys: from, id, timestamp, type, text, etc.
        Returns None if no message found
        
    Example:
        >>> message = parse_webhook_payload(webhook_data)
        >>> if message:
        ...     print(f"From: {message['from']}, Text: {message['text']}")
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
        
        # Extract contact name if available
        contacts = value.get("contacts", [{}])
        contact_name = contacts[0].get("profile", {}).get("name") if contacts else None
        
        return {
            "from": message.get("from"),
            "id": message.get("id"),
            "timestamp": message.get("timestamp"),
            "type": message.get("type"),
            "name": contact_name,
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


def parse_status_update(payload: dict) -> Optional[Dict]:
    """
    Parse message status update from webhook
    
    Args:
        payload: Raw webhook payload
        
    Returns:
        Status dict with keys: id, status, timestamp, recipient_id, errors
        Returns None if no status found
        
    Status values: sent, delivered, read, failed
    
    Example:
        >>> status = parse_status_update(webhook_data)
        >>> if status and status['status'] == 'read':
        ...     print("Message was read!")
    """
    try:
        entry = payload.get("entry", [{}])[0]
        changes = entry.get("changes", [{}])[0]
        value = changes.get("value", {})
        
        statuses = value.get("statuses")
        if not statuses:
            return None
        
        status = statuses[0]
        
        return {
            "id": status.get("id"),
            "status": status.get("status"),
            "timestamp": status.get("timestamp"),
            "recipient_id": status.get("recipient_id"),
            "errors": status.get("errors"),
            "conversation": status.get("conversation"),
            "pricing": status.get("pricing")
        }
    except (KeyError, IndexError, TypeError):
        return None


def extract_button_reply(message: dict) -> Optional[Dict]:
    """
    Extract button reply from interactive message
    
    Args:
        message: Parsed message dict from parse_webhook_payload
        
    Returns:
        Dict with button_id and title, or None
        
    Example:
        >>> button = extract_button_reply(message)
        >>> if button:
        ...     print(f"User clicked: {button['title']}")
    """
    if message.get("type") != "interactive":
        return None
    
    interactive = message.get("interactive", {})
    button_reply = interactive.get("button_reply")
    
    if button_reply:
        return {
            "button_id": button_reply.get("id"),
            "title": button_reply.get("title")
        }
    
    return None


def extract_list_reply(message: dict) -> Optional[Dict]:
    """
    Extract list selection from interactive message
    
    Args:
        message: Parsed message dict from parse_webhook_payload
        
    Returns:
        Dict with list_id, title, and description, or None
        
    Example:
        >>> selection = extract_list_reply(message)
        >>> if selection:
        ...     print(f"User selected: {selection['title']}")
    """
    if message.get("type") != "interactive":
        return None
    
    interactive = message.get("interactive", {})
    list_reply = interactive.get("list_reply")
    
    if list_reply:
        return {
            "list_id": list_reply.get("id"),
            "title": list_reply.get("title"),
            "description": list_reply.get("description")
        }
    
    return None


def sanitize_text(text: str) -> str:
    """
    Sanitize text for WhatsApp (remove unsupported characters)
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text safe for WhatsApp
    """
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid URL
        
    Example:
        >>> is_valid_url("https://example.com")
        True
        >>> is_valid_url("not a url")
        False
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return url_pattern.match(url) is not None


def format_indian_phone(phone: str) -> str:
    """
    Format Indian phone number specifically
    
    Args:
        phone: Indian phone number
        
    Returns:
        Formatted number with +91 prefix
        
    Example:
        >>> format_indian_phone("9342585854")
        '+91 93425 85854'
        >>> format_indian_phone("919342585854")
        '+91 93425 85854'
    """
    digits = re.sub(r'\D', '', phone)
    
    # Remove 91 if present
    if digits.startswith('91') and len(digits) == 12:
        digits = digits[2:]
    
    # Format: +91 XXXXX XXXXX
    if len(digits) == 10:
        return f"+91 {digits[:5]} {digits[5:]}"
    
    return phone


def get_media_type_from_mime(mime_type: str) -> Optional[str]:
    """
    Get WhatsApp media type from MIME type
    
    Args:
        mime_type: MIME type string
        
    Returns:
        'image', 'video', 'audio', 'document', or None
        
    Example:
        >>> get_media_type_from_mime("image/jpeg")
        'image'
        >>> get_media_type_from_mime("application/pdf")
        'document'
    """
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type.startswith('application/') or mime_type.startswith('text/'):
        return 'document'
    
    return None


def chunk_text(text: str, chunk_size: int = 4096) -> list:
    """
    Split long text into chunks for multiple messages
    
    Args:
        text: Long text to split
        chunk_size: Maximum size per chunk
        
    Returns:
        List of text chunks
        
    Example:
        >>> long_text = "A" * 10000
        >>> chunks = chunk_text(long_text, 4096)
        >>> len(chunks)
        3
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences to avoid breaking mid-sentence
    sentences = re.split(r'([.!?]\s+)', text)
    
    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
        full_sentence = sentence + delimiter
        
        if len(current_chunk) + len(full_sentence) <= chunk_size:
            current_chunk += full_sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = full_sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def create_quick_reply_buttons(options: list, max_buttons: int = 3) -> list:
    """
    Create quick reply buttons from list of options
    
    Args:
        options: List of button texts (strings or dicts with id and title)
        max_buttons: Maximum buttons (WhatsApp limit is 3)
        
    Returns:
        List of button dicts ready for send_interactive
        
    Example:
        >>> buttons = create_quick_reply_buttons(["Yes", "No", "Maybe"])
        >>> # Returns: [{'id': 'yes', 'title': 'Yes'}, ...]
    """
    buttons = []
    
    for i, option in enumerate(options[:max_buttons]):
        if isinstance(option, dict):
            buttons.append(option)
        else:
            # Auto-generate ID from title
            button_id = re.sub(r'[^a-z0-9_]', '', option.lower().replace(' ', '_'))
            buttons.append({
                'id': button_id or f'btn_{i}',
                'title': str(option)[:20]  # WhatsApp limit: 20 chars
            })
    
    return buttons
