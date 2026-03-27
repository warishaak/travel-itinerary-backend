"""
SendGrid email service utility for the Travel Itinerary Backend.

This module provides a reusable email sending functionality using SendGrid API.
"""

import logging
from typing import List, Optional, Union

from django.conf import settings
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, From, Mail, To

logger = logging.getLogger(__name__)


class EmailService:
    """Service class for sending emails via SendGrid."""

    def __init__(self):
        """Initialize the EmailService with SendGrid API key."""
        self.api_key = settings.SENDGRID_API_KEY
        if not self.api_key:
            logger.warning(
                "SENDGRID_API_KEY is not configured. Email sending will fail."
            )
        self.client = SendGridAPIClient(self.api_key) if self.api_key else None
        self.from_email = settings.FROM_EMAIL

    def send_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        html_content: Optional[str] = None,
        plain_text_content: Optional[str] = None,
        from_email: Optional[str] = None,
    ) -> bool:
        """
        Send an email using SendGrid.

        Args:
            to_emails: Single email address or list of email addresses
            subject: Email subject line
            html_content: HTML content of the email (optional)
            plain_text_content: Plain text content of the email (optional)
            from_email: Override the default from_email (optional)

        Returns:
            bool: True if email was sent successfully, False otherwise

        Raises:
            ValueError: If neither html_content nor plain_text_content is provided
        """
        if not html_content and not plain_text_content:
            raise ValueError(
                "Either html_content or plain_text_content must be provided"
            )

        if not self.client:
            logger.error("SendGrid client is not initialized. Cannot send email.")
            return False

        try:
            # Prepare sender email
            sender = from_email or self.from_email

            # Prepare message
            message = Mail(
                from_email=From(sender),
                to_emails=(
                    To(to_emails)
                    if isinstance(to_emails, str)
                    else [To(email) for email in to_emails]
                ),
                subject=subject,
            )

            # Add content
            if html_content:
                message.content = Content("text/html", html_content)
            if plain_text_content:
                message.content = Content("text/plain", plain_text_content)

            # Send email
            response = self.client.send(message)

            # Log success
            logger.info(
                f"Email sent successfully. Status: {response.status_code}, "
                f"Subject: '{subject}', To: {to_emails}"
            )

            # Status 202 means email was queued successfully
            return response.status_code in [200, 202]

        except Exception as exc:
            logger.error(
                f"Failed to send email. Subject: '{subject}', To: {to_emails}, "
                f"Error: {exc}",
                exc_info=True,
            )
            return False

    def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """
        Send a welcome email to a new user.

        Args:
            user_email: User's email address
            user_name: User's name

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = "Welcome to Travel Itinerary!"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #4A90E2;">Welcome to Travel Itinerary, {user_name}!</h2>
                <p>Thank you for joining our platform. We're excited to help you plan your next adventure.</p>
                <p>Get started by creating your first itinerary and explore amazing travel destinations.</p>
                <br>
                <p>Best regards,</p>
                <p><strong>The Travel Itinerary Team</strong></p>
            </body>
        </html>
        """
        plain_text_content = f"""
        Welcome to Travel Itinerary, {user_name}!

        Thank you for joining our platform. We're excited to help you plan your next adventure.

        Get started by creating your first itinerary and explore amazing travel destinations.

        Best regards,
        The Travel Itinerary Team
        """

        return self.send_email(
            to_emails=user_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_text_content,
        )

    def send_itinerary_confirmation_email(
        self, user_email: str, user_name: str, itinerary_title: str
    ) -> bool:
        """
        Send a confirmation email when a user creates a new itinerary.

        Args:
            user_email: User's email address
            user_name: User's name
            itinerary_title: Title of the created itinerary

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        subject = f"Itinerary Created: {itinerary_title}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: #4A90E2;">Itinerary Created Successfully!</h2>
                <p>Hi {user_name},</p>
                <p>Your itinerary "<strong>{itinerary_title}</strong>" has been created successfully.</p>
                <p>You can now add destinations, activities, and share it with your travel companions.</p>
                <br>
                <p>Happy planning!</p>
                <p><strong>The Travel Itinerary Team</strong></p>
            </body>
        </html>
        """
        plain_text_content = f"""
        Itinerary Created Successfully!

        Hi {user_name},

        Your itinerary "{itinerary_title}" has been created successfully.

        You can now add destinations, activities, and share it with your travel companions.

        Happy planning!
        The Travel Itinerary Team
        """

        return self.send_email(
            to_emails=user_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=plain_text_content,
        )


# Create a singleton instance
email_service = EmailService()
