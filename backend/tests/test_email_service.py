import pytest
from unittest.mock import MagicMock, patch
import os
from ..src.services.email_service import EmailService
from ..src.utils.error_handler import APIError

@pytest.fixture
def email_service():
    """Create email service with test configuration"""
    os.environ['SMTP_SERVER'] = 'test.smtp.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['SMTP_USERNAME'] = 'test@example.com'
    os.environ['SMTP_PASSWORD'] = 'test_password'
    os.environ['SENDER_EMAIL'] = 'noreply@mystictarot.com'
    return EmailService()

@pytest.fixture
def sample_reading():
    """Sample reading data for tests"""
    return {
        'mbtiType': 'INTJ',
        'mbtiDescription': 'The Architect: Strategic and thoughtful...',
        'cards': [
            {
                'name': 'The Hermit',
                'meaning': 'A time for introspection...',
                'imageUrl': '/images/hermit.png'
            },
            {
                'name': 'The Star',
                'meaning': 'Hope and inspiration...',
                'imageUrl': '/images/star.png'
            }
        ]
    }

def test_email_service_initialization():
    """Test email service initialization"""
    # Test with missing configuration
    os.environ.clear()
    with pytest.raises(APIError) as exc_info:
        EmailService()
    assert exc_info.value.error_code == "EMAIL_CONFIG_ERROR"

    # Test with valid configuration
    os.environ['SMTP_USERNAME'] = 'test@example.com'
    os.environ['SMTP_PASSWORD'] = 'test_password'
    os.environ['SENDER_EMAIL'] = 'noreply@mystictarot.com'
    service = EmailService()
    assert service.smtp_username == 'test@example.com'

def test_create_text_content(email_service, sample_reading):
    """Test plain text email content creation"""
    text_content = email_service._create_text_content(sample_reading)
    assert sample_reading['mbtiType'] in text_content
    assert "The Hermit" in text_content
    assert "The Star" in text_content

def test_create_html_content(email_service, sample_reading):
    """Test HTML email content creation"""
    html_content = email_service._create_html_content(sample_reading)
    assert sample_reading['mbtiType'] in html_content
    assert "The Hermit" in html_content
    assert "The Star" in html_content
    assert '<html>' in html_content
    assert '</html>' in html_content

@patch('smtplib.SMTP')
def test_send_reading_success(mock_smtp, email_service, sample_reading):
    """Test successful email sending"""
    mock_smtp_instance = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

    email_service.send_reading(
        'test@example.com',
        sample_reading,
        ['test_image1.png', 'test_image2.png']
    )

    # Verify SMTP calls
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with(
        email_service.smtp_username,
        email_service.smtp_password
    )
    mock_smtp_instance.send_message.assert_called_once()

@patch('smtplib.SMTP')
def test_send_reading_auth_error(mock_smtp, email_service, sample_reading):
    """Test SMTP authentication error"""
    mock_smtp_instance = MagicMock()
    mock_smtp_instance.login.side_effect = smtplib.SMTPAuthenticationError(535, b'Auth failed')
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

    with pytest.raises(APIError) as exc_info:
        email_service.send_reading('test@example.com', sample_reading)
    
    assert exc_info.value.error_code == "EMAIL_AUTH_ERROR"
    assert not exc_info.value.is_retryable

@patch('smtplib.SMTP')
def test_send_reading_smtp_error(mock_smtp, email_service, sample_reading):
    """Test general SMTP error"""
    mock_smtp_instance = MagicMock()
    mock_smtp_instance.send_message.side_effect = smtplib.SMTPException('Failed to send')
    mock_smtp.return_value.__enter__.return_value = mock_smtp_instance

    with pytest.raises(APIError) as exc_info:
        email_service.send_reading('test@example.com', sample_reading)
    
    assert exc_info.value.error_code == "EMAIL_SEND_ERROR"
    assert exc_info.value.is_retryable

def test_attach_images(email_service):
    """Test image attachment"""
    message = MIMEMultipart('alternative')
    test_images = ['test1.png', 'test2.png']

    # Test with missing images
    with pytest.raises(APIError) as exc_info:
        email_service._attach_images(message, test_images)
    assert "Failed to attach images" in str(exc_info.value)

    # Test with valid images
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value.__enter__.return_value.read.return_value = b'test image data'
        email_service._attach_images(message, test_images)
        assert mock_open.call_count == len(test_images)

def test_invalid_email_format(email_service, sample_reading):
    """Test sending to invalid email"""
    invalid_emails = ['not_an_email', '@missing.com', 'missing@', 'missing@.com']
    
    for email in invalid_emails:
        with pytest.raises(APIError) as exc_info:
            email_service.send_reading(email, sample_reading)
        assert "Invalid email format" in str(exc_info.value)
