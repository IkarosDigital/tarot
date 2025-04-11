from flask import Flask, request, jsonify, send_from_directory
from tarot.card_generator import TarotCardGenerator
from tarot.user_manager import UserManager
from web3.auto import w3
import json
import os

app = Flask(__name__, static_folder='.')

# Load MBTI data
with open('data/mbti_personalities.json', 'r') as f:
    mbti_data = json.load(f)

with open('data/questions.json', 'r') as f:
    questions_data = json.load(f)

# Initialize managers
card_generator = TarotCardGenerator()
user_manager = UserManager()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Return personality quiz questions"""
    return jsonify(questions_data)

@app.route('/api/verify-wallet', methods=['POST'])
def verify_wallet():
    """Verify wallet signature"""
    data = request.json
    address = data.get('address')
    signature = data.get('signature')
    message = data.get('message')

    try:
        # Verify the signature
        recovered_address = w3.eth.account.recover_message(
            message,
            signature=signature
        )
        
        if recovered_address.lower() != address.lower():
            return jsonify({'error': 'Invalid signature'}), 401

        # Register or update user
        user_manager.register_user(address)
        
        return jsonify({'verified': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/calculate-result', methods=['POST'])
def calculate_result():
    """Calculate MBTI result and generate tarot cards"""
    data = request.json
    answers = data.get('answers')
    wallet_address = data.get('walletAddress')
    template_id = data.get('template_id', 'classic')

    try:
        # Calculate MBTI type
        mbti_type = calculate_mbti_type(answers)
        personality = mbti_data['personalities'].get(mbti_type, {})

        # Generate cards
        cards = None
        if wallet_address:
            # If wallet is connected, check cached cards first
            cards = user_manager.get_user_cards(wallet_address)
        
        if not cards:
            # Generate new cards
            major_arcana = card_generator.generate_major_arcana(mbti_type, template_id)
            minor_arcana = card_generator.generate_minor_arcana(mbti_type, template_id)
            cards = {
                'major_arcana': major_arcana,
                'minor_arcana': minor_arcana
            }
            
            # Cache cards if wallet is connected
            if wallet_address:
                user_manager.cache_user_cards(wallet_address, cards)

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
            'minor_arcana': [{
                'name': card['name'],
                'image_path': card['image_path'],
                'orientation': card['orientation'],
                'meanings': card['meanings']
            } for card in cards['minor_arcana']],
            'can_mint': bool(wallet_address)
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

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
    scores = {'E': 0, 'I': 0, 'S': 0, 'N': 0, 'T': 0, 'F': 0, 'J': 0, 'P': 0}
    
    for i, answer in enumerate(answers):
        question = questions_data['questions'][i]
        option = question['options'][answer]
        for dimension, score in option['score'].items():
            scores[dimension] += score

    mbti = ''
    mbti += 'E' if scores['E'] > scores['I'] else 'I'
    mbti += 'S' if scores['S'] > scores['N'] else 'N'
    mbti += 'T' if scores['T'] > scores['F'] else 'F'
    mbti += 'J' if scores['J'] > scores['P'] else 'P'
    
    return mbti

if __name__ == '__main__':
    app.run(debug=True)
