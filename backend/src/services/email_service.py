from typing import Dict, Any, List, Optional
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import logging
from jinja2 import Environment, FileSystemLoader
from ..utils.error_handler import APIError

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Initialize email service with configuration"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.sender_email = os.getenv('SENDER_EMAIL')
        
        if not all([self.smtp_username, self.smtp_password, self.sender_email]):
            raise APIError(
                "Email service not properly configured",
                error_code="EMAIL_CONFIG_ERROR",
                is_retryable=False
            )
        
        # Initialize Jinja2 template environment
        template_dir = os.path.join(os.path.dirname(__file__), '../templates')
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )

    def _create_html_content(self, reading_data: Dict[str, Any]) -> str:
        """Create HTML email content using template"""
        try:
            template = self.jinja_env.get_template('reading_email.html')
            return template.render(
                mbti_type=reading_data['mbtiType'],
                mbti_description=reading_data['mbtiDescription'],
                cards=reading_data['cards']
            )
        except Exception as e:
            logger.error(f"Error creating email content: {str(e)}")
            raise APIError("Failed to create email content")

    def _create_text_content(self, reading_data: Dict[str, Any]) -> str:
        """Create plain text email content"""
        try:
            text = f"""
Your Mystic Tarot Reading

Personality Type: {reading_data['mbtiType']}
{reading_data['mbtiDescription']}

Your Cards:
"""
            for card in reading_data['cards']:
                text += f"\n{card['name']}\n{card['meaning']}\n"
            
            text += "\nVisit our website to view the card images and save them as NFTs!"
            return text
        except Exception as e:
            logger.error(f"Error creating text content: {str(e)}")
            raise APIError("Failed to create email content")

    def _attach_images(
        self,
        message: MIMEMultipart,
        image_paths: List[str]
    ) -> None:
        """Attach card images to email"""
        try:
            for i, image_path in enumerate(image_paths):
                with open(image_path, 'rb') as f:
                    img = MIMEImage(f.read())
                    img.add_header(
                        'Content-ID',
                        f'<card_{i}>'
                    )
                    message.attach(img)
        except Exception as e:
            logger.error(f"Error attaching images: {str(e)}")
            raise APIError("Failed to attach images to email")

    def send_reading(
        self,
        to_email: str,
        reading_data: Dict[str, Any],
        image_paths: Optional[List[str]] = None
    ) -> None:
        """Send tarot reading email"""
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = f"Your {reading_data['mbtiType']} Tarot Reading"
            message['From'] = self.sender_email
            message['To'] = to_email

            # Create plain text and HTML versions
            text_content = self._create_text_content(reading_data)
            html_content = self._create_html_content(reading_data)

            # Attach both versions
            message.attach(MIMEText(text_content, 'plain'))
            message.attach(MIMEText(html_content, 'html'))

            # Attach images if provided
            if image_paths:
                self._attach_images(message, image_paths)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)

            logger.info(f"Successfully sent reading email to {to_email}")

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            raise APIError(
                "Email service authentication failed",
                error_code="EMAIL_AUTH_ERROR",
                is_retryable=False
            )
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            raise APIError(
                "Failed to send email",
                error_code="EMAIL_SEND_ERROR",
                is_retryable=True
            )
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            raise APIError("Failed to send email")
