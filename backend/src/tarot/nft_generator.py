import json
import os
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image
from web3 import Web3
from dotenv import load_load_dotenv

class TarotNFTGenerator:
    def __init__(self):
        load_dotenv()
        self.ipfs_project_id = os.getenv('IPFS_PROJECT_ID')
        self.ipfs_project_secret = os.getenv('IPFS_PROJECT_SECRET')
        self.contract_address = os.getenv('NFT_CONTRACT_ADDRESS')
        self.web3 = Web3(Web3.HTTPProvider(os.getenv('WEB3_PROVIDER_URI')))
        
        # Load contract ABI
        with open('contracts/TarotNFT.json', 'r') as f:
            contract_json = json.load(f)
            self.contract_abi = contract_json['abi']
        
        self.contract = self.web3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )

    def generate_card_image(self, card_data, mbti_type):
        """
        Generate a unique card image based on the reading
        TODO: Implement actual image generation logic
        """
        # This is a placeholder - you'll need to implement actual image generation
        # You could use PIL to create custom card designs
        img = Image.new('RGB', (800, 1200), color='white')
        return img

    def upload_to_ipfs(self, file_path):
        """Upload a file to IPFS using Pinata"""
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        
        headers = {
            'pinata_api_key': self.ipfs_project_id,
            'pinata_secret_api_key': self.ipfs_project_secret
        }
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files, headers=headers)
            
        if response.status_code == 200:
            return f"ipfs://{response.json()['IpfsHash']}"
        else:
            raise Exception("IPFS upload failed")

    def create_metadata(self, card_data, mbti_type, image_uri):
        """Create metadata for the NFT"""
        metadata = {
            "name": f"MBTI Tarot: {card_data['card']} - {mbti_type}",
            "description": f"A unique tarot card reading connecting {card_data['card']} with MBTI type {mbti_type}",
            "image": image_uri,
            "attributes": [
                {
                    "trait_type": "Card",
                    "value": card_data['card']
                },
                {
                    "trait_type": "MBTI Type",
                    "value": mbti_type
                },
                {
                    "trait_type": "Description",
                    "value": card_data['description']
                },
                {
                    "trait_type": "Meaning",
                    "value": card_data['meaning']['upright']
                },
                {
                    "trait_type": "Reversed Meaning",
                    "value": card_data['meaning']['reversed']
                },
                {
                    "trait_type": "Generation Date",
                    "value": datetime.now().isoformat()
                }
            ]
        }
        return metadata

    async def mint_nft(self, recipient_address, card_data, mbti_type):
        """
        Generate and mint an NFT for a tarot reading
        """
        # Generate card image
        card_image = self.generate_card_image(card_data, mbti_type)
        
        # Save image temporarily
        temp_image_path = Path('temp_card.png')
        card_image.save(temp_image_path)
        
        # Upload image to IPFS
        image_uri = self.upload_to_ipfs(temp_image_path)
        
        # Create and upload metadata
        metadata = self.create_metadata(card_data, mbti_type, image_uri)
        metadata_path = Path('temp_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        metadata_uri = self.upload_to_ipfs(metadata_path)
        
        # Clean up temporary files
        temp_image_path.unlink()
        metadata_path.unlink()
        
        # Mint NFT
        tx_hash = await self.contract.functions.mintTarotCard(
            recipient_address,
            metadata_uri,
            card_data['card'],
            card_data.get('suit', 'Major Arcana'),
            False,  # isReversed
            mbti_type
        ).transact({'from': self.web3.eth.accounts[0]})
        
        # Wait for transaction to be mined
        receipt = await self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        return receipt
