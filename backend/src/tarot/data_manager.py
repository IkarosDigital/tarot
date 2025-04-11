import json
from pathlib import Path
from typing import Dict, List, Optional

class TarotDataManager:
    def __init__(self):
        self.data_dir = Path("data")
        self._load_data()
    
    def _load_data(self):
        """Load all data files."""
        # Load keys (major arcana)
        with open(self.data_dir / "keys.json", 'r') as f:
            self.keys = json.load(f)['keys']
        
        # Load suites
        with open(self.data_dir / "suites.json", 'r') as f:
            self.suites = json.load(f)['suits']
        
        # Load personality constructs
        with open(self.data_dir / "personality_construct.json", 'r') as f:
            self.personality_constructs = json.load(f)
        
        # Load MBTI-Tarot correlations
        with open(self.data_dir / "mbti_tarot.json", 'r') as f:
            self.mbti_tarot = json.load(f)['mbti_tarot_correlation']
    
    def get_key_symbolism(self, card_name: str) -> Dict:
        """Get symbolism for a major arcana card."""
        for key in self.keys:
            if key['name'].lower() == card_name.lower():
                return key
        return None
    
    def get_suite_info(self, suite_name: str) -> Dict:
        """Get information about a suite."""
        for suite in self.suites:
            if suite['name'].lower() == suite_name.lower():
                return suite
        return None
    
    def get_personality_construct(self, mbti_type: str) -> Dict:
        """Get personality construct for MBTI type."""
        for construct in self.personality_constructs:
            if construct['construct_name'].startswith(mbti_type):
                return construct
        return None
    
    def get_mbti_card_correlation(self, mbti_type: str) -> Dict:
        """Get tarot card correlation for MBTI type."""
        correlations = self.mbti_tarot.get('court_card_correlations', [])
        for correlation in correlations:
            if correlation['mbti'] == mbti_type:
                return correlation
        return None
    
    def get_cognitive_suite(self, function: str) -> str:
        """Get suite associated with cognitive function."""
        return self.mbti_tarot['mbti_basis']['suits_association'].get(function.lower())
    
    def get_color_scheme(self, mbti_type: str) -> Dict[str, List[str]]:
        """Get color scheme based on MBTI type."""
        # Define color schemes based on cognitive functions
        color_schemes = {
            'NT': {
                'primary': ['deep purple', 'midnight blue', 'silver'],
                'accent': ['electric blue', 'metallic gold'],
                'background': ['dark indigo', 'starry black']
            },
            'NF': {
                'primary': ['violet', 'rose gold', 'pearl'],
                'accent': ['sunset orange', 'mystic purple'],
                'background': ['deep magenta', 'celestial blue']
            },
            'ST': {
                'primary': ['steel gray', 'bronze', 'obsidian'],
                'accent': ['copper', 'titanium'],
                'background': ['charcoal', 'gunmetal']
            },
            'SF': {
                'primary': ['earth brown', 'forest green', 'terracotta'],
                'accent': ['autumn gold', 'sage green'],
                'background': ['warm brown', 'deep green']
            }
        }
        return color_schemes.get(mbti_type[:2], color_schemes['NT'])
    
    def get_geometric_pattern(self, mbti_type: str, number: int) -> Dict[str, str]:
        """Get geometric pattern based on MBTI type and card number."""
        # Base patterns enhanced by MBTI preferences
        base_patterns = {
            'NT': {
                'style': 'crystalline',
                'complexity': 'high',
                'elements': ['fractals', 'platonic solids', 'sacred geometry']
            },
            'NF': {
                'style': 'organic',
                'complexity': 'flowing',
                'elements': ['spirals', 'waves', 'natural forms']
            },
            'ST': {
                'style': 'mechanical',
                'complexity': 'precise',
                'elements': ['gears', 'circuits', 'blueprints']
            },
            'SF': {
                'style': 'natural',
                'complexity': 'balanced',
                'elements': ['leaves', 'flowers', 'branches']
            }
        }
        
        pattern = base_patterns.get(mbti_type[:2], base_patterns['NT']).copy()
        
        # Add number-specific geometry
        if number:
            pattern['number_geometry'] = {
                1: 'point of origin',
                2: 'vesica piscis',
                3: 'triangle',
                4: 'square',
                5: 'pentagram',
                6: 'hexagon',
                7: 'septagram',
                8: 'octagon',
                9: 'enneagram',
                10: 'decagram'
            }.get(number, 'circle')
        
        return pattern
    
    def get_card_prompt(self, mbti_type: str, card_name: str, suite: str) -> Dict[str, str]:
        """Generate comprehensive prompt for card generation."""
        personality = self.get_personality_construct(mbti_type)
        mbti_card = self.get_mbti_card_correlation(mbti_type)
        suite_info = self.get_suite_info(suite) if suite != "Major" else None
        key_info = self.get_key_symbolism(card_name) if suite == "Major" else None
        
        # Get color scheme and patterns
        colors = self.get_color_scheme(mbti_type)
        number = self._extract_number(card_name)
        geometry = self.get_geometric_pattern(mbti_type, number)
        
        prompt = {
            'personality_elements': {
                'traits': personality['key_traits'] if personality else [],
                'strengths': personality['strengths'] if personality else [],
                'style': f"{geometry['style']} with {geometry['complexity']} complexity"
            },
            'colors': {
                'primary': colors['primary'],
                'accent': colors['accent'],
                'background': colors['background']
            },
            'symbolism': {
                'geometric': geometry['elements'] + [geometry.get('number_geometry', '')],
                'suite': suite_info['symbolism'] if suite_info else {},
                'key': key_info['symbolism'] if key_info else {},
                'mbti': mbti_card['description'] if mbti_card else ''
            }
        }
        
        return prompt
    
    def _extract_number(self, card_name: str) -> Optional[int]:
        """Extract number from card name."""
        number_words = {
            'ace': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
        }
        
        words = card_name.lower().split()
        for word in words:
            if word in number_words:
                return number_words[word]
        return None
