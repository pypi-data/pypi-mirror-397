# WhatsApp Biz

**Simplified Python SDK for WhatsApp Business Cloud API**

[![PyPI version](https://badge.fury.io/py/waclient.svg)](https://badge.fury.io/py/waclient)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/waclient.svg)](https://pypi.org/project/waclient/)

`waclient` is a clean, easy-to-use Python wrapper for the WhatsApp Business Cloud API. It handles authentication, message composition (text, media, interactive), and media management, allowing you to build WhatsApp bots and integrations quickly.

## Features

- **Easy Authentication**: Simple client initialization.
- **Rich Messaging**: Send Text, Image, Video, Audio, Document, Sticker, Location, and Contact messages.
- **Interactive Elements**: Support for Reply Buttons and List Messages.
- **Templates**: Full support for WhatsApp Template Messages.
- **Media Handling**: Upload and retrieve media easily.

## Installation

```bash
pip install waclient
```

## Quick Start

```python
from waclient import WhatsAppClient

client = WhatsAppClient(
    phone_number_id="YOUR_PHONE_ID",
    access_token="YOUR_ACCESS_TOKEN"
)

client.messages.send_text(to="15551234567", body="Hello form WhatsApp Biz!")
```

## Documentation

- **[User Manual](USER_MANUAL.md)**: Detailed verification of all features, code examples, and configuration.
- **[Developer Guide](DEVELOPER_GUIDE.md)**: Setup for contributors, running tests, and project structure.

## ⚠️ WhatsApp 24-Hour Messaging Rule (Important)

WhatsApp enforces a **24-hour customer service window**.

- Free-form messages can be sent **only within 24 hours** after a user’s last message.
- After 24 hours, businesses **must use approved WhatsApp Template Messages**.
- This is a **WhatsApp platform rule**, not a limitation of `waclient`.

### How waclient handles this
- Supports **session messages** (within 24 hours)
- Supports **template messages** (can be sent anytime)
- Webhook-based message tracking helps manage the 24-hour window

📌 Popular platforms like **Amazon, Flipkart, Swiggy** also use **template messages** for notifications.


## Examples

Check the `examples/` directory for ready-to-run scripts:
- `examples/verify_features.py`: comprehensive tour of features.
- `examples/verify_delivery.py`: delivery status verification.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Surenthar**  
Email: surentharsenthilkumar2003@gmail.com
