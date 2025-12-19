"""
File: waclient/client.py
Main WhatsApp Business Cloud API Client
"""

import requests
import json
from typing import Optional, Dict, List, Any
from .exceptions import WhatsAppError, AuthenticationError, MessageError
from .messages import MessageBuilder
from .media import MediaHandler


class WhatsAppClient:
    """
    WhatsApp Business Cloud API Client
    
    Example:
        client = WhatsAppClient(
            phone_number_id="YOUR_PHONE_ID",
            access_token="YOUR_ACCESS_TOKEN"
        )
        client.send_text("919342585854", "Hello!")
    """
    
    BASE_URL = "https://graph.facebook.com/v21.0"
    
    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        api_version: str = "v21.0"
    ):
        """
        Initialize WhatsApp Client
        
        Args:
            phone_number_id: Your WhatsApp Business phone number ID
            access_token: Your WhatsApp Business API access token
            api_version: API version (default: v21.0)
        """
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.message_builder = MessageBuilder()
        self.media_handler = MediaHandler(self)
        
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict:
        """Make HTTP request to WhatsApp API"""
        url = f"{self.base_url}/{self.phone_number_id}/{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code >= 400:
                error_msg = response_data.get("error", {}).get("message", "Unknown error")
                error_code = response_data.get("error", {}).get("code", 0)
                
                if response.status_code == 401:
                    raise AuthenticationError(f"Authentication failed: {error_msg}")
                else:
                    raise MessageError(f"API Error ({error_code}): {error_msg}")
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            raise WhatsAppError(f"Request failed: {str(e)}")
    
    def send_text(
        self,
        to: str,
        message: str,
        preview_url: bool = False
    ) -> Dict:
        """
        Send a text message
        
        Args:
            to: Recipient phone number (with country code, no + sign)
            message: Text message to send
            preview_url: Enable URL preview
            
        Returns:
            API response with message ID
            
        Example:
            response = client.send_text("919342585854", "Hello World!")
        """
        payload = self.message_builder.text_message(to, message, preview_url)
        return self._make_request("POST", "messages", data=payload)
    
    def send_template(
        self,
        to: str,
        template_name: str,
        language: str = "en",
        components: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict:
        """
        Send a template message
        
        Args:
            to: Recipient phone number
            template_name: Approved template name
            language: Template language code (default: en)
            components: Template components (parameters, buttons, etc.)
            **kwargs: Additional template parameters
            
        Returns:
            API response with message ID
            
        Example:
            client.send_template(
                to="919342585854",
                template_name="order_confirmation",
                language="en",
                components=[{
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": "Order123"},
                        {"type": "text", "text": "₹499"}
                    ]
                }]
            )
        """
        payload = self.message_builder.template_message(
            to, template_name, language, components
        )
        return self._make_request("POST", "messages", data=payload)
    
    def send_image(
        self,
        to: str,
        image_url: Optional[str] = None,
        image_id: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict:
        """
        Send an image message
        
        Args:
            to: Recipient phone number
            image_url: Public URL of the image (or use image_id)
            image_id: Media ID from uploaded image
            caption: Optional image caption
            
        Returns:
            API response with message ID
        """
        payload = self.message_builder.media_message(
            to, "image", image_url, image_id, caption
        )
        return self._make_request("POST", "messages", data=payload)
    
    def send_document(
        self,
        to: str,
        document_url: Optional[str] = None,
        document_id: Optional[str] = None,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict:
        """Send a document (PDF, DOC, etc.)"""
        payload = self.message_builder.media_message(
            to, "document", document_url, document_id, caption, filename
        )
        return self._make_request("POST", "messages", data=payload)
    
    def send_video(
        self,
        to: str,
        video_url: Optional[str] = None,
        video_id: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict:
        """Send a video message"""
        payload = self.message_builder.media_message(
            to, "video", video_url, video_id, caption
        )
        return self._make_request("POST", "messages", data=payload)
    
    def send_audio(
        self,
        to: str,
        audio_url: Optional[str] = None,
        audio_id: Optional[str] = None
    ) -> Dict:
        """Send an audio message"""
        payload = self.message_builder.media_message(
            to, "audio", audio_url, audio_id
        )
        return self._make_request("POST", "messages", data=payload)
    
    def send_location(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None
    ) -> Dict:
        """Send a location message"""
        payload = self.message_builder.location_message(
            to, latitude, longitude, name, address
        )
        return self._make_request("POST", "messages", data=payload)
    
    def send_contacts(
        self,
        to: str,
        contacts: List[Dict]
    ) -> Dict:
        """Send contact card(s)"""
        payload = self.message_builder.contacts_message(to, contacts)
        return self._make_request("POST", "messages", data=payload)
    
    def send_interactive(
        self,
        to: str,
        interactive_type: str,
        body_text: str,
        **kwargs
    ) -> Dict:
        """
        Send interactive message (buttons, lists)
        
        Args:
            to: Recipient phone number
            interactive_type: 'button' or 'list'
            body_text: Message body text
            **kwargs: Additional parameters (buttons, sections, etc.)
        """
        payload = self.message_builder.interactive_message(
            to, interactive_type, body_text, **kwargs
        )
        return self._make_request("POST", "messages", data=payload)
    
    def mark_as_read(self, message_id: str) -> Dict:
        """Mark a message as read"""
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        return self._make_request("POST", "messages", data=payload)
    
    def upload_media(self, file_path: str, mime_type: str) -> str:
        """
        Upload media file and get media ID
        
        Args:
            file_path: Path to the media file
            mime_type: MIME type (e.g., 'image/jpeg', 'application/pdf')
            
        Returns:
            Media ID to use in send methods
        """
        return self.media_handler.upload(file_path, mime_type)
    
    def get_media_url(self, media_id: str) -> str:
        """Get download URL for a media ID"""
        return self.media_handler.get_url(media_id)
