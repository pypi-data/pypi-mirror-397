"""
File: waclient/webhooks.py
Webhook verification and handling
"""

import hmac
import hashlib
from typing import Optional, Dict, Callable
from .exceptions import WebhookError


class WebhookHandler:
    """Handle WhatsApp webhook verification and message processing"""
    
    def __init__(self, app_secret: str, verify_token: str):
        """
        Initialize webhook handler
        
        Args:
            app_secret: Your Facebook App Secret
            verify_token: Your custom verification token
        """
        self.app_secret = app_secret
        self.verify_token = verify_token
    
    def verify_signature(self, signature: str, payload: bytes) -> bool:
        """
        Verify webhook signature
        
        Args:
            signature: X-Hub-Signature-256 header value
            payload: Raw request body (bytes)
            
        Returns:
            True if signature is valid
            
        Raises:
            WebhookError: If signature is invalid
        """
        if not signature:
            raise WebhookError("Missing signature header")
        
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
        
        # Calculate expected signature
        expected = hmac.new(
            self.app_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        if not hmac.compare_digest(signature, expected):
            raise WebhookError("Invalid signature")
        
        return True
    
    def verify_token(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook setup token (for initial webhook setup)
        
        Args:
            mode: hub.mode parameter
            token: hub.verify_token parameter
            challenge: hub.challenge parameter
            
        Returns:
            Challenge string if verification succeeds, None otherwise
        """
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
    
    def parse_message(self, payload: Dict) -> Optional[Dict]:
        """
        Parse incoming webhook message
        
        Args:
            payload: Webhook JSON payload
            
        Returns:
            Parsed message dict or None
        """
        try:
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            
            # Check if it's a message
            messages = value.get("messages")
            if not messages:
                return None
            
            message = messages[0]
            message_type = message.get("type")
            
            # Base message info
            result = {
                "from": message.get("from"),
                "id": message.get("id"),
                "timestamp": message.get("timestamp"),
                "type": message_type,
                "name": value.get("contacts", [{}])[0].get("profile", {}).get("name")
            }
            
            # Parse based on message type
            if message_type == "text":
                result["text"] = message.get("text", {}).get("body")
            
            elif message_type == "image":
                result["image"] = message.get("image")
            
            elif message_type == "video":
                result["video"] = message.get("video")
            
            elif message_type == "audio":
                result["audio"] = message.get("audio")
            
            elif message_type == "document":
                result["document"] = message.get("document")
            
            elif message_type == "location":
                result["location"] = message.get("location")
            
            elif message_type == "contacts":
                result["contacts"] = message.get("contacts")
            
            elif message_type == "button":
                result["button"] = message.get("button")
            
            elif message_type == "interactive":
                interactive = message.get("interactive", {})
                result["interactive"] = {
                    "type": interactive.get("type"),
                    "button_reply": interactive.get("button_reply"),
                    "list_reply": interactive.get("list_reply")
                }
            
            return result
            
        except (KeyError, IndexError, TypeError) as e:
            raise WebhookError(f"Failed to parse message: {str(e)}")
    
    def parse_status(self, payload: Dict) -> Optional[Dict]:
        """
        Parse message status update
        
        Args:
            payload: Webhook JSON payload
            
        Returns:
            Status dict or None
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
                "status": status.get("status"),  # sent, delivered, read, failed
                "timestamp": status.get("timestamp"),
                "recipient_id": status.get("recipient_id"),
                "errors": status.get("errors"),
                "conversation": status.get("conversation"),
                "pricing": status.get("pricing")
            }
            
        except (KeyError, IndexError, TypeError):
            return None
