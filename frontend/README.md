# Mystic Tarot NFT Frontend

The frontend application for the Mystic Tarot NFT project, built with TypeScript and Vite.

## Directory Structure

```
src/
├── components/     # Reusable UI components
│   └── header.js  # Shared header with wallet connection
├── pages/         # Page components
│   ├── index.html      # Landing page
│   ├── personality_test.html  # MBTI quiz
│   └── results.html    # Results and card display
├── styles/        # CSS styles
│   └── styles.css     # Global styles
├── app.ts         # Main application entry
├── main.ts        # Web3 wallet integration
└── results.ts     # Results page logic
```

## Development

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Build for production:
```bash
npm run build
```

## Features

- Responsive design with consistent dark theme
- Web3 wallet integration using Web3Modal
- MBTI personality quiz
- Tarot card display
- NFT minting capability
- Email results sharing

## Dependencies

- @reown/appkit - Web3 wallet integration
- @reown/appkit-adapter-wagmi - Wagmi adapter
- Vite - Build tool and development server
- TypeScript - Type safety
- Jest - Testing

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run tests
- `npm run lint` - Run ESLint
