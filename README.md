# Mystic Tarot NFT

A web application that generates personalized tarot card readings based on MBTI personality types, with the ability to mint cards as NFTs.

## Project Structure

```
.
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/         # Page components
│   │   ├── styles/        # CSS styles
│   │   ├── app.ts         # Main application entry
│   │   ├── main.ts        # Web3 wallet integration
│   │   └── results.ts     # Results page logic
│   ├── public/           # Static assets
│   ├── package.json      # Frontend dependencies
│   └── vite.config.js    # Vite configuration
│
└── backend/
    ├── src/
    │   ├── tarot/        # Core tarot card generation
    │   └── app.py        # Flask server
    ├── tests/           # Python tests
    └── pyproject.toml   # Backend dependencies
```

## Getting Started

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
poetry install
poetry run python src/app.py
```

## Features

- MBTI Personality Quiz
- AI-Generated Tarot Cards
- NFT Minting Capability
- Email Results Sharing
- Web3 Wallet Integration

## Technologies

### Frontend
- TypeScript
- Vite
- Web3Modal
- Wagmi

### Backend
- Python
- Flask
- Pillow
- Stability AI SDK

## License

MIT License
