# Mystic Tarot NFT Backend

The Python backend for the Mystic Tarot NFT project, built with Flask.

## Directory Structure

```
src/
├── tarot/              # Core tarot package
│   ├── card_generator.py  # Card generation logic
│   ├── data_manager.py    # Data handling
│   ├── template_manager.py # Card template management
│   └── user_manager.py    # User data handling
└── app.py              # Flask server

tests/                  # Test files
├── test_card_generation.py
├── test_deck_manager.py
├── test_mbti_cards.py
├── test_specific_cards.py
└── test_user_cards.py
```

## Development

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the development server:
```bash
poetry run python src/app.py
```

5. Run tests:
```bash
poetry run pytest
```

## Features

- MBTI personality analysis
- AI-powered tarot card generation
- Card caching system
- User data management
- Web3 integration for NFTs

## Dependencies

- Flask - Web framework
- Pillow - Image processing
- Stability AI SDK - AI image generation
- Web3.py - Ethereum interaction
- pytest - Testing

## API Endpoints

- `/api/questions` - Get personality quiz questions
- `/api/calculate-result` - Process quiz answers and generate cards
- `/api/save-reading` - Save reading results
- `/api/verify-wallet` - Verify wallet ownership

## Testing

Run tests with coverage:
```bash
poetry run pytest --cov=tarot
```

## Code Style

The project uses:
- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run formatters:
```bash
poetry run black .
poetry run isort .
```
