from tarot.deck_manager import DeckManager
import os
from dotenv import load_dotenv

load_dotenv()

def test_deck_manager():
    try:
        # Initialize deck manager with optional API key
        api_key = os.getenv('STABILITY_API_KEY')
        deck_manager = DeckManager(api_key)

        # Test for an INTJ user
        mbti_type = "INTJ"
        
        print(f"\nGetting themed deck for {mbti_type}...")
        try:
            deck_paths = deck_manager.get_themed_deck(mbti_type)
            print(f"Found {len(deck_paths)} cards in themed deck")
        except ValueError as e:
            print(f"Note: {str(e)}")
            print("This is expected if you haven't pre-generated the themed deck yet.")

        if api_key:
            print(f"\nGenerating special cards for {mbti_type}...")
            try:
                special_cards = deck_manager.generate_special_cards(mbti_type, count=2)
                print(f"Generated {len(special_cards)} special cards:")
                for path in special_cards:
                    print(f"- {path}")
            except Exception as e:
                print(f"Error generating special cards: {str(e)}")
        else:
            print("\nSkipping special card generation (no API key provided)")

    except Exception as e:
        print(f"Error in deck manager test: {str(e)}")

if __name__ == "__main__":
    test_deck_manager()
