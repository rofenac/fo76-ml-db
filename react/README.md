# Fallout 76 Character Builder - Frontend

React-based frontend for the Fallout 76 Character Builder, connecting to MySQL database with 1,206 items and RAG-powered Claude AI.

## Tech Stack

- **React 19** + **TypeScript** + **Vite**
- **TailwindCSS v4** + **DaisyUI** (styling)
- **GSAP** (animations)
- **ESM** modules throughout

## Quick Start

```bash
npm install      # Install dependencies
npm run dev      # Start dev server (http://localhost:5173)
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Lint code
```

## Project Structure

```
react/
├── src/
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # React entry point
│   ├── index.css        # Global styles (Tailwind config)
│   └── assets/          # Static assets
├── public/              # Public files
├── index.html           # HTML template
└── [config files]       # tsconfig, vite.config, eslint.config
```

## Features

**Current:**
- Animated statistics showcase
- Responsive dark theme
- GSAP entrance animations

**Planned:**
- Character build planner
- RAG-powered AI chat
- Weapon/armor comparison tools
- Perk calculator with synergy recommendations
- Build sharing and export

## Configuration

**TailwindCSS v4:** Configured in `src/index.css`:
```css
@import "tailwindcss";
@plugin "daisyui";
```

**TypeScript:** Multiple configs handle different concerns (app, node, base)

**Vite:** React plugin configured in `vite.config.ts`

## Development Guidelines

See `DEVELOPMENT_GUIDELINES.md` for:
- ESM syntax requirements (always use `import`/`export`)
- GSAP animation patterns (always use `useGSAP()` hook)
- TypeScript best practices
- Component structure patterns

## Related Documentation

- Parent project: `../README.md`
- Project roadmap: `../docs/TODO.md`
- Weapon mechanics: `../docs/WEAPON_MECHANICS.md`
- RAG system: `../rag/` (in parent directory)

## Status

Personal academic project for ML/AI coursework. Backend operational; frontend in early development.

## License

MIT
