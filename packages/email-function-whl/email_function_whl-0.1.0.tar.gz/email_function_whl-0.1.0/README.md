# email-sender

A lightweight internal Python library that provides reusable email-sending utilities for the Fabric Notebook team.

This package is designed to be published as a wheel (.whl) and consumed across internal services.

---

## Features

- Send emails via a simple POST API
- Supports multiple recipients
- Handles 200, 201, 202 as successful response codes
- Minimal dependencies (only `requests`)
- Easy to integrate in notebooks, scripts, or internal pipelines

---

## Installation

Install the wheel file:

```bash
pip install email_sender-0.1.0-py3-none-any.whl

# Creating the wheel file
pip install build       # Install the build tool
python -m build         # Build the .whl file

"""
Usage:
from email_sender import send_email_no_attachment

status, response = send_email_no_attachment(
    {
        "to": ["user1@domain.com", "user2@domain.com"],
        "subject": "Team Update",
        "body": "Hello team!"
    },
    endpoint_url="https://your-mail-endpoint",
    access_token="YOUR_ACCESS_TOKEN"
)

print(status, response)
"""