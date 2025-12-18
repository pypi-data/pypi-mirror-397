"""
email_sender package

Provides helper functions for sending email via a custom API.
"""

from .mailer_function import send_email_no_attachment
__all__ = ["send_email_no_attachment"]