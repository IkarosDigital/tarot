from typing import Dict, Optional, List
import json
from pathlib import Path
import os
from web3 import Web3
from eth_account.messages import encode_defunct
import time

class UserManager:
    def __init__(self):
        self.cache_dir = Path("cache/users")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.web3 = Web3()
        self._load_cached_users()
    
    def _load_cached_users(self):
        """Load cached user data."""
        self.users = {}
        if (self.cache_dir / "users.json").exists():
            with open(self.cache_dir / "users.json", 'r') as f:
                self.users = json.load(f)
    
    def _save_cached_users(self):
        """Save user data to cache."""
        with open(self.cache_dir / "users.json", 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def verify_wallet_signature(self, address: str, signature: str, message: str) -> bool:
        """Verify a wallet signature."""
        try:
            message_hash = encode_defunct(text=message)
            signer = self.web3.eth.account.recover_message(message_hash, signature=signature)
            return signer.lower() == address.lower()
        except Exception:
            return False
    
    def get_user_cards(self, wallet_address: str) -> Dict:
        """Get cached cards for a user."""
        return self.users.get(wallet_address, {}).get('cards', {})
    
    def cache_user_card(self, wallet_address: str, card_data: Dict):
        """Cache a card for a user."""
        if wallet_address not in self.users:
            self.users[wallet_address] = {'cards': {}}
        
        card_id = f"{card_data['name']}_{int(time.time())}"
        self.users[wallet_address]['cards'][card_id] = {
            'data': card_data,
            'timestamp': time.time(),
            'status': 'draft'  # draft, final, minted
        }
        self._save_cached_users()
        return card_id
    
    def update_card_status(self, wallet_address: str, card_id: str, status: str):
        """Update the status of a cached card."""
        if wallet_address in self.users and card_id in self.users[wallet_address]['cards']:
            self.users[wallet_address]['cards'][card_id]['status'] = status
            self._save_cached_users()
    
    def get_card_template(self, template_id: str) -> Dict:
        """Get a card template by ID."""
        templates = {
            'classic': {
                'border': {
                    'style': 'ornate',
                    'color': 'gold',
                    'width': 20
                },
                'corners': 'rounded',
                'background': 'parchment'
            },
            'modern': {
                'border': {
                    'style': 'minimal',
                    'color': 'silver',
                    'width': 10
                },
                'corners': 'sharp',
                'background': 'gradient'
            },
            'ethereal': {
                'border': {
                    'style': 'flowing',
                    'color': 'iridescent',
                    'width': 15
                },
                'corners': 'flowing',
                'background': 'cosmic'
            }
        }
        return templates.get(template_id, templates['classic'])
    
    def track_nft_transfer(self, wallet_address: str, new_wallet: str, token_id: str):
        """Track NFT transfer between wallets."""
        if wallet_address in self.users:
            # Find cards associated with this token
            for card_id, card_data in self.users[wallet_address]['cards'].items():
                if card_data.get('token_id') == token_id:
                    # Create or update new wallet's data
                    if new_wallet not in self.users:
                        self.users[new_wallet] = {'cards': {}}
                    
                    # Transfer card data
                    self.users[new_wallet]['cards'][card_id] = card_data
                    del self.users[wallet_address]['cards'][card_id]
                    self._save_cached_users()
                    break
