from flask import Flask, request, jsonify
from .utils.error_handler import error_handler, validate_request, rate_limit, APIError, ValidationError
from .tarot.card_generator import CardGenerator, CardGenerationError
from typing import Dict, Any
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize card generator
card_generator = CardGenerator(
    api_key=os.getenv('STABILITY_API_KEY'),
    output_dir=os.getenv('OUTPUT_DIR', 'generated_cards')
)

# Request validation schemas
quiz_schema = {
    "type": "object",
    "properties": {
        "answers": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"}
                },
                "required": ["question", "answer"]
            }
        },
        "walletAddress": {"type": ["string", "null"]}
    },
    "required": ["answers"]
}

@app.route('/api/questions', methods=['GET'])
@error_handler
def get_questions():
    """Get personality quiz questions"""
    try:
        questions = [
            {
                "text": "After a social gathering, you typically feel:",
                "options": [
                    "Energized and ready for more social interaction",
                    "Need time alone to recharge"
                ]
            },
            # Add more questions...
        ]
        return jsonify({"success": True, "questions": questions})
    except Exception as e:
        logger.error(f"Error fetching questions: {str(e)}")
        raise APIError("Failed to fetch questions")

@app.route('/api/calculate-result', methods=['POST'])
@error_handler
@validate_request(quiz_schema)
@rate_limit(max_requests=10, time_window=60)  # 10 requests per minute
def calculate_result():
    """Calculate personality type and generate cards"""
    try:
        data = request.get_json()
        answers = data['answers']
        wallet_address = data.get('walletAddress')

        # Calculate MBTI type
        mbti_type = calculate_mbti_type(answers)
        
        # Generate cards
        cards = []
        reading_results = card_generator.generate_reading(mbti_type)
        
        for result in reading_results:
            if not result.success:
                logger.error(f"Card generation failed: {result.error.message}")
                if not result.error.is_retryable:
                    raise APIError(
                        "Failed to generate some cards",
                        details={"error": result.error.message}
                    )
            else:
                cards.append({
                    "name": result.metadata["card_name"],
                    "meaning": result.metadata["meaning"],
                    "imageUrl": f"/images/{os.path.basename(result.image_path)}"
                })

        response_data = {
            "success": True,
            "mbtiType": mbti_type,
            "mbtiDescription": get_mbti_description(mbti_type),
            "cards": cards
        }

        # Store result if wallet connected
        if wallet_address:
            store_reading_result(wallet_address, response_data)

        return jsonify(response_data)

    except CardGenerationError as e:
        logger.error(f"Card generation error: {str(e)}")
        raise APIError(
            message=e.message,
            error_code=e.error_code,
            is_retryable=e.is_retryable
        )
    except Exception as e:
        logger.error(f"Error calculating result: {str(e)}")
        raise APIError("Failed to calculate result")

@app.route('/api/mint-nft', methods=['POST'])
@error_handler
@rate_limit(max_requests=5, time_window=300)  # 5 requests per 5 minutes
def mint_nft():
    """Mint reading as NFT"""
    try:
        data = request.get_json()
        if not data.get('reading') or not data.get('walletAddress'):
            raise ValidationError("Missing required fields")

        # Mint NFT logic here
        # This would interact with your blockchain contract

        return jsonify({
            "success": True,
            "message": "NFT minted successfully",
            "openseaUrl": f"https://opensea.io/assets/{contract_address}/{token_id}"
        })
    except Exception as e:
        logger.error(f"Error minting NFT: {str(e)}")
        raise APIError("Failed to mint NFT")

@app.route('/api/save-reading', methods=['POST'])
@error_handler
@rate_limit(max_requests=10, time_window=60)
def save_reading():
    """Save reading to email"""
    try:
        data = request.get_json()
        if not data.get('email') or not data.get('reading'):
            raise ValidationError("Missing required fields")

        # Email sending logic here
        send_reading_email(data['email'], data['reading'])

        return jsonify({
            "success": True,
            "message": "Reading saved and email sent"
        })
    except Exception as e:
        logger.error(f"Error saving reading: {str(e)}")
        raise APIError("Failed to save reading")

def calculate_mbti_type(answers: list) -> str:
    """Calculate MBTI type from quiz answers"""
    try:
        # MBTI calculation logic here
        return "INTJ"  # Placeholder
    except Exception as e:
        logger.error(f"Error calculating MBTI type: {str(e)}")
        raise APIError("Failed to calculate personality type")

def get_mbti_description(mbti_type: str) -> str:
    """Get description for MBTI type"""
    descriptions = {
        "INTJ": "The Architect: Imaginative and strategic thinkers...",
        # Add more descriptions...
    }
    return descriptions.get(mbti_type, "Description not found")

def store_reading_result(wallet_address: str, result: Dict[str, Any]) -> None:
    """Store reading result in database"""
    try:
        # Database storage logic here
        pass
    except Exception as e:
        logger.error(f"Error storing reading: {str(e)}")
        # Don't raise error, just log it as this is not critical

def send_reading_email(email: str, reading: Dict[str, Any]) -> None:
    """Send reading results via email"""
    try:
        # Email sending logic here
        pass
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise APIError("Failed to send email")
