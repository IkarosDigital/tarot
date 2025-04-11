from tarot.card_generator import TarotCardGenerator, CardSide, CardOrientation
import os

def test_user_cards():
    try:
        generator = TarotCardGenerator()
        
        # Simulate a user's wallet address
        test_wallet = "0x123456789abcdef"
        
        # Test different templates with the same card
        templates = ['classic', 'modern', 'ethereal']
        card_info = {
            'mbti_type': 'INTJ',
            'card_name': 'The Magician',
            'suite': 'Major'
        }
        
        print("\nGenerating initial card with different templates...")
        for template in templates:
            print(f"\nTemplate: {template}")
            image = generator.generate_card_art(
                mbti_type=card_info['mbti_type'],
                card_name=card_info['card_name'],
                suite=card_info['suite'],
                side=CardSide.FRONT,
                wallet_address=test_wallet,
                template_id=template
            )
            print(f"Generated card with {template} template")
        
        print("\nTesting card regeneration...")
        # Get cached card ID
        cached_cards = generator.user_manager.get_user_cards(test_wallet)
        if cached_cards:
            card_id = next(iter(cached_cards.keys()))
            print(f"Regenerating card {card_id}")
            
            # Try regenerating with a different template
            new_image = generator.regenerate_card(
                test_wallet,
                card_id,
                template_id='modern'
            )
            print("Successfully regenerated card with new template")
        
        print("\nTesting cache retrieval...")
        # Try getting the card from cache
        cached_image = generator.generate_card_art(
            mbti_type=card_info['mbti_type'],
            card_name=card_info['card_name'],
            suite=card_info['suite'],
            side=CardSide.FRONT,
            wallet_address=test_wallet,
            force_regenerate=False
        )
        print("Successfully retrieved card from cache")
        
    except Exception as e:
        print(f"Error in test: {str(e)}")

if __name__ == "__main__":
    test_user_cards()
