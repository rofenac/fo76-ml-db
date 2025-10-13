# Frontend Development Guidelines

## Project Context

This is the frontend for the **Fallout 76 Character Builder** application, part of a larger project that includes:
- MySQL database with 262 weapons, 477 armor pieces, and 268 perks
- RAG-powered Claude AI interface for build optimization
- Comprehensive game data scraped from Fallout Wiki
- Python-based backend and data collection system

## Technology Stack

This frontend uses the following technologies:

- **TypeScript** - Type-safe JavaScript development
- **React 19** - Modern React with latest features
- **Vite** - Fast build tool and development server
- **TailwindCSS v4** - Utility-first CSS framework
- **DaisyUI** - TailwindCSS component library
- **GSAP** - Professional-grade animation library
- **ESM** - ES Module support throughout

## Standing Orders

### 1. Always Use ESM Syntax

This project strictly uses ES Modules. Always use:

```typescript
// ✅ CORRECT - ESM syntax
import { useState } from 'react';
import App from './App';
export default MyComponent;
export { namedExport };

// ❌ INCORRECT - CommonJS syntax
const React = require('react');
module.exports = MyComponent;
```

### 2. Always Use useGSAP Hook

Never use GSAP animations directly. Always wrap them in the `useGSAP()` hook from `@gsap/react`:

```typescript
// ✅ CORRECT - useGSAP wrapper
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";

function MyComponent() {
  const elementRef = useRef(null);

  useGSAP(() => {
    gsap.from(elementRef.current, {
      opacity: 0,
      duration: 1
    });
  }, []);

  return <div ref={elementRef}>Content</div>;
}

// ❌ INCORRECT - Direct GSAP usage
function MyComponent() {
  useEffect(() => {
    gsap.from('.element', { opacity: 0 });
  }, []);
}
```

**Why useGSAP?**
- Automatic cleanup when component unmounts
- Better React integration and lifecycle management
- Proper scope management for animations
- Type safety with TypeScript
- Consistent patterns across the project

### 3. TailwindCSS v4 + DaisyUI

- Use TailwindCSS utility classes for styling
- Leverage DaisyUI components (cards, alerts, badges, buttons, etc.)
- Configuration is in `src/index.css` via `@import` and `@plugin` directives
- Dark theme is preferred for gaming aesthetic

### 4. TypeScript Best Practices

- Always type your props and state
- Use proper TypeScript generics (e.g., `useRef<HTMLDivElement>(null)`)
- Leverage TypeScript's strict mode
- Multiple tsconfig files handle different concerns

### 5. Project Structure

```
react/
├── src/
│   ├── App.tsx          # Main application component
│   ├── main.tsx         # React entry point
│   ├── index.css        # Global styles (Tailwind imports)
│   └── assets/          # Static assets
├── public/              # Public static files
├── index.html           # HTML template
└── DEVELOPMENT_GUIDELINES.md  # This file
```

## Code Style Guidelines

### Component Structure

```typescript
import { gsap } from "gsap";
import { useGSAP } from "@gsap/react";
import { useRef, useState } from 'react';
import './styles.css';

interface MyComponentProps {
  title: string;
  count?: number;
}

function MyComponent({ title, count = 0 }: MyComponentProps) {
  const [state, setState] = useState<number>(count);
  const elementRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    // GSAP animations here
    gsap.from(elementRef.current, {
      opacity: 0,
      y: 50,
      duration: 1
    });
  }, []);

  return (
    <div ref={elementRef} className="container">
      <h1>{title}</h1>
      <p>{state}</p>
    </div>
  );
}

export default MyComponent;
```

### Animation Patterns

```typescript
// Staggered animations
useGSAP(() => {
  gsap.from(cardsRef.current?.children || [], {
    opacity: 0,
    y: 50,
    stagger: 0.2,
    duration: 0.8
  });
}, []);

// Timeline sequences
useGSAP(() => {
  const tl = gsap.timeline();

  tl.from(titleRef.current, {
    opacity: 0,
    y: -50,
    duration: 1
  })
  .from(subtitleRef.current, {
    opacity: 0,
    y: -30,
    duration: 0.8
  }, "-=0.5"); // Overlap by 0.5s
}, []);
```

## Related Documentation

- Parent project: `../README.md`
- Database schema: `../docs/SCHEMA_DESIGN.md`
- Project roadmap: `../docs/TODO.md`
- RAG system: `../rag/` (in parent directory)
- Frontend README: `./README.md`

## Development Commands

```bash
npm run dev      # Start dev server (http://localhost:5173)
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Lint code
```

## Important Notes

- This is an academic project for ML/AI coursework
- Backend and database are fully functional
- Frontend is in early development
- RAG interface will be integrated in future phases
- All game data sourced from Fallout Wiki
