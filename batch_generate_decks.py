from tarot.deck_manager import DeckManager
import os
from dotenv import load_dotenv
import json
from pathlib import Path

def generate_decks():
    load_dotenv()
    api_key = os.getenv('STABILITY_API_KEY')
    
    if not api_key:
        print("Error: STABILITY_API_KEY not found in environment variables")
        return
    
    deck_manager = DeckManager(api_key)
    
    # Example MBTI types to generate (one from each group)
    mbti_types = ['INTJ', 'ENFP', 'ISTJ', 'ISFP']
    
    results = {}
    for mbti_type in mbti_types:
        print(f"\n{'='*50}")
        print(f"Processing deck for {mbti_type}")
        print(f"{'='*50}")
        
        # Check current status
        status = deck_manager.get_deck_status(mbti_type)
        print(f"\nCurrent deck status for {mbti_type}:")
        print(f"Total cards expected: {status['total_expected']}")
        print(f"Total cards existing: {status['total_existing']}")
        print(f"Completion: {status['completion_percentage']}%")
        
        if status['missing_cards']:
            print(f"\nMissing cards ({len(status['missing_cards'])}):")
            for card in status['missing_cards'][:5]:  # Show first 5
                print(f"- {card}")
            if len(status['missing_cards']) > 5:
                print(f"... and {len(status['missing_cards']) - 5} more")
        
        if status['extra_cards']:
            print(f"\nExtra cards found ({len(status['extra_cards'])}):")
            for card in status['extra_cards']:
                print(f"- {card}")
        
        # Generate missing cards
        if not status['is_complete']:
            print(f"\nGenerating missing cards for {mbti_type}...")
            result = deck_manager.generate_complete_deck(mbti_type)
            
            if result['errors']:
                print("\nErrors encountered:")
                for error in result['errors']:
                    print(f"- {error['card']}: {error['error']}")
            
            # Update status
            status = result['status']
            print(f"\nUpdated completion: {status['completion_percentage']}%")
        else:
            print(f"\nDeck for {mbti_type} is already complete!")
        
        results[mbti_type] = status
    
    # Save summary report
    report = {
        'timestamp': str(Path.ctime(Path.cwd())),
        'results': results
    }
    
    with open('deck_generation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\nDeck generation complete! Summary:")
    for mbti_type, status in results.items():
        print(f"\n{mbti_type}: {status['completion_percentage']}% complete")
        if not status['is_complete']:
            print(f"Missing: {len(status['missing_cards'])} cards")

if __name__ == "__main__":
    generate_decks()
