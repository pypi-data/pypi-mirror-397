"""
File: waclient/messages.py
Message payload builders for different message types
"""

from typing import Optional, Dict, List, Any


class MessageBuilder:
    """Build WhatsApp message payloads"""
    
    def text_message(
        self,
        to: str,
        text: str,
        preview_url: bool = False
    ) -> Dict:
        """Build text message payload"""
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "preview_url": preview_url,
                "body": text
            }
        }
    
    def template_message(
        self,
        to: str,
        template_name: str,
        language: str = "en",
        components: Optional[List[Dict]] = None
    ) -> Dict:
        """Build template message payload"""
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
            
        return payload
    
    def media_message(
        self,
        to: str,
        media_type: str,
        url: Optional[str] = None,
        media_id: Optional[str] = None,
        caption: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict:
        """Build media message payload (image, video, audio, document)"""
        
        if not url and not media_id:
            raise ValueError("Either url or media_id must be provided")
        
        media_obj = {}
        
        if media_id:
            media_obj["id"] = media_id
        else:
            media_obj["link"] = url
        
        if caption and media_type in ["image", "video", "document"]:
            media_obj["caption"] = caption
        
        if filename and media_type == "document":
            media_obj["filename"] = filename
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": media_type,
            media_type: media_obj
        }
    
    def location_message(
        self,
        to: str,
        latitude: float,
        longitude: float,
        name: Optional[str] = None,
        address: Optional[str] = None
    ) -> Dict:
        """Build location message payload"""
        location_obj = {
            "latitude": latitude,
            "longitude": longitude
        }
        
        if name:
            location_obj["name"] = name
        if address:
            location_obj["address"] = address
        
        return {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "location",
            "location": location_obj
        }
    
    def contacts_message(
        self,
        to: str,
        contacts: List[Dict]
    ) -> Dict:
        """Build contacts message payload"""
        return {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "contacts",
            "contacts": contacts
        }
    
    def interactive_message(
        self,
        to: str,
        interactive_type: str,
        body_text: str,
        **kwargs
    ) -> Dict:
        """
        Build interactive message payload (buttons or list)
        
        For buttons:
            kwargs should include:
            - buttons: List of button dicts with 'id' and 'title'
            - header (optional): Header text
            - footer (optional): Footer text
        
        For list:
            kwargs should include:
            - button_text: Text on the list button
            - sections: List of section dicts
        """
        interactive_obj = {
            "type": interactive_type,
            "body": {"text": body_text}
        }
        
        # Add header if provided
        if "header" in kwargs:
            interactive_obj["header"] = {"type": "text", "text": kwargs["header"]}
        
        # Add footer if provided
        if "footer" in kwargs:
            interactive_obj["footer"] = {"text": kwargs["footer"]}
        
        # Build action based on type
        if interactive_type == "button":
            buttons = kwargs.get("buttons", [])
            interactive_obj["action"] = {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": btn.get("id", f"btn_{i}"),
                            "title": btn.get("title", f"Button {i+1}")
                        }
                    }
                    for i, btn in enumerate(buttons[:3])  # Max 3 buttons
                ]
            }
        
        elif interactive_type == "list":
            interactive_obj["action"] = {
                "button": kwargs.get("button_text", "View Options"),
                "sections": kwargs.get("sections", [])
            }
        
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "interactive",
            "interactive": interactive_obj
        }


class TemplateBuilder:
    """Helper to build template message components easily"""
    
    @staticmethod
    def body_parameters(*values: str) -> Dict:
        """Create body parameters for template"""
        return {
            "type": "body",
            "parameters": [
                {"type": "text", "text": str(val)}
                for val in values
            ]
        }
    
    @staticmethod
    def header_text(text: str) -> Dict:
        """Create header text parameter"""
        return {
            "type": "header",
            "parameters": [
                {"type": "text", "text": text}
            ]
        }
    
    @staticmethod
    def header_image(image_url: str , image_id: str) -> Dict:
        """Create header image parameter"""
        image_obj = {}
        if image_id:
            image_obj["id"] = image_id
        else:
            image_obj["link"] = image_url
        
        return {
            "type": "header",
            "parameters": [
                {"type": "image", "image": image_obj}
            ]
        }
    
    @staticmethod
    def button_url(index: int, url_suffix: str) -> Dict:
        """Create button URL parameter"""
        return {
            "type": "button",
            "sub_type": "url",
            "index": index,
            "parameters": [
                {"type": "text", "text": url_suffix}
            ]
        }
