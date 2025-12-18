"""
File: waclient/templates.py
Template message builders and utilities for WhatsApp Business API
"""

from typing import List, Dict, Optional, Union


class TemplateBuilder:
    """
    Helper class to build template message components easily
    
    WhatsApp templates have three main parts:
    1. Header (optional): Text, image, video, or document
    2. Body: Main message with parameters
    3. Buttons (optional): Call-to-action or quick reply buttons
    """
    
    @staticmethod
    def body_parameters(*values: Union[str, int, float]) -> Dict:
        """
        Create body parameters for template
        
        Args:
            *values: Variable number of parameter values
            
        Returns:
            Component dict for body parameters
            
        Example:
            component = TemplateBuilder.body_parameters("John", "Order123", "₹999")
            # Use in template: "Hello {{1}}, your order {{2}} of {{3}} is ready"
        """
        return {
            "type": "body",
            "parameters": [
                {"type": "text", "text": str(val)}
                for val in values
            ]
        }
    
    @staticmethod
    def header_text(text: str) -> Dict:
        """
        Create header text parameter
        
        Args:
            text: Header text value
            
        Returns:
            Component dict for header text
            
        Example:
            component = TemplateBuilder.header_text("Order Confirmation")
        """
        return {
            "type": "header",
            "parameters": [
                {"type": "text", "text": text}
            ]
        }
    
    @staticmethod
    def header_image(image_url: Optional[str] = None, image_id: Optional[str] = None) -> Dict:
        """
        Create header image parameter
        
        Args:
            image_url: Public URL of the image (optional)
            image_id: Media ID from uploaded image (optional)
            
        Returns:
            Component dict for header image
            
        Example:
            # Using URL
            component = TemplateBuilder.header_image(
                image_url="https://example.com/banner.jpg"
            )
            
            # Using media ID
            media_id = client.upload_media("banner.jpg", "image/jpeg")
            component = TemplateBuilder.header_image(image_id=media_id)
        """
        if not image_url and not image_id:
            raise ValueError("Either image_url or image_id must be provided")
        
        image_obj = {}
        if image_id:
            image_obj["id"] = image_id
        elif image_url:
            image_obj["link"] = image_url
        
        return {
            "type": "header",
            "parameters": [
                {"type": "image", "image": image_obj}
            ]
        }
    
    @staticmethod
    def header_video(video_url: Optional[str] = None, video_id: Optional[str] = None) -> Dict:
        """
        Create header video parameter
        
        Args:
            video_url: Public URL of the video (optional)
            video_id: Media ID from uploaded video (optional)
            
        Returns:
            Component dict for header video
            
        Example:
            component = TemplateBuilder.header_video(
                video_url="https://example.com/promo.mp4"
            )
        """
        if not video_url and not video_id:
            raise ValueError("Either video_url or video_id must be provided")
        
        video_obj = {}
        if video_id:
            video_obj["id"] = video_id
        elif video_url:
            video_obj["link"] = video_url
        
        return {
            "type": "header",
            "parameters": [
                {"type": "video", "video": video_obj}
            ]
        }
    
    @staticmethod
    def header_document(document_url: Optional[str] = None, document_id: Optional[str] = None, filename: Optional[str] = None) -> Dict:
        """
        Create header document parameter
        
        Args:
            document_url: Public URL of the document (optional)
            document_id: Media ID from uploaded document (optional)
            filename: Optional filename
            
        Returns:
            Component dict for header document
            
        Example:
            component = TemplateBuilder.header_document(
                document_url="https://example.com/invoice.pdf",
                filename="Invoice_2024.pdf"
            )
        """
        if not document_url and not document_id:
            raise ValueError("Either document_url or document_id must be provided")
        
        document_obj = {}
        if document_id:
            document_obj["id"] = document_id
        elif document_url:
            document_obj["link"] = document_url
        
        if filename:
            document_obj["filename"] = filename
        
        return {
            "type": "header",
            "parameters": [
                {"type": "document", "document": document_obj}
            ]
        }
    
    @staticmethod
    def button_url(index: int, url_suffix: str) -> Dict:
        """
        Create button URL parameter for dynamic URLs
        
        Args:
            index: Button index (0-based)
            url_suffix: Dynamic part to append to button URL
            
        Returns:
            Component dict for button URL
            
        Example:
            # Template button: "View Order" -> https://example.com/orders/{{1}}
            component = TemplateBuilder.button_url(0, "ORD12345")
            # Final URL: https://example.com/orders/ORD12345
        """
        return {
            "type": "button",
            "sub_type": "url",
            "index": index,
            "parameters": [
                {"type": "text", "text": url_suffix}
            ]
        }
    
    @staticmethod
    def button_quick_reply(index: int, payload: str) -> Dict:
        """
        Create quick reply button parameter
        
        Args:
            index: Button index (0-based)
            payload: Payload to send back when clicked
            
        Returns:
            Component dict for quick reply button
            
        Note: This is for templates with predefined quick reply buttons
        """
        return {
            "type": "button",
            "sub_type": "quick_reply",
            "index": index,
            "parameters": [
                {"type": "payload", "payload": payload}
            ]
        }
    
    @staticmethod
    def currency_parameter(
        fallback_value: str,
        code: str,
        amount_1000: int
    ) -> Dict:
        """
        Create currency parameter for body
        
        Args:
            fallback_value: Fallback text (e.g., "₹999")
            code: Currency code (e.g., "INR", "USD")
            amount_1000: Amount in smallest currency unit * 1000
            
        Returns:
            Parameter dict for currency
            
        Example:
            # For ₹999.50
            param = TemplateBuilder.currency_parameter(
                fallback_value="₹999.50",
                code="INR",
                amount_1000=999500  # 999.50 * 1000
            )
        """
        return {
            "type": "currency",
            "currency": {
                "fallback_value": fallback_value,
                "code": code,
                "amount_1000": amount_1000
            }
        }
    
    @staticmethod
    def date_time_parameter(fallback_value: str) -> Dict:
        """
        Create date/time parameter for body
        
        Args:
            fallback_value: Fallback date/time text
            
        Returns:
            Parameter dict for date/time
            
        Example:
            param = TemplateBuilder.date_time_parameter("Dec 25, 2024")
        """
        return {
            "type": "date_time",
            "date_time": {
                "fallback_value": fallback_value
            }
        }
    
    @staticmethod
    def build_template(
        template_name: str,
        language: str = "en",
        header_params: Optional[Dict] = None,
        body_params: Optional[List] = None,
        button_params: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Build complete template message payload
        
        Args:
            template_name: Name of the approved template
            language: Language code (default: "en")
            header_params: Header component (from header_* methods)
            body_params: List of body parameter values
            button_params: List of button components (from button_* methods)
            
        Returns:
            Complete template payload for send_template
            
        Example:
            template = TemplateBuilder.build_template(
                template_name="order_confirmation",
                language="en",
                header_params=TemplateBuilder.header_image(
                    image_url="https://example.com/logo.jpg"
                ),
                body_params=["John", "ORD123", "₹999"],
                button_params=[
                    TemplateBuilder.button_url(0, "ORD123")
                ]
            )
        """
        components = []
        
        # Add header if provided
        if header_params:
            components.append(header_params)
        
        # Add body parameters if provided
        if body_params:
            components.append(
                TemplateBuilder.body_parameters(*body_params)
            )
        
        # Add button parameters if provided
        if button_params:
            components.extend(button_params)
        
        return {
            "name": template_name,
            "language": {"code": language},
            "components": components if components else None
        }


class TemplateValidator:
    """Validate template message components"""
    
    @staticmethod
    def validate_body_params(params: List, expected_count: int) -> bool:
        """
        Validate body parameters count
        
        Args:
            params: List of parameter values
            expected_count: Expected number of parameters in template
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If count doesn't match
        """
        if len(params) != expected_count:
            raise ValueError(
                f"Expected {expected_count} parameters, got {len(params)}"
            )
        return True
    
    @staticmethod
    def validate_button_index(index: int, max_buttons: int = 10) -> bool:
        """
        Validate button index
        
        Args:
            index: Button index
            max_buttons: Maximum allowed buttons
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If index is invalid
        """
        if index < 0 or index >= max_buttons:
            raise ValueError(
                f"Button index must be between 0 and {max_buttons - 1}"
            )
        return True


# ============================================
# Pre-built Template Examples
# ============================================

class CommonTemplates:
    """
    Common pre-built templates for typical use cases
    You still need to create these templates in Meta Business Manager
    """
    
    @staticmethod
    def order_confirmation(
        order_number: str,
        amount: str,
        delivery_date: str 
    ) -> Dict:
        """
        Order confirmation template
        
        Template text example:
        "Your order {{1}} of {{2}} has been confirmed. 
        Expected delivery: {{3}}"
        """
        params = [order_number, amount]
        if delivery_date:
            params.append(delivery_date)
        
        return TemplateBuilder.body_parameters(*params)
    
    @staticmethod
    def otp_verification(otp: str, validity_minutes: str = "5") -> Dict:
        """
        OTP verification template
        
        Template text example:
        "Your OTP is {{1}}. Valid for {{2}} minutes."
        """
        return TemplateBuilder.body_parameters(otp, validity_minutes)
    
    @staticmethod
    def appointment_reminder(
        name: str,
        date: str,
        time: str,
        location: str 
    ) -> Dict:
        """
        Appointment reminder template
        
        Template text example:
        "Hi {{1}}, reminder for your appointment on {{2}} at {{3}}.
        Location: {{4}}"
        """
        params = [name, date, time]
        if location:
            params.append(location)
        
        return TemplateBuilder.body_parameters(*params)
    
    @staticmethod
    def payment_reminder(
        name: str,
        amount: str,
        due_date: str,
        invoice_number: str
    ) -> Dict:
        """
        Payment reminder template
        
        Template text example:
        "Hi {{1}}, this is a reminder that payment of {{2}} 
        is due on {{3}}. Invoice: {{4}}"
        """
        params = [name, amount, due_date]
        if invoice_number:
            params.append(invoice_number)
        
        return TemplateBuilder.body_parameters(*params)
    
    @staticmethod
    def shipping_update(
        order_number: str,
        tracking_number: str,
        carrier: str,
        estimated_delivery: str
    ) -> Dict:
        """
        Shipping update template
        
        Template text example:
        "Your order {{1}} has been shipped! 
        Tracking: {{2}} via {{3}}. 
        Expected delivery: {{4}}"
        """
        params = [order_number, tracking_number, carrier]
        if estimated_delivery:
            params.append(estimated_delivery)
        
        return TemplateBuilder.body_parameters(*params)



def create_template_with_image_header(
    template_name: str,
    image_url: str,
    body_params: List[str],
    language: str = "en"
) -> Dict:
    """
    Quick helper to create template with image header
    
    Args:
        template_name: Template name
        image_url: Header image URL
        body_params: List of body parameter values
        language: Language code
        
    Returns:
        Complete template payload
        
    Example:
        template = create_template_with_image_header(
            "sale_announcement",
            "https://example.com/sale.jpg",
            ["50% OFF", "Today Only!"]
        )
    """
    return {
        "name": template_name,
        "language": {"code": language},
        "components": [
            TemplateBuilder.header_image(image_url=image_url),
            TemplateBuilder.body_parameters(*body_params)
        ]
    }


def create_template_with_cta_button(
    template_name: str,
    body_params: List[str],
    button_url_suffix: str,
    button_index: int = 0,
    language: str = "en"
) -> Dict:
    """
    Quick helper to create template with CTA button
    
    Args:
        template_name: Template name
        body_params: List of body parameter values
        button_url_suffix: Dynamic URL suffix
        button_index: Button index (default: 0)
        language: Language code
        
    Returns:
        Complete template payload
        
    Example:
        template = create_template_with_cta_button(
            "invoice_ready",
            ["INV-2024-001", "₹5,000"],
            "INV-2024-001"  # Appended to button URL
        )
    """
    return {
        "name": template_name,
        "language": {"code": language},
        "components": [
            TemplateBuilder.body_parameters(*body_params),
            TemplateBuilder.button_url(button_index, button_url_suffix)
        ]
    }


def format_currency_indian(amount: float) -> str:
    """
    Format amount in Indian rupee style
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted string (e.g., "₹1,23,456.78")
        
    Example:
        >>> format_currency_indian(123456.78)
        '₹1,23,456.78'
    """
    # Convert to string with 2 decimal places
    amount_str = f"{amount:,.2f}"
    
    # Indian numbering system (lakhs, crores)
    parts = amount_str.split('.')
    integer_part = parts[0].replace(',', '')
    decimal_part = parts[1] if len(parts) > 1 else '00'
    
    # Add commas Indian style
    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        remaining = integer_part[:-3]
        
        # Add commas every 2 digits for remaining
        formatted_remaining = ''
        for i, digit in enumerate(reversed(remaining)):
            if i > 0 and i % 2 == 0:
                formatted_remaining = ',' + formatted_remaining
            formatted_remaining = digit + formatted_remaining
        
        integer_part = formatted_remaining + ',' + last_three
    
    return f"₹{integer_part}.{decimal_part}"
