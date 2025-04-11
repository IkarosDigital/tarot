import pytest
from unittest.mock import MagicMock, patch
import os
from PIL import Image
import io
from ..src.tarot.card_generator import (
    CardGenerator,
    CardGenerationError,
    CardGenerationResult,
    ErrorCode
)

@pytest.fixture
def card_generator():
    """Create card generator with test configuration"""
    return CardGenerator(
        api_key='test_api_key',
        output_dir='test_output'
    )

@pytest.fixture
def mock_stability_response():
    """Create mock Stability AI response"""
    # Create a small test image
    img = Image.new('RGB', (100, 100), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    mock_artifact = MagicMock()
    mock_artifact.binary = img_byte_arr
    
    mock_answer = MagicMock()
    mock_answer.artifacts = [mock_artifact]
    
    return [mock_answer]

def test_card_generator_initialization():
    """Test card generator initialization"""
    # Test with invalid API key
    with pytest.raises(CardGenerationError) as exc_info:
        CardGenerator(api_key='', output_dir='test')
    assert exc_info.value.error_code == ErrorCode.INVALID_API_KEY.value

    # Test with valid configuration
    generator = CardGenerator(api_key='test_key', output_dir='test')
    assert generator.api_key == 'test_key'
    assert os.path.exists('test')  # Output directory should be created

def test_validate_prompt(card_generator):
    """Test prompt validation"""
    # Test empty prompt
    with pytest.raises(CardGenerationError) as exc_info:
        card_generator._validate_prompt('')
    assert exc_info.value.error_code == ErrorCode.INVALID_PROMPT.value

    # Test short prompt
    with pytest.raises(CardGenerationError) as exc_info:
        card_generator._validate_prompt('too short')
    assert exc_info.value.error_code == ErrorCode.INVALID_PROMPT.value

    # Test valid prompt
    card_generator._validate_prompt('This is a valid prompt for testing purposes')

@patch('stability_sdk.client.StabilityInference.generate')
def test_generate_image_success(mock_generate, card_generator, mock_stability_response):
    """Test successful image generation"""
    mock_generate.return_value = mock_stability_response
    
    image = card_generator._generate_image(
        "Test prompt for generating a tarot card"
    )
    assert isinstance(image, Image.Image)
    assert image.size == (100, 100)

@patch('stability_sdk.client.StabilityInference.generate')
def test_generate_image_rate_limit(mock_generate, card_generator):
    """Test rate limit handling"""
    from stability_sdk.exceptions import RateLimitError
    
    mock_generate.side_effect = RateLimitError('Rate limit exceeded')
    
    with pytest.raises(CardGenerationError) as exc_info:
        card_generator._generate_image("Test prompt")
    assert exc_info.value.error_code == ErrorCode.RATE_LIMIT_EXCEEDED.value

@patch('stability_sdk.client.StabilityInference.generate')
def test_generate_image_invalid_request(mock_generate, card_generator):
    """Test invalid request handling"""
    from stability_sdk.exceptions import StabilityInvalidRequest
    
    mock_generate.side_effect = StabilityInvalidRequest('Invalid prompt')
    
    with pytest.raises(CardGenerationError) as exc_info:
        card_generator._generate_image("Test prompt")
    assert exc_info.value.error_code == ErrorCode.INVALID_PROMPT.value
    assert not exc_info.value.is_retryable

def test_process_image(card_generator):
    """Test image processing"""
    # Create test image
    test_image = Image.new('RGB', (100, 150), color='red')
    
    # Process image
    output_path = card_generator._process_image(test_image, "Test Card")
    
    # Verify output
    assert os.path.exists(output_path)
    processed_image = Image.open(output_path)
    assert processed_image.size == (140, 190)  # Original size + 2*border_size

def test_generate_card(card_generator, mock_stability_response):
    """Test complete card generation"""
    with patch('stability_sdk.client.StabilityInference.generate') as mock_generate:
        mock_generate.return_value = mock_stability_response
        
        result = card_generator.generate_card(
            "The Fool",
            personality_traits=["INTJ"]
        )
        
        assert isinstance(result, CardGenerationResult)
        assert result.success
        assert os.path.exists(result.image_path)
        assert result.metadata["card_name"] == "The Fool"

def test_generate_reading(card_generator):
    """Test complete reading generation"""
    with patch.object(card_generator, 'generate_card') as mock_generate_card:
        # Mock successful card generation
        mock_generate_card.return_value = CardGenerationResult(
            image_path="test.png",
            success=True,
            metadata={
                "card_name": "Test Card",
                "meaning": "Test meaning"
            }
        )
        
        results = card_generator.generate_reading("INTJ")
        assert len(results) == 3  # Default reading size
        assert all(r.success for r in results)

def test_error_handling(card_generator):
    """Test error handling in card generation"""
    # Test with invalid card name
    result = card_generator.generate_card("Invalid Card")
    assert not result.success
    assert isinstance(result.error, CardGenerationError)
    assert result.error.error_code == ErrorCode.INVALID_PROMPT.value

    # Test with network error
    with patch('stability_sdk.client.StabilityInference.generate') as mock_generate:
        mock_generate.side_effect = Exception("Network error")
        result = card_generator.generate_card("The Fool")
        assert not result.success
        assert isinstance(result.error, CardGenerationError)
        assert result.error.error_code == ErrorCode.STABILITY_API_ERROR.value

def test_personality_card_mapping(card_generator):
    """Test personality type to card mapping"""
    # Test known personality type
    cards = card_generator._get_cards_for_personality("INTJ")
    assert len(cards) == 3
    assert "The Hermit" in cards
    assert "The High Priestess" in cards

    # Test unknown personality type
    cards = card_generator._get_cards_for_personality("UNKNOWN")
    assert len(cards) == 3
    assert "The Fool" in cards  # Should get default selection
