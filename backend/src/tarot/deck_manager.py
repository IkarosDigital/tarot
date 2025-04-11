from pathlib import Path
import json
from typing import List, Dict, Set, Optional, Tuple
from .card_generator import TarotCardGenerator, CardSide, CardOrientation
import os
from tqdm import tqdm

class DeckTheme(Enum):
    NT_COSMIC = "cosmic"    # Technology and cosmic themes
    NF_MYSTIC = "mystic"    # Spiritual and mystical themes
    ST_MECHANICAL = "mechanical"  # Mechanical and structured themes
    SF_NATURAL = "natural"   # Natural and organic themes

@dataclass
class CardMetadata:
    name: str
    suite: str
    mbti_type: str
    theme: DeckTheme
    description: str
    meanings: Dict[str, str]  # upright and reversed meanings

class DeckManager:
    # Standard deck structure
    SUITES = ['Swords', 'Cups', 'Sceptres', 'Pentacles']
    COURTS = ['Page', 'Knight', 'Queen', 'King']
    NUMBERS = ['Ace', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten']
    MAJOR_ARCANA = [
        'The Fool', 'The Magician', 'The High Priestess', 'The Empress', 'The Emperor',
        'The Hierophant', 'The Lovers', 'The Chariot', 'Strength', 'The Hermit',
        'Wheel of Fortune', 'Justice', 'The Hanged Man', 'Death', 'Temperance',
        'The Devil', 'The Tower', 'The Star', 'The Moon', 'The Sun',
        'Judgement', 'The World'
    ]
    
    # MBTI type groupings
    MBTI_GROUPS = {
        'NT': ['INTJ', 'INTP', 'ENTJ', 'ENTP'],
        'NF': ['INFJ', 'INFP', 'ENFJ', 'ENFP'],
        'ST': ['ISTJ', 'ISTP', 'ESTJ', 'ESTP'],
        'SF': ['ISFJ', 'ISFP', 'ESFJ', 'ESFP']
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize deck manager with optional API key."""
        self.generator = TarotCardGenerator() if api_key else None
        self.base_path = Path("generated_cards")
        self.base_path.mkdir(exist_ok=True)
        
        # Load or create deck metadata
        self.metadata_file = self.base_path / "deck_metadata.json"
        self.metadata = self._load_metadata()
        
    def _load_metadata(self) -> Dict:
        """Load or create deck metadata."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {'decks': {}}
    
    def _save_metadata(self):
        """Save deck metadata."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def get_deck_status(self, mbti_type: str) -> Dict:
        """Get status of deck completion for an MBTI type."""
        deck_path = self.base_path / mbti_type
        expected_cards = self._get_expected_cards()
        existing_cards = set()
        
        if deck_path.exists():
            for card_file in deck_path.glob("*.png"):
                card_name = card_file.stem.replace(f"{mbti_type}_", "").replace("_", " ")
                existing_cards.add(card_name)
        
        missing_cards = expected_cards - existing_cards
        extra_cards = existing_cards - expected_cards
        
        return {
            'total_expected': len(expected_cards),
            'total_existing': len(existing_cards),
            'completion_percentage': round(len(existing_cards) / len(expected_cards) * 100, 2),
            'missing_cards': sorted(list(missing_cards)),
            'extra_cards': sorted(list(extra_cards)),
            'is_complete': len(missing_cards) == 0
        }
    
    def _get_expected_cards(self) -> Set[str]:
        """Get set of all expected card names in a complete deck."""
        expected_cards = set(self.MAJOR_ARCANA)
        
        # Add minor arcana
        for suite in self.SUITES:
            # Add number cards
            for number in self.NUMBERS:
                expected_cards.add(f"{number} of {suite}")
            # Add court cards
            for court in self.COURTS:
                expected_cards.add(f"{court} of {suite}")
        
        return expected_cards
    
    def generate_complete_deck(self, mbti_type: str, overwrite: bool = False) -> Dict:
        """Generate a complete deck for an MBTI type."""
        if not self.generator:
            raise ValueError("Card generator not initialized. API key required.")
        
        # Validate MBTI type
        mbti_type = mbti_type.upper()
        if not any(mbti_type in group for group in self.MBTI_GROUPS.values()):
            raise ValueError(f"Invalid MBTI type: {mbti_type}")
        
        deck_path = self.base_path / mbti_type
        deck_path.mkdir(exist_ok=True)
        
        # Get current status
        status = self.get_deck_status(mbti_type)
        cards_to_generate = status['missing_cards'] if not overwrite else self._get_expected_cards()
        
        if not cards_to_generate and not overwrite:
            return {'message': 'Deck is already complete!', 'status': status}
        
        # Generate back design first
        print(f"\nGenerating back design for {mbti_type}...")
        back_image = self.generator.generate_card_art(
            mbti_type=mbti_type,
            card_name="Back",
            suite="All",
            side=CardSide.BACK
        )
        back_path = deck_path / f"{mbti_type}_back.png"
        back_image.save(back_path, "PNG", quality=100)
        
        # Generate all missing cards
        print(f"\nGenerating {len(cards_to_generate)} cards for {mbti_type}...")
        generated_cards = []
        errors = []
        
        for card_name in tqdm(cards_to_generate):
            try:
                # Determine suite (Major Arcana has no suite)
                suite = next((s for s in self.SUITES if s in card_name), "Major")
                
                # Generate card
                card_image = self.generator.generate_card_art(
                    mbti_type=mbti_type,
                    card_name=card_name,
                    suite=suite,
                    side=CardSide.FRONT,
                    orientation=CardOrientation.UPRIGHT
                )
                
                # Save card
                card_filename = f"{mbti_type}_{card_name.replace(' ', '_')}.png"
                card_path = deck_path / card_filename
                card_image.save(card_path, "PNG", quality=100)
                generated_cards.append(card_name)
                
            except Exception as e:
                errors.append({'card': card_name, 'error': str(e)})
        
        # Update metadata
        self.metadata['decks'][mbti_type] = {
            'last_updated': str(Path.ctime(deck_path)),
            'card_count': len(list(deck_path.glob("*.png"))),
            'status': self.get_deck_status(mbti_type)
        }
        self._save_metadata()
        
        return {
            'generated_cards': generated_cards,
            'errors': errors,
            'status': self.get_deck_status(mbti_type)
        }
    
    def get_themed_deck(self, mbti_type: str) -> Dict:
        """Get information about a themed deck."""
        mbti_type = mbti_type.upper()
        deck_path = self.base_path / mbti_type
        
        if not deck_path.exists():
            raise ValueError(f"No deck found for {mbti_type}")
        
        status = self.get_deck_status(mbti_type)
        return {
            'deck_path': str(deck_path),
            'status': status,
            'metadata': self.metadata['decks'].get(mbti_type, {})
        }
    
    def get_card_path(self, mbti_type: str, card_name: str) -> Path:
        """Get path to a specific card."""
        mbti_type = mbti_type.upper()
        deck_path = self.base_path / mbti_type
        card_filename = f"{mbti_type}_{card_name.replace(' ', '_')}.png"
        card_path = deck_path / card_filename
        
        if not card_path.exists():
            raise ValueError(f"Card not found: {card_name} for {mbti_type}")
        
        return card_path
    
    def get_rws_symbolism(self, card_name: str) -> Dict:
        """Get traditional RWS symbolism for a card."""
        # This could be expanded with more detailed symbolism
        symbolism = {
            # Major Arcana examples
            'The Fool': {
                'symbols': ['white dog', 'cliff edge', 'knapsack', 'white rose'],
                'colors': ['yellow', 'white', 'red'],
                'elements': ['air', 'earth'],
                'composition': 'figure stepping off cliff, dog at heels'
            },
            # Minor Arcana examples
            'Ace of Swords': {
                'symbols': ['crown', 'laurel wreath', 'mountain peaks'],
                'colors': ['silver', 'gold', 'blue'],
                'elements': ['air', 'metal'],
                'composition': 'sword pointing upward through crown'
            }
            # Add more cards as needed
        }
        return symbolism.get(card_name, {
            'symbols': [],
            'colors': [],
            'elements': [],
            'composition': 'traditional tarot symbolism'
        })
