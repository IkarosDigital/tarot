from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from .card_generator import TarotCardGenerator
from .user_manager import UserManager
from web3 import Web3
import json
import os
from pathlib import Path
import eth_account
from eth_account.messages import encode_defunct

app = Flask(__name__)
CORS(app)

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent

# Load MBTI data
with open(ROOT_DIR / 'data/mbti_personalities.json', 'r') as f:
    mbti_data = json.load(f)

with open(ROOT_DIR / 'data/questions.json', 'r') as f:
    questions_data = json.load(f)

# Initialize managers
card_generator = TarotCardGenerator()
user_manager = UserManager()
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Local provider for testing

@app.route('/')
def serve_index():
    return send_from_directory(ROOT_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(ROOT_DIR, path)

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Return personality quiz questions"""
    return jsonify(questions_data)

@app.route('/api/verify-wallet', methods=['POST'])
def verify_wallet():
    """Verify wallet signature"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        address = data.get('address')
        signature = data.get('signature')
        message = data.get('message')

        if not all([address, signature, message]):
            return jsonify({'error': 'Missing required fields'}), 400

        try:
            # Create message hash
            message_hash = encode_defunct(text=message)
            
            # Verify the signature
            recovered_address = w3.eth.account.recover_message(
                message_hash,
                signature=signature
            )
            
            if recovered_address.lower() != address.lower():
                return jsonify({'error': 'Invalid signature'}), 401

            # Register or update user
            user_manager.register_user(address)
            
            return jsonify({'verified': True})
        except Exception as e:
            return jsonify({'error': f'Signature verification failed: {str(e)}'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/calculate-result', methods=['POST'])
def calculate_result():
    """Calculate MBTI result and generate tarot cards"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        answers = data.get('answers')
        wallet_address = data.get('walletAddress')
        wallet_signature = data.get('walletSignature')
        template_id = data.get('template_id', 'classic')

        if not all([answers, wallet_address, wallet_signature]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Verify wallet ownership
        if not user_manager.verify_user(wallet_address, wallet_signature):
            return jsonify({'error': 'Invalid wallet authentication'}), 401

        # Calculate MBTI type
        try:
            mbti_type = calculate_mbti_type(answers)
        except Exception as e:
            return jsonify({'error': f'Error calculating MBTI type: {str(e)}'}), 400

        personality = mbti_data['personalities'].get(mbti_type, {})
        if not personality:
            return jsonify({'error': f'Invalid MBTI type: {mbti_type}'}), 400

        # Generate or retrieve cached cards
        try:
            cards = user_manager.get_user_cards(wallet_address)
            if not cards:
                # Generate new cards
                major_arcana = card_generator.generate_major_arcana(mbti_type, template_id)
                minor_arcana = card_generator.generate_minor_arcana(mbti_type, template_id)
                cards = {
                    'major_arcana': major_arcana,
                    'minor_arcana': minor_arcana
                }
                # Cache the cards
                user_manager.cache_user_cards(wallet_address, cards)
        except Exception as e:
            return jsonify({'error': f'Error generating cards: {str(e)}'}), 500

        # Prepare response
        result = {
            'mbti_type': mbti_type,
            'personality': personality,
            'tarot_info': {
                'major_arcana': cards['major_arcana']['name'],
                'major_arcana_image': cards['major_arcana']['image_path'],
                'orientation': cards['major_arcana']['orientation'],
                'specific_meanings': cards['major_arcana']['meanings']
            },
            'minor_arcana': [
                {
                    'name': card['name'],
                    'image_path': card['image_path'],
                    'suite': card['suite'],
                    'orientation': card['orientation']
                }
                for card in cards['minor_arcana']
            ]
        }

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/collection/<address>', methods=['GET'])
def get_collection(address):
    """Get user's card collection"""
    try:
        cards = user_manager.get_user_cards(address)
        if not cards:
            return jsonify({'error': 'No cards found'}), 404

        return jsonify(cards)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def calculate_mbti_type(answers):
    """Calculate MBTI type based on quiz answers"""
    if not answers or len(answers) != len(questions_data['questions']):
        raise ValueError(f'Expected {len(questions_data["questions"])} answers, got {len(answers) if answers else 0}')

    scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    
    for i, answer in enumerate(answers):
        question = questions_data['questions'][i]
        if answer >= len(question['options']):
            raise ValueError(f'Invalid answer index {answer} for question {i}')
            
        option = question['options'][answer]
        for dimension, score in option['score'].items():
            scores[dimension] += score

    # Calculate each dimension based on the highest score
    mbti = ''
    mbti += 'E' if scores['E'] > scores['I'] else 'I'
    mbti += 'S' if scores['S'] > scores['N'] else 'N'
    mbti += 'T' if scores['T'] > scores['F'] else 'F'
    mbti += 'J' if scores['J'] > scores['P'] else 'P'
    
    return mbti

def main():
    """Entry point for the application"""
    app.run(debug=True)

if __name__ == '__main__':
    main()
