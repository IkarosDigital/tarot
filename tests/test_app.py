import pytest
from tarot.app import app, calculate_mbti_type, w3
from tarot.card_generator import TarotCardGenerator
from tarot.user_manager import UserManager
import json
from unittest.mock import patch, MagicMock
from web3 import Web3
import eth_account
from pathlib import Path

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_card_generator():
    with patch('tarot.app.card_generator') as mock:
        mock.generate_major_arcana.return_value = {
            'name': 'The Hermit',
            'image_path': '/images/cards/hermit.png',
            'orientation': 'Upright',
            'meanings': ['Introspection', 'Wisdom']
        }
        mock.generate_minor_arcana.return_value = [
            {
                'name': 'Two of Swords',
                'image_path': '/images/cards/two_swords.png',
                'suite': 'Swords',
                'orientation': 'Upright'
            }
        ]
        yield mock

@pytest.fixture
def mock_user_manager():
    with patch('tarot.app.user_manager') as mock:
        mock.verify_user.return_value = True
        mock.get_user_cards.return_value = None
        yield mock

@pytest.fixture(autouse=True)
def mock_data():
    mock_mbti = {
        'personalities': {
            'INTJ': {
                'name': 'Architect',
                'description': 'Test description'
            },
            'ESFP': {
                'name': 'Entertainer',
                'description': 'Test description'
            }
        }
    }
    
    mock_questions = {
        'questions': [
            {
                'question': f'Test Question {i}',
                'options': [
                    {
                        'text': 'Option 1',
                        'score': {'I': 2, 'N': 2, 'T': 2, 'J': 2, 'E': 0, 'S': 0, 'F': 0, 'P': 0}
                    },
                    {
                        'text': 'Option 2',
                        'score': {'E': 2, 'S': 2, 'F': 2, 'P': 2, 'I': 0, 'N': 0, 'T': 0, 'J': 0}
                    }
                ]
            }
            for i in range(20)  # Create 20 questions
        ]
    }
    
    with patch('tarot.app.mbti_data', mock_mbti), \
         patch('tarot.app.questions_data', mock_questions):
        yield

def test_serve_index(client):
    """Test serving index.html"""
    response = client.get('/')
    assert response.status_code == 200

def test_get_questions(client):
    """Test getting quiz questions"""
    response = client.get('/api/questions')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'questions' in data

def test_verify_wallet_valid_signature(client):
    """Test wallet verification with valid signature"""
    # Create a test wallet and sign a message
    account = w3.eth.account.create()
    message = "Test message"
    message_hash = eth_account.messages.encode_defunct(text=message)
    signed = account.sign_message(message_hash)
    
    response = client.post('/api/verify-wallet', json={
        'address': account.address,
        'signature': signed.signature.hex(),
        'message': message
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['verified'] is True

def test_verify_wallet_invalid_signature(client):
    """Test wallet verification with invalid signature"""
    response = client.post('/api/verify-wallet', json={
        'address': '0x1234567890123456789012345678901234567890',
        'signature': '0xinvalid',
        'message': 'Test message'
    })

    assert response.status_code == 400

def test_calculate_result_success(client, mock_card_generator, mock_user_manager):
    """Test successful result calculation"""
    # Mock answers that would result in INTJ
    answers = [0] * 20  # All answers favor I, N, T, J (Option 1)
    
    response = client.post('/api/calculate-result', json={
        'answers': answers,
        'walletAddress': '0x1234567890123456789012345678901234567890',
        'walletSignature': '0xvalid',
        'template_id': 'classic'
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'mbti_type' in data
    assert data['mbti_type'] == 'INTJ'
    assert 'tarot_info' in data
    assert 'minor_arcana' in data

def test_calculate_result_invalid_wallet(client, mock_user_manager):
    """Test result calculation with invalid wallet"""
    mock_user_manager.verify_user.return_value = False
    
    response = client.post('/api/calculate-result', json={
        'answers': [0] * 20,
        'walletAddress': '0x1234567890123456789012345678901234567890',
        'walletSignature': '0xinvalid',
        'template_id': 'classic'
    })

    assert response.status_code == 401

def test_get_collection_success(client, mock_user_manager):
    """Test getting user's card collection"""
    mock_user_manager.get_user_cards.return_value = {
        'major_arcana': {
            'name': 'The Hermit',
            'image_path': '/images/cards/hermit.png'
        },
        'minor_arcana': []
    }

    response = client.get('/api/collection/0x1234567890123456789012345678901234567890')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'major_arcana' in data

def test_get_collection_not_found(client, mock_user_manager):
    """Test getting non-existent collection"""
    mock_user_manager.get_user_cards.return_value = None

    response = client.get('/api/collection/0x1234567890123456789012345678901234567890')
    assert response.status_code == 404

def test_calculate_mbti_type():
    """Test MBTI type calculation"""
    # Test INTJ result (all answers favor I, N, T, J)
    intj_answers = [0] * 20  # Option 1 favors INTJ
    assert calculate_mbti_type(intj_answers) == 'INTJ'
    
    # Test ESFP result (all answers favor E, S, F, P)
    esfp_answers = [1] * 20  # Option 2 favors ESFP
    assert calculate_mbti_type(esfp_answers) == 'ESFP'
