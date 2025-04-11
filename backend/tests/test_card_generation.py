from tarot.card_generator import TarotCardGenerator, CardSide, CardOrientation
import os

def test_generate_card():
    try:
        generator = TarotCardGenerator()
        
        # Test parameters
        mbti_type = "INTJ"  # Focus on one type for testing
        cards = [
            # Test different number-suite combinations
            ("Ace of Swords", "Swords"),     # Air element, singular focus
            ("Two of Cups", "Cups"),         # Water element, duality
            ("Three of Sceptres", "Sceptres"), # Fire element, expansion
            ("Four of Pentacles", "Pentacles"), # Earth element, stability
            
            # Test court cards with RWS symbolism
            ("King of Swords", "Swords"),    # Intellectual authority
            ("Queen of Cups", "Cups"),       # Emotional wisdom
            
            # Test Major Arcana
            ("The Fool", "Major"),           # Pure potential
            ("The Magician", "Major")        # Manifestation
        ]
        
        # Create output directory
        os.makedirs("generated_cards", exist_ok=True)
        
        # Generate back design first (shared for the deck)
        print("\nGenerating themed back design...")
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
        for card_name, suite in cards:
            print(f"\nGenerating {card_name}...")
            
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
            
            print(f"Note: For reversed orientation, rotate the front image 180 degrees.")
        
    except Exception as e:
        print(f"Error generating cards: {str(e)}")

if __name__ == "__main__":
    test_generate_card()
