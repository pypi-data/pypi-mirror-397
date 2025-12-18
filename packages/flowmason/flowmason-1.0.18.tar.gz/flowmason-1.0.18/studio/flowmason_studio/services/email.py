"""
FlowMason Email Service

Handles sending emails for password resets, notifications, etc.

This is a stub implementation that logs emails to the console.
For production, implement SMTPEmailService or use a service like SendGrid.
"""

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Email message data"""
    to: List[str]
    subject: str
    body_text: str
    body_html: Optional[str] = None
    from_address: Optional[str] = None
    reply_to: Optional[str] = None


class EmailService(ABC):
    """Abstract base class for email services"""

    @abstractmethod
    async def send(self, message: EmailMessage) -> bool:
        """Send an email message. Returns True if successful."""
        pass

    async def send_password_reset(
        self,
        to_email: str,
        reset_url: str,
        user_name: Optional[str] = None,
    ) -> bool:
        """Send a password reset email"""
        name = user_name or "User"

        message = EmailMessage(
            to=[to_email],
            subject="Reset Your FlowMason Password",
            body_text=f"""Hi {name},

You requested to reset your FlowMason password.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, you can safely ignore this email.

- The FlowMason Team
""",
            body_html=f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .button {{ display: inline-block; padding: 12px 24px; background-color: #4F46E5; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>Reset Your Password</h2>
        <p>Hi {name},</p>
        <p>You requested to reset your FlowMason password.</p>
        <p>Click the button below to reset your password:</p>
        <a href="{reset_url}" class="button">Reset Password</a>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #666;">{reset_url}</p>
        <p><strong>This link will expire in 24 hours.</strong></p>
        <p>If you didn't request this, you can safely ignore this email.</p>
        <div class="footer">
            <p>- The FlowMason Team</p>
        </div>
    </div>
</body>
</html>
""",
        )

        return await self.send(message)


class ConsoleEmailService(EmailService):
    """
    Email service that logs emails to the console.

    Use this for development and testing.
    """

    async def send(self, message: EmailMessage) -> bool:
        """Log email to console instead of sending"""
        logger.info("=" * 60)
        logger.info("EMAIL MESSAGE (Console - Not Actually Sent)")
        logger.info("=" * 60)
        logger.info(f"To: {', '.join(message.to)}")
        logger.info(f"Subject: {message.subject}")
        logger.info("-" * 40)
        logger.info(message.body_text)
        logger.info("=" * 60)

        # Also print to stdout for visibility during development
        print("\n" + "=" * 60)
        print("EMAIL MESSAGE (Console - Not Actually Sent)")
        print("=" * 60)
        print(f"To: {', '.join(message.to)}")
        print(f"Subject: {message.subject}")
        print("-" * 40)
        print(message.body_text)
        print("=" * 60 + "\n")

        return True


class SMTPEmailService(EmailService):
    """
    Email service using SMTP.

    Configure with environment variables:
    - SMTP_HOST: SMTP server hostname
    - SMTP_PORT: SMTP server port (default: 587)
    - SMTP_USER: SMTP username
    - SMTP_PASSWORD: SMTP password
    - SMTP_FROM: From address
    - SMTP_TLS: Use TLS (default: true)
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        from_address: Optional[str] = None,
        use_tls: bool = True,
    ):
        self.host = host or os.getenv("SMTP_HOST", "localhost")
        self.port = port or int(os.getenv("SMTP_PORT", "587"))
        self.user = user or os.getenv("SMTP_USER")
        self.password = password or os.getenv("SMTP_PASSWORD")
        self.from_address = from_address or os.getenv("SMTP_FROM", "noreply@flowmason.io")
        self.use_tls = use_tls if use_tls is not None else os.getenv("SMTP_TLS", "true").lower() == "true"

    async def send(self, message: EmailMessage) -> bool:
        """Send email via SMTP"""
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = message.from_address or self.from_address
            msg["To"] = ", ".join(message.to)

            if message.reply_to:
                msg["Reply-To"] = message.reply_to

            # Attach plain text version
            msg.attach(MIMEText(message.body_text, "plain"))

            # Attach HTML version if available
            if message.body_html:
                msg.attach(MIMEText(message.body_html, "html"))

            # Connect and send
            if self.use_tls:
                server = smtplib.SMTP(self.host, self.port)
                server.starttls()
            else:
                server = smtplib.SMTP(self.host, self.port)

            if self.user and self.password:
                server.login(self.user, self.password)

            server.sendmail(
                msg["From"],
                message.to,
                msg.as_string(),
            )
            server.quit()

            logger.info(f"Email sent to {', '.join(message.to)}: {message.subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """
    Get the global email service instance.

    Returns SMTPEmailService if SMTP_HOST is configured, else ConsoleEmailService.
    """
    global _email_service
    if _email_service is None:
        if os.getenv("SMTP_HOST"):
            _email_service = SMTPEmailService()
        else:
            _email_service = ConsoleEmailService()
    return _email_service


def set_email_service(service: EmailService) -> None:
    """Set the global email service instance (for testing)"""
    global _email_service
    _email_service = service
