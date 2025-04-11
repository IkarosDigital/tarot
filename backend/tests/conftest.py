import pytest
import os
import shutil
from PIL import Image
import io

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables and directories"""
    # Create test directories
    os.makedirs('test_output', exist_ok=True)
    os.makedirs('test_templates', exist_ok=True)
    
    yield
    
    # Cleanup after tests
    shutil.rmtree('test_output', ignore_errors=True)
    shutil.rmtree('test_templates', ignore_errors=True)

@pytest.fixture
def sample_image():
    """Create a sample test image"""
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

@pytest.fixture
def sample_card_data():
    """Sample card data for tests"""
    return {
        "The Fool": {
            "prompt": "A whimsical figure stepping off a cliff...",
            "meaning": "New beginnings, innocence, spontaneity"
        },
        "The Magician": {
            "prompt": "A powerful figure channeling cosmic energy...",
            "meaning": "Manifestation, resourcefulness, power"
        },
        "The High Priestess": {
            "prompt": "A mysterious feminine figure between pillars...",
            "meaning": "Intuition, mystery, inner knowledge"
        }
    }

@pytest.fixture
def mock_email_config(monkeypatch):
    """Mock email configuration"""
    monkeypatch.setenv('SMTP_SERVER', 'test.smtp.com')
    monkeypatch.setenv('SMTP_PORT', '587')
    monkeypatch.setenv('SMTP_USERNAME', 'test@example.com')
    monkeypatch.setenv('SMTP_PASSWORD', 'test_password')
    monkeypatch.setenv('SENDER_EMAIL', 'noreply@mystictarot.com')
