from typing import Dict, Optional
from PIL import Image, ImageDraw
import json
from pathlib import Path

class TemplateManager:
    def __init__(self):
        self.templates_dir = Path("data/templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._load_templates()
    
    def _load_templates(self):
        """Load card templates."""
        self.templates = {
            'borders': {
                'classic': {
                    'ornate': self._create_ornate_border,
                    'simple': self._create_simple_border
                },
                'modern': {
                    'minimal': self._create_minimal_border,
                    'gradient': self._create_gradient_border
                },
                'ethereal': {
                    'flowing': self._create_flowing_border,
                    'cosmic': self._create_cosmic_border
                }
            },
            'backgrounds': {
                'parchment': self._create_parchment_bg,
                'gradient': self._create_gradient_bg,
                'cosmic': self._create_cosmic_bg
            }
        }
    
    def apply_template(self, image: Image.Image, template: Dict) -> Image.Image:
        """Apply a template to an image."""
        # Create a new image with the template
        width, height = image.size
        final_image = Image.new('RGBA', (width + 40, height + 40), (0, 0, 0, 0))
        
        # Apply background
        bg_style = template.get('background', 'parchment')
        if bg_style in self.templates['backgrounds']:
            background = self.templates['backgrounds'][bg_style](width + 40, height + 40)
            final_image.paste(background, (0, 0))
        
        # Apply border
        border_config = template.get('border', {'style': 'ornate', 'color': 'gold'})
        border_style = border_config['style']
        if border_style in self.templates['borders']['classic']:
            border = self.templates['borders']['classic'][border_style](
                width + 40, 
                height + 40, 
                border_config.get('color', 'gold'),
                border_config.get('width', 20)
            )
            final_image.paste(border, (0, 0), border)
        
        # Paste the main image
        final_image.paste(image, (20, 20))
        
        return final_image
    
    def _create_ornate_border(self, width: int, height: int, color: str, border_width: int) -> Image.Image:
        """Create an ornate border."""
        border = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(border)
        
        # Convert color string to RGB
        color_map = {
            'gold': (218, 165, 32, 255),
            'silver': (192, 192, 192, 255),
            'bronze': (205, 127, 50, 255)
        }
        rgb_color = color_map.get(color, (218, 165, 32, 255))
        
        # Draw ornate border
        draw.rectangle([(0, 0), (width-1, height-1)], outline=rgb_color, width=border_width)
        # Add corner decorations
        corner_size = border_width * 2
        for x, y in [(0, 0), (width-corner_size, 0), (0, height-corner_size), (width-corner_size, height-corner_size)]:
            draw.ellipse([x, y, x+corner_size, y+corner_size], outline=rgb_color, width=2)
        
        return border
    
    def _create_simple_border(self, width: int, height: int, color: str, border_width: int) -> Image.Image:
        """Create a simple border."""
        border = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(border)
        
        color_map = {
            'gold': (218, 165, 32, 255),
            'silver': (192, 192, 192, 255),
            'bronze': (205, 127, 50, 255)
        }
        rgb_color = color_map.get(color, (218, 165, 32, 255))
        
        draw.rectangle([(0, 0), (width-1, height-1)], outline=rgb_color, width=border_width)
        return border
    
    def _create_minimal_border(self, width: int, height: int, color: str, border_width: int) -> Image.Image:
        """Create a minimal border."""
        # Similar to simple but with thinner lines
        return self._create_simple_border(width, height, color, max(1, border_width // 2))
    
    def _create_gradient_border(self, width: int, height: int, color: str, border_width: int) -> Image.Image:
        """Create a gradient border."""
        border = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(border)
        
        color_map = {
            'gold': [(218, 165, 32), (255, 215, 0)],
            'silver': [(192, 192, 192), (220, 220, 220)],
            'bronze': [(205, 127, 50), (218, 165, 32)]
        }
        colors = color_map.get(color, [(218, 165, 32), (255, 215, 0)])
        
        # Create gradient effect with multiple lines
        for i in range(border_width):
            factor = i / border_width
            current_color = tuple(
                int(colors[0][j] * (1-factor) + colors[1][j] * factor)
                for j in range(3)
            ) + (255,)
            draw.rectangle(
                [(i, i), (width-1-i, height-1-i)],
                outline=current_color,
                width=1
            )
        
        return border
    
    def _create_flowing_border(self, width: int, height: int, color: str, border_width: int) -> Image.Image:
        """Create a flowing, organic border."""
        border = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(border)
        
        color_map = {
            'gold': (218, 165, 32, 255),
            'silver': (192, 192, 192, 255),
            'iridescent': (200, 200, 255, 255)
        }
        rgb_color = color_map.get(color, (218, 165, 32, 255))
        
        # Create flowing effect with curved corners
        draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=border_width*2, 
                             outline=rgb_color, width=border_width)
        return border
    
    def _create_cosmic_border(self, width: int, height: int, color: str, border_width: int) -> Image.Image:
        """Create a cosmic-themed border."""
        border = self._create_flowing_border(width, height, color, border_width)
        # Add cosmic effects (stars, nebula-like patterns)
        draw = ImageDraw.Draw(border)
        
        # Add star points
        for _ in range(20):
            x = width * ((_ * 17) % 100) // 100
            y = height * ((_ * 23) % 100) // 100
            size = 2
            draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 255, 255, 200))
        
        return border
    
    def _create_parchment_bg(self, width: int, height: int) -> Image.Image:
        """Create a parchment-like background."""
        bg = Image.new('RGBA', (width, height), (245, 235, 220, 255))
        return bg
    
    def _create_gradient_bg(self, width: int, height: int) -> Image.Image:
        """Create a gradient background."""
        bg = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(bg)
        
        for y in range(height):
            color = tuple(int(255 * (1 - y/height)) for _ in range(3)) + (255,)
            draw.line([(0, y), (width, y)], fill=color)
        
        return bg
    
    def _create_cosmic_bg(self, width: int, height: int) -> Image.Image:
        """Create a cosmic-themed background."""
        bg = Image.new('RGBA', (width, height), (10, 0, 30, 255))
        draw = ImageDraw.Draw(bg)
        
        # Add stars
        for _ in range(100):
            x = width * ((_ * 17) % 100) // 100
            y = height * ((_ * 23) % 100) // 100
            size = 1
            draw.ellipse([x-size, y-size, x+size, y+size], fill=(255, 255, 255, 150))
        
        return bg
