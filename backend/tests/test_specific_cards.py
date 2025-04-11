from tarot.card_generator import TarotCardGenerator, CardSide, CardOrientation
import os

def test_specific_cards():
    try:
        generator = TarotCardGenerator()
        
        # Test specific cards that need improvement
        test_cases = [
            {
                'mbti_type': 'INTJ',
                'cards': [
                    ('The Magician', 'Major'),      # Test enhanced Magician imagery
                    ('The Sun', 'Major'),           # Test enhanced Sun imagery
                    ('Ace of Wands', 'Wands'),      # Test enhanced Wands imagery
                    ('Two of Pentacles', 'Pentacles')  # Test enhanced Pentacles imagery
                ]
            },
            {
                'mbti_type': 'ENFP',
                'cards': [
                    ('The Star', 'Major'),          # Test enhanced Star imagery
                    ('Three of Wands', 'Wands'),    # Test enhanced Wands imagery
                    ('Ace of Cups', 'Cups')         # Test enhanced Cups imagery
                ]
            }
        ]
        
        # Create output directory
        os.makedirs("generated_cards", exist_ok=True)
        
        # Generate cards with enhanced prompts
        for case in test_cases:
            mbti_type = case['mbti_type']
            print(f"\n{'='*50}")
            print(f"Generating cards for {mbti_type}")
            print(f"{'='*50}")
            
            for card_name, suite in case['cards']:
                print(f"\nGenerating {card_name}...")
                
                # Generate card with specific imagery
                image = generator.generate_card_art(
                    mbti_type=mbti_type,
                    card_name=card_name,
                    suite=suite,
                    side=CardSide.FRONT,
                    orientation=CardOrientation.UPRIGHT,
                    template_id='classic'  # Use classic template for better visibility of imagery
                )
                
                # Save the image
                output_path = f"generated_cards/{mbti_type}_{card_name.replace(' ', '_')}_enhanced.png"
                image.save(output_path, "PNG", quality=100)
                print(f"Generated {card_name}! Saved to: {output_path}")
        
    except Exception as e:
        print(f"Error in test: {str(e)}")

if __name__ == "__main__":
    test_specific_cards()
