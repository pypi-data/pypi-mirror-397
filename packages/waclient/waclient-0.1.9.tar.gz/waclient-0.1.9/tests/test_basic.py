"""
Basic tests for whatsapp-biz package
"""


def test_import():
    """Test if package imports correctly"""
    try:
        from waclient import WhatsAppClient

        print("[PASS] Import successful!")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False


def test_client_creation():
    """Test if client can be instantiated"""
    try:
        from waclient import WhatsAppClient

        client = WhatsAppClient(
            phone_number_id="YOUR_PHONE_ID",
            access_token="YOUR_ACCESS_TOKEN",
        )

        print("[PASS] Client created successfully!")
        print(f"   Phone ID: {client.phone_number_id}")
        print(f"   Base URL: {client.base_url}")
        return True
    except Exception as e:
        print(f"[FAIL] Client creation failed: {e}")
        return False


def test_message_builder():
    """Test message builders"""
    try:
        from waclient.messages import MessageBuilder

        builder = MessageBuilder()

        # Test text message
        msg = builder.text_message("919342585854", "Hello!")
        assert msg["type"] == "text"
        assert msg["text"]["body"] == "Hello!"

        print("[PASS] Message builder works!")
        return True
    except Exception as e:
        print(f"[FAIL] Message builder failed: {e}")
        return False


def test_template_builder():
    """Test template builders"""
    try:
        from waclient.templates import TemplateBuilder

        component = TemplateBuilder.body_parameters("value1", "value2")
        assert component["type"] == "body"
        assert len(component["parameters"]) == 2

        print("[PASS] Template builder works!")
        return True
    except Exception as e:
        print(f"[FAIL] Template builder failed: {e}")
        return False


def test_utils():
    """Test utility functions"""
    try:
        from waclient.utils import format_phone_number, validate_phone_number

        # Test phone formatting
        phone = format_phone_number("9342585854")
        assert phone == "919342585854"

        # Test validation
        assert validate_phone_number("919342585854") == True

        print("[PASS] Utils work!")
        return True
    except Exception as e:
        print(f"[FAIL] Utils failed: {e}")
        return False


def test_exceptions():
    """Test custom exceptions"""
    try:
        from waclient.exceptions import (
            WhatsAppError,
            AuthenticationError,
            MessageError,
            MediaError,
        )

        # Test exception creation
        error = WhatsAppError("Test error")
        assert str(error) == "Test error"

        print("[PASS] Exceptions work!")
        return True
    except Exception as e:
        print(f"[FAIL] Exceptions test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("[TEST] Testing whatsapp-biz Package")
    print("=" * 50)

    tests = [
        test_import,
        test_client_creation,
        test_message_builder,
        test_template_builder,
        test_utils,
        test_exceptions,
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\n[RUN] Running: {test.__name__}")
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[FAIL] Test crashed: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print("=" * 50)
