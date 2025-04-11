from typing import Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import os
import base64
from dotenv import load_dotenv
from enum import Enum
import time
from .data_manager import TarotDataManager
from .user_manager import UserManager
from .template_manager import TemplateManager
import logging
from stability_sdk import StabilityInference
from stability_sdk.interfaces.gooseai.generation.generation_pb2 import generation
from dataclasses import dataclass

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CardSide(Enum):
    FRONT = "front"
    BACK = "back"

class CardOrientation(Enum):
    UPRIGHT = "upright"
    REVERSED = "reversed"

class CardGenerationError(Exception):
    """Base exception for card generation errors"""
    def __init__(self, message: str, error_code: str, is_retryable: bool = True):
        self.message = message
        self.error_code = error_code
        self.is_retryable = is_retryable
        super().__init__(self.message)

class StabilityAIError(CardGenerationError):
    """Stability AI specific errors"""
    pass

class ImageProcessingError(CardGenerationError):
    """Image processing related errors"""
    pass

class ErrorCode(Enum):
    STABILITY_API_ERROR = "STABILITY_API_ERROR"
    INVALID_API_KEY = "INVALID_API_KEY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    IMAGE_PROCESSING_ERROR = "IMAGE_PROCESSING_ERROR"
    INVALID_PROMPT = "INVALID_PROMPT"
    STORAGE_ERROR = "STORAGE_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

@dataclass
class CardGenerationResult:
    """Result of card generation process"""
    image_path: str
    success: bool
    error: Optional[CardGenerationError] = None
    metadata: Optional[Dict] = None

class TarotCardGenerator:
    # Standard tarot card dimensions (ratio preserved)
    CARD_WIDTH = 768
    CARD_HEIGHT = 1344
    
    # Border and margin settings
    BORDER_WIDTH = 36
    MARGIN = 48
    TEXT_AREA_HEIGHT = 160
    
    def __init__(self):
        self.data_manager = TarotDataManager()
        self.user_manager = UserManager()
        self.template_manager = TemplateManager()
        self.api_key = os.getenv('STABILITY_API_KEY')
        self.api_host = 'https://api.stability.ai'
        if not self.api_key:
            raise ValueError("STABILITY_API_KEY not found in environment variables")
        
        # Load or create card frame assets
        self.frame = self._create_card_frame()
        self.text_bg = self._create_text_background()
        
        # Initialize fonts
        self._init_fonts()
        
        # Initialize Stability AI client
        self.stability_client = self._initialize_stability_client()
        
    def _init_fonts(self):
        """Initialize fonts with fallbacks."""
        try:
            self.title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 56)
            self.subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 36)
        except:
            print("Warning: Custom fonts not found, using default font")
            self.title_font = ImageFont.load_default()
            self.subtitle_font = ImageFont.load_default()

    def _create_card_frame(self) -> Image.Image:
        """Create decorative frame for cards."""
        frame = Image.new('RGBA', (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(frame)
        
        # Outer border
        draw.rectangle([0, 0, self.CARD_WIDTH-1, self.CARD_HEIGHT-1], 
                      outline=(218, 165, 32, 255), width=self.BORDER_WIDTH)
        
        # Inner border
        draw.rectangle([self.MARGIN, self.MARGIN, 
                       self.CARD_WIDTH-self.MARGIN-1, self.CARD_HEIGHT-self.MARGIN-1],
                      outline=(218, 165, 32, 128), width=2)
        
        return frame

    def _create_text_background(self) -> Image.Image:
        """Create semi-transparent background for text area."""
        gradient = Image.new('RGBA', (self.CARD_WIDTH, self.TEXT_AREA_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        # Create gradient effect
        for y in range(self.TEXT_AREA_HEIGHT):
            alpha = int(128 * (y / self.TEXT_AREA_HEIGHT))
            draw.line([(0, y), (self.CARD_WIDTH, y)], fill=(0, 0, 0, alpha))
            
        return gradient

    def _initialize_stability_client(self) -> StabilityInference:
        """Initialize the Stability AI client with error handling"""
        try:
            return StabilityInference(
                key=self.api_key,
                verbose=True,
            )
        except Exception as e:
            logger.error(f"Failed to initialize Stability AI client: {str(e)}")
            if "401" in str(e):
                raise CardGenerationError(
                    "Invalid Stability AI API key",
                    ErrorCode.INVALID_API_KEY.value,
                    is_retryable=False
                )
            raise CardGenerationError(
                f"Failed to initialize Stability AI client: {str(e)}",
                ErrorCode.STABILITY_API_ERROR.value
            )

    def generate_card_art(
        self,
        mbti_type: str,
        card_name: str,
        suite: str,
        side: CardSide,
        orientation: CardOrientation = CardOrientation.UPRIGHT,
        wallet_address: Optional[str] = None,
        template_id: Optional[str] = None,
        force_regenerate: bool = False
    ) -> Image.Image:
        """Generate card artwork with caching and template support."""
        # Check cache if wallet provided
        if wallet_address and not force_regenerate:
            cached_cards = self.user_manager.get_user_cards(wallet_address)
            for card_id, card_data in cached_cards.items():
                if (card_data['data']['name'] == card_name and 
                    card_data['data']['suite'] == suite and
                    card_data['status'] == 'final'):
                    return Image.open(card_data['data']['image_path'])
        
        # Get prompt information
        prompt_info = self.data_manager.get_card_prompt(mbti_type, card_name, suite)
        prompt_info['card_name'] = card_name
        prompt_info['suite'] = suite
        
        # Generate base image using Stability AI
        base_image = self._generate_stability_image(prompt_info, side, orientation)
        
        # Apply template if specified
        if template_id:
            template = self.user_manager.get_card_template(template_id)
            base_image = self.template_manager.apply_template(base_image, template)
        
        # Cache the result if wallet provided
        if wallet_address:
            image_path = f"cache/users/{wallet_address}/{card_name}_{int(time.time())}.png"
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            base_image.save(image_path)
            
            card_data = {
                'name': card_name,
                'suite': suite,
                'mbti_type': mbti_type,
                'image_path': image_path,
                'template_id': template_id,
                'orientation': orientation.value
            }
            self.user_manager.cache_user_card(wallet_address, card_data)
        
        return base_image

    def _generate_stability_image(self, prompt_info: dict, side: CardSide, orientation: CardOrientation) -> Image.Image:
        """Generate image using Stability AI API."""
        # Get card name and suite from prompt info
        card_name = prompt_info.get('card_name', '')
        suite = prompt_info.get('suite', '')
        
        # Get specific imagery for this card
        specific_imagery = self._get_specific_card_imagery(card_name, suite)
        
        base_prompt = f"""
        Create a detailed mystical tarot card illustration with the following elements:
        
        Main Scene:
        {specific_imagery}
        
        Composition:
        - Centered focal point with balanced elements
        - Rich, deep colors with dramatic shadows
        - Professional fantasy art style
        - Clear foreground, midground, and background
        - Intricate details and symbolic elements
        - No text or borders
        """
        
        # Add personality elements
        personality_prompt = f"""
        Personality Influence:
        - Style: {prompt_info['personality_elements']['style']}
        - Character Traits: {', '.join(prompt_info['personality_elements']['traits'])}
        - Energy: {', '.join(prompt_info['personality_elements']['strengths'])}
        """
        
        # Add color scheme
        color_prompt = f"""
        Color Palette:
        - Primary: {', '.join(prompt_info['colors']['primary'])}
        - Accents: {', '.join(prompt_info['colors']['accent'])}
        - Background: {', '.join(prompt_info['colors']['background'])}
        """
        
        # Add symbolism
        symbolism_prompt = f"""
        Symbolic Elements:
        - Sacred Geometry: {', '.join(prompt_info['symbolism']['geometric'])}
        - Suite Elements: {prompt_info['symbolism'].get('suite', {}).get('description', '')}
        - Traditional Symbols: {prompt_info['symbolism'].get('key', {}).get('description', '')}
        - Psychological Aspect: {prompt_info['symbolism']['mbti']}
        """
        
        # Combine all prompts
        final_prompt = f"{base_prompt}\n{personality_prompt}\n{color_prompt}\n{symbolism_prompt}"
        
        try:
            logger.info(f"Generating image with prompt: {final_prompt}")
            answers = self.stability_client.generate(
                prompt=final_prompt,
                seed=int(time.time()),  # Dynamic seed
                steps=50,
                cfg_scale=8.0,
                width=self.CARD_WIDTH,
                height=self.CARD_HEIGHT,
                samples=1,
                sampler=generation.SAMPLER_K_DPMPP_2M
            )
            
            for answer in answers:
                if answer.artifacts:
                    image = Image.open(io.BytesIO(answer.artifacts[0].binary))
                    return image
                    
            raise CardGenerationError(
                "No image generated",
                ErrorCode.STABILITY_API_ERROR.value
            )
            
        except stability_sdk.exceptions.RateLimitError:
            logger.warning("Rate limit exceeded")
            raise CardGenerationError(
                "Rate limit exceeded",
                ErrorCode.RATE_LIMIT_EXCEEDED.value
            )
            
        except stability_sdk.exceptions.StabilityInvalidRequest as e:
            logger.error(f"Invalid request: {str(e)}")
            raise CardGenerationError(
                f"Invalid request: {str(e)}",
                ErrorCode.INVALID_PROMPT.value,
                is_retryable=False
            )
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}\n{traceback.format_exc()}")
            raise StabilityAIError(
                f"Failed to generate image: {str(e)}",
                ErrorCode.STABILITY_API_ERROR.value
            )

    def _get_specific_card_imagery(self, card_name: str, suite: str) -> str:
        """Get specific imagery for each card."""
        # Major Arcana specific imagery
        major_arcana_imagery = {
            "The Magician": """
                A powerful figure in flowing robes stands before an altar,
                Four elemental tools arranged on the altar: Wand (Fire), Cup (Water), Sword (Air), and Pentacle (Earth),
                The figure's right hand holds a wand pointing skyward, left hand points to earth,
                Above the figure's head floats the infinity symbol (∞),
                Red and white robes symbolizing wisdom and purity,
                Roses and lilies grow at their feet
            """,
            "The Sun": """
                A brilliant golden sun with a human face radiating straight and wavy rays,
                A young child riding a white horse beneath the sun,
                Four tall sunflowers rising behind a garden wall,
                The child wears a bright red feather and carries an orange banner,
                Clear blue sky background with minimal clouds,
                Vibrant yellows and oranges dominate the scene
            """,
            "The Star": """
                A graceful figure in flowing robes by a serene pool,
                Pouring water from two vessels, one onto land and one into water,
                Eight-pointed star shining brightly above, surrounded by seven smaller stars,
                An ibis bird perched in a flowering tree, representing wisdom,
                Ripples spreading across the water's surface,
                Night sky with ethereal starlight illuminating the scene
            """
        }
        
        # Minor Arcana specific imagery by number
        number_imagery = {
            "Ace": {
                "Wands": "A divine hand emerging from clouds holding a flowering staff, sparks and leaves flying, volcanic landscape",
                "Cups": "A chalice overflowing with five streams of water, dove carrying a wafer, radiant light from above",
                "Swords": "A crown-topped sword piercing through clouds, mountains in background, drops of golden light",
                "Pentacles": "A golden coin with a pentacle design held by a heavenly hand, garden paradise below"
            },
            "Two": {
                "Wands": "A figure holding a globe, standing between two staves, overlooking a vast landscape",
                "Cups": "Two chalices with a caduceus-like design between them, flowing water, doves exchanging tokens",
                "Swords": "Crossed swords, blindfolded figure, crescent moon, calm sea",
                "Pentacles": "A figure juggling two coins, infinity symbol (∞), ships on horizon"
            },
            "Three": {
                "Wands": "A merchant overlooking ships at sea from a cliff, three staffs planted in ground",
                "Cups": "Three figures dancing in a garden, raising chalices in celebration, abundant flowers",
                "Swords": "A heart pierced by three swords, storm clouds, rain",
                "Pentacles": "A craftsman reviewing work with apprentices, cathedral window"
            },
            "Four": {
                "Wands": "A flower-adorned gateway, dancers celebrating, castle in background",
                "Cups": "A figure contemplating three cups, one cup behind, angel offering opportunity",
                "Swords": "A figure resting in meditation, swords hanging above, stained glass window",
                "Pentacles": "A miser holding coins, crown, city walls"
            }
        }
        
        # Get card number and suite
        card_parts = card_name.split()
        if suite == "Major":
            return major_arcana_imagery.get(card_name, "")
        elif len(card_parts) >= 2:
            number = card_parts[0]
            if number in number_imagery and suite in number_imagery[number]:
                return number_imagery[number][suite]
        
        return ""

    def _compose_card(self, art_image: Image.Image, card_name: str, mbti_type: str) -> Image.Image:
        """Compose final card with artwork, frame, and text."""
        # Create base canvas
        final_image = Image.new('RGBA', (self.CARD_WIDTH, self.CARD_HEIGHT), (0, 0, 0, 255))
        
        # Resize and paste artwork
        art_area_height = self.CARD_HEIGHT - self.TEXT_AREA_HEIGHT - 2 * self.MARGIN
        art_image = art_image.resize((self.CARD_WIDTH - 2 * self.MARGIN, 
                                    art_area_height), 
                                   Image.Resampling.LANCZOS)
        final_image.paste(art_image, (self.MARGIN, self.MARGIN))
        
        # Add text background at bottom
        text_bg_pos = self.CARD_HEIGHT - self.TEXT_AREA_HEIGHT
        final_image.paste(self.text_bg, (0, text_bg_pos), self.text_bg)
        
        # Add frame
        final_image.paste(self.frame, (0, 0), self.frame)
        
        # Add text
        draw = ImageDraw.Draw(final_image)
        
        # Draw card name
        name_y = self.CARD_HEIGHT - self.TEXT_AREA_HEIGHT + 40
        self._draw_text_with_outline(draw, card_name, 
                                   self.CARD_WIDTH//2, name_y, 
                                   self.title_font)
        
        # Draw MBTI type
        type_y = self.CARD_HEIGHT - self.TEXT_AREA_HEIGHT + 100
        self._draw_text_with_outline(draw, mbti_type, 
                                   self.CARD_WIDTH//2, type_y, 
                                   self.subtitle_font)
        
        return final_image

    def regenerate_card(self, wallet_address: str, card_id: str,
                       template_id: Optional[str] = None) -> Image.Image:
        """Regenerate a specific card."""
        cached_cards = self.user_manager.get_user_cards(wallet_address)
        if card_id not in cached_cards:
            raise ValueError("Card not found in cache")
        
        card_data = cached_cards[card_id]['data']
        return self.generate_card_art(
            mbti_type=card_data['mbti_type'],
            card_name=card_data['name'],
            suite=card_data['suite'],
            side=CardSide.FRONT,
            orientation=CardOrientation(card_data['orientation']),
            wallet_address=wallet_address,
            template_id=template_id or card_data.get('template_id'),
            force_regenerate=True
        )

    def _draw_text_with_outline(self, draw: ImageDraw, 
                              text: str, x: int, y: int, 
                              font: ImageFont, 
                              outline_color: Tuple[int, int, int] = (0, 0, 0),
                              text_color: Tuple[int, int, int] = (255, 215, 0)):  # Golden text
        """Draw text with outline for better visibility."""
        # Draw outline
        for offset_x, offset_y in [(2,2), (-2,-2), (2,-2), (-2,2)]:
            draw.text((x + offset_x, y + offset_y), text, 
                     font=font, fill=outline_color, anchor="mm")
        # Draw main text
        draw.text((x, y), text, font=font, fill=text_color, anchor="mm")
                    
    def _get_element_style(self, mbti_type: str) -> str:
        elements = {
            'NT': 'ethereal geometric patterns, technological and cosmic symbols, deep purples and blues',
            'NF': 'flowing organic shapes, spiritual and mystical symbols, rich golds and violets',
            'ST': 'structured mechanical elements, logical and mathematical symbols, metallic silvers and blacks',
            'SF': 'natural organic patterns, emotional and earthly symbols, warm browns and greens'
        }
        return elements.get(mbti_type[:2], elements['NT'])
        
    def _get_suite_style(self, suite: str) -> str:
        styles = {
            'Swords': 'sharp angular designs, air elements, silver metallic accents, floating crystals',
            'Cups': 'flowing water elements, emotional symbols, deep blues and aqua, rippling effects',
            'Sceptres': 'fire elements, energy patterns, warm colors, flame motifs, ascending spirals',
            'Pentacles': 'earth elements, crystal formations, rich greens and golds, growing vines'
        }
        return styles.get(suite, '')

    def _get_composition_style(self, card_name: str) -> str:
        """Get detailed composition style based on card name and traditional symbolism."""
        # Get RWS symbolism
        rws = self._get_rws_symbolism(card_name)
        
        # Court Cards with enhanced symbolism
        if 'King' in card_name:
            return f"""regal figure on ornate throne, crown motif, commanding presence,
                   geometric throne design with {rws['elements'][0]} symbols,
                   {', '.join(rws['symbols'])},
                   color palette: {', '.join(rws['colors'])}"""
        elif 'Queen' in card_name:
            return f"""elegant figure with flowing robes, nature elements, nurturing presence,
                   curved throne design with {rws['elements'][0]} symbols,
                   {', '.join(rws['symbols'])},
                   color palette: {', '.join(rws['colors'])}"""
        elif 'Knight' in card_name:
            return f"""dynamic figure in motion, action scene, determined presence,
                   moving {rws['elements'][0]} energy,
                   {', '.join(rws['symbols'])},
                   color palette: {', '.join(rws['colors'])}"""
        elif 'Page' in card_name:
            return f"""youthful figure with symbolic object, learning scene, curious presence,
                   gentle {rws['elements'][0]} elements,
                   {', '.join(rws['symbols'])},
                   color palette: {', '.join(rws['colors'])}"""
        
        # Minor Arcana Numbers with geometric patterns
        try:
            number_words = {
                'Ace': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5,
                'Six': 6, 'Seven': 7, 'Eight': 8, 'Nine': 9, 'Ten': 10
            }
            
            for word, num in number_words.items():
                if word in card_name:
                    # Get suite-specific elements
                    suite = next((s for s in ['Swords', 'Cups', 'Sceptres', 'Pentacles'] 
                                if s in card_name), '')
                    
                    # Combine number geometry with suite elements
                    return self._get_number_suite_composition(num, suite, rws)
        except:
            pass
        
        # Major Arcana or unrecognized card
        return f"""symbolic arrangement based on RWS tradition,
               {rws['composition']},
               featuring {', '.join(rws['symbols'])},
               color palette: {', '.join(rws['colors'])}"""

    def _get_number_suite_composition(self, number: int, suite: str, rws: dict) -> str:
        """Get detailed composition for number and suite combination."""
        # Base geometric patterns for numbers
        geometries = {
            1: ('circle', 'point of origin', 'central emanation'),
            2: ('vesica piscis', 'mirrored forms', 'balanced duality'),
            3: ('triangle', 'triad', 'dynamic growth'),
            4: ('square', 'cross', 'stable foundation'),
            5: ('pentagram', 'five-pointed star', 'dynamic change'),
            6: ('hexagon', 'honeycomb', 'harmony'),
            7: ('septagram', 'seven-pointed star', 'mystical order'),
            8: ('octagon', 'double square', 'infinite flow'),
            9: ('triple triangle', 'three triads', 'completion'),
            10: ('decagon', 'tree of life', 'manifestation')
        }
        
        # Suite-specific manifestations
        suite_patterns = {
            'Swords': {
                'element': 'air',
                'energy': 'intellectual',
                'symbols': ['clouds', 'wind patterns', 'mountain peaks'],
                'motifs': {
                    'low': ['conflict', 'sharp angles', 'crossing paths'],
                    'mid': ['decision', 'clarity', 'truth'],
                    'high': ['victory', 'transcendence', 'wisdom']
                }
            },
            'Cups': {
                'element': 'water',
                'energy': 'emotional',
                'symbols': ['waves', 'fish', 'lotus flowers'],
                'motifs': {
                    'low': ['reflection', 'pools', 'mist'],
                    'mid': ['flow', 'fountains', 'rivers'],
                    'high': ['abundance', 'ocean', 'rain']
                }
            },
            'Sceptres': {
                'element': 'fire',
                'energy': 'spiritual',
                'symbols': ['flames', 'salamanders', 'sun rays'],
                'motifs': {
                    'low': ['sparks', 'embers', 'smoke'],
                    'mid': ['torches', 'bonfires', 'lanterns'],
                    'high': ['solar disc', 'phoenix', 'lightning']
                }
            },
            'Pentacles': {
                'element': 'earth',
                'energy': 'material',
                'symbols': ['crystals', 'vines', 'sacred geometry'],
                'motifs': {
                    'low': ['seeds', 'roots', 'soil'],
                    'mid': ['gardens', 'trees', 'fruits'],
                    'high': ['mountains', 'temples', 'stars']
                }
            }
        }
        
        # Get base geometry
        geo = geometries.get(number, ('circle', 'form', 'energy'))
        
        # Get suite patterns
        pat = suite_patterns.get(suite, suite_patterns['Pentacles'])
        
        # Determine motif level based on number
        level = 'low' if number <= 3 else 'mid' if number <= 6 else 'high'
        
        # Combine all elements
        composition = f"""
        Geometric base: {geo[0]} pattern with {pat['element']} energy,
        Arrangement: {geo[1]} showing {pat['energy']} {geo[2]},
        Elements: {', '.join(pat['symbols'])},
        Motifs: {', '.join(pat['motifs'][level])},
        Traditional elements: {rws['composition']},
        Color palette: {', '.join(rws['colors'])}
        """
        
        return composition.strip()

    def _get_rws_symbolism(self, card_name: str) -> dict:
        """Get traditional RWS symbolism for a card."""
        symbolism = {
            # Major Arcana
            'The Fool': {
                'symbols': ['white dog', 'cliff edge', 'knapsack', 'white rose'],
                'colors': ['yellow', 'white', 'red'],
                'elements': ['air', 'earth'],
                'composition': 'figure stepping off cliff, dog at heels'
            },
            # Swords
            'Ace of Swords': {
                'symbols': ['crown', 'laurel wreath', 'mountain peaks'],
                'colors': ['silver', 'gold', 'blue'],
                'elements': ['air', 'metal'],
                'composition': 'sword pointing upward through crown'
            },
            'Two of Swords': {
                'symbols': ['blindfold', 'crossed swords', 'crescent moon'],
                'colors': ['blue', 'silver', 'gray'],
                'elements': ['air', 'water'],
                'composition': 'seated figure with balanced swords'
            },
            # Cups
            'Ace of Cups': {
                'symbols': ['dove', 'holy water', 'five streams'],
                'colors': ['gold', 'blue', 'white'],
                'elements': ['water', 'air'],
                'composition': 'chalice with divine energy flowing'
            },
            'Two of Cups': {
                'symbols': ['caduceus', 'lion head', 'winged crown'],
                'colors': ['blue', 'gold', 'red'],
                'elements': ['water', 'fire'],
                'composition': 'two figures exchanging cups'
            },
            # Sceptres
            'Ace of Sceptres': {
                'symbols': ['sprouts', 'castle', 'landscape'],
                'colors': ['green', 'red', 'gold'],
                'elements': ['fire', 'earth'],
                'composition': 'divine hand offering flowering staff'
            },
            'Two of Sceptres': {
                'symbols': ['globe', 'crossed wands', 'rose'],
                'colors': ['orange', 'red', 'gray'],
                'elements': ['fire', 'earth'],
                'composition': 'figure holding globe between wands'
            },
            # Pentacles
            'Ace of Pentacles': {
                'symbols': ['garden', 'archway', 'lilies'],
                'colors': ['gold', 'green', 'white'],
                'elements': ['earth', 'air'],
                'composition': 'divine hand offering golden coin'
            },
            'Two of Pentacles': {
                'symbols': ['infinity symbol', 'ships', 'waves'],
                'colors': ['gold', 'green', 'blue'],
                'elements': ['earth', 'water'],
                'composition': 'figure juggling two coins'
            }
        }
        
        # Default symbolism if card not found
        default_symbolism = {
            'symbols': ['mystical elements', 'traditional symbols'],
            'colors': ['gold', 'blue', 'purple'],
            'elements': ['spirit', 'light'],
            'composition': 'balanced mystical arrangement'
        }
        
        return symbolism.get(card_name, default_symbolism)

    def _get_back_pattern(self, mbti_type: str) -> str:
        patterns = {
            'NT': 'technological mandala with circuit patterns and sacred geometry',
            'NF': 'spiritual mandala with flowing energy and mystical symbols',
            'ST': 'precise geometric mandala with mathematical harmony',
            'SF': 'natural mandala with organic forms and emotional symbols'
        }
        return patterns.get(mbti_type[:2], patterns['NT'])