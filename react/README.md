# Fallout 76 Character Builder - Frontend

A modern, interactive React-based frontend for the Fallout 76 Character Builder application. This interface connects to a MySQL database populated with FO76 item and perk data, and integrates with Claude AI using a RAG (Retrieval Augmented Generation) interface to answer questions about character builds.

## Tech Stack

- **TypeScript** - Type-safe JavaScript development
- **React 19** - Modern React with latest features
- **Vite** - Fast build tool and development server
- **TailwindCSS v4** - Utility-first CSS framework
- **DaisyUI** - TailwindCSS component library
- **GSAP** - Professional-grade animation library
- **ESM** - ES Module support throughout

## Project Overview

This frontend is part of a larger project that includes:
- MySQL database with 262 weapons, 477 armor pieces, and 268 perks
- RAG-powered Claude AI interface for build optimization
- Comprehensive game data scraped from Fallout Wiki

See the parent directory and `/docs` folder for complete project documentation.

## Quick Start

### Prerequisites

- Node.js 18+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Development

The dev server runs on `http://localhost:5173` by default (Vite's default port).

### Project Structure

```
react/
├── src/
│   ├── App.tsx          # Main application component
│   ├── main.tsx         # React entry point
│   ├── index.css        # Global styles (Tailwind imports)
│   └── assets/          # Static assets
├── public/              # Public static files
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── tsconfig.json        # TypeScript configuration
├── vite.config.ts       # Vite configuration
└── eslint.config.js     # ESLint configuration
```

## Features

### Current Implementation

- Landing page with animated statistics showcase
- Responsive design using TailwindCSS and DaisyUI
- GSAP-powered entrance animations
- Dark theme optimized for gaming aesthetic

### Planned Features

- Character build planner interface
- RAG-powered AI chat for build questions
- Weapon and armor comparison tools
- Perk calculator with synergy recommendations
- Build sharing and export functionality

## Dependencies

### Core Dependencies
- `react` & `react-dom` - React framework
- `typescript` - Type safety
- `gsap` & `@gsap/react` - Animation library
- `tailwindcss` & `@tailwindcss/vite` - Styling framework
- `daisyui` - UI component library

### Dev Dependencies
- `vite` & `@vitejs/plugin-react` - Build tooling
- `eslint` - Code linting
- `typescript-eslint` - TypeScript linting rules

## Configuration

### TailwindCSS

TailwindCSS v4 is configured via `src/index.css`:
```css
@import "tailwindcss";
@plugin "daisyui";
```

### TypeScript

Multiple tsconfig files for different concerns:
- `tsconfig.json` - Base configuration
- `tsconfig.app.json` - Application code
- `tsconfig.node.json` - Build tooling

### Vite

Configuration in `vite.config.ts` includes React plugin and optimizations.

## Contributing

This is a personal academic project for ML/AI coursework. The backend and database are fully functional; the frontend is in early development.

## Related Documentation

- Parent project README: `../README.md`
- Database schema: `../docs/SCHEMA_DESIGN.md`
- Project roadmap: `../docs/TODO.md`
- RAG system docs: `../rag/` (in parent directory)

## License

MIT License