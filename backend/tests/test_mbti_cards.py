from tarot.card_generator import TarotCardGenerator, CardSide, CardOrientation
from tarot.data_manager import TarotDataManager
import os
from pprint import pprint

def test_mbti_cards():
    try:
        generator = TarotCardGenerator()
        data_manager = TarotDataManager()
        
        # Test different MBTI types (one from each group)
        test_cases = [
            {
                'mbti': 'INTJ',
                'cards': [
                    ('The Magician', 'Major'),      # Represents mastery and intellect
                    ('King of Swords', 'Swords'),   # Strategic leadership
                    ('Two of Pentacles', 'Pentacles')  # Balance and adaptation
                ]
            },
            {
                'mbti': 'ENFP',
                'cards': [
                    ('The Star', 'Major'),          # Hope and inspiration
                    ('Knight of Wands', 'Wands'),   # Creative passion
                    ('Three of Cups', 'Cups')       # Emotional connection
                ]
            },
            {
                'mbti': 'ISTJ',
                'cards': [
                    ('Justice', 'Major'),           # Order and structure
                    ('King of Pentacles', 'Pentacles'),  # Practical mastery
                    ('Four of Swords', 'Swords')    # Logical rest
                ]
            },
            {
                'mbti': 'ESFP',
                'cards': [
                    ('The Sun', 'Major'),           # Joy and vitality
                    ('Knight of Cups', 'Cups'),     # Emotional adventure
                    ('Six of Wands', 'Wands')       # Social victory
                ]
            }
        ]
        
        # Create output directory
        os.makedirs("generated_cards", exist_ok=True)
        
        # Generate cards for each MBTI type
        for case in test_cases:
            mbti_type = case['mbti']
            print(f"\n{'='*50}")
            print(f"Generating cards for {mbti_type}")
            print(f"{'='*50}")
            
            # Generate back design first
            print(f"\nGenerating themed back design...")
            back_image = generator.generate_card_art(
                mbti_type=mbti_type,
                card_name="Back",
                suite="All",
                side=CardSide.BACK
            )
            
            back_path = f"generated_cards/{mbti_type}_back.png"
            back_image.save(back_path, "PNG", quality=100)
            print(f"Generated back design! Saved to: {back_path}")
            
            # Generate front designs
            for card_name, suite in case['cards']:
                print(f"\nGenerating {card_name}...")
                
                # Get detailed prompt information
                prompt_info = data_manager.get_card_prompt(mbti_type, card_name, suite)
                print("\nPrompt details:")
                pprint(prompt_info)
                
                # Generate front
                front_image = generator.generate_card_art(
                    mbti_type=mbti_type,
                    card_name=card_name,
                    suite=suite,
                    side=CardSide.FRONT,
                    orientation=CardOrientation.UPRIGHT
                )
                
                # Save front image
                front_path = f"generated_cards/{mbti_type}_{card_name.replace(' ', '_')}.png"
                front_image.save(front_path, "PNG", quality=100)
                print(f"Generated {card_name}! Saved to: {front_path}")
        
    except Exception as e:
        print(f"Error generating cards: {str(e)}")

if __name__ == "__main__":
    test_mbti_cards()
