# Fallout 76 Character Builder - Frontend

A modern, fully-featured React frontend for the Fallout 76 Character Builder database and RAG system.

## 🚀 Features

### Completed
- ✅ **Home Dashboard** - Stats overview with animated cards and quick navigation
- ✅ **Weapons Database** - Browse 262+ weapons with advanced filtering and search
- ✅ **Armor Database** - Browse 477+ armor pieces with type, class, and slot filters
- ✅ **Perks System** - View regular and legendary perks with SPECIAL stat filtering
- ✅ **Mutations** - Complete list of 19 mutations with effects
- ✅ **Consumables** - Build-relevant consumables with duration and effect data
- ✅ **AI Chat Interface** - RAG-powered chat with Claude AI for build questions
- ✅ **Build Planner** - Create, save, and share character builds with SPECIAL allocation
- ✅ **HashRouter Navigation** - Client-side routing without server configuration
- ✅ **GSAP Animations** - Smooth, professional animations throughout

### Tech Stack
- **React 19.1.1** - Latest React with concurrent features
- **TypeScript** - Full type safety
- **Vite 7.1.7** - Lightning-fast build tool
- **TailwindCSS 4.1.14** - Utility-first styling
- **DaisyUI 5.3.0** - Beautiful component library
- **GSAP 3.13.0** - Professional-grade animations
- **React Router DOM** - HashRouter for static hosting

## 📦 Installation

```bash
npm install
```

## 🛠️ Development

```bash
# Start dev server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file (see `.env.example`):

```env
VITE_API_URL=http://localhost:8000
```

### API Backend
Ensure the FastAPI backend is running on port 8000:

```bash
# From project root
cd api
python main.py
```

## 📁 Project Structure

```
react/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Layout.tsx        # Main layout with navbar/footer
│   │   │   └── Navbar.tsx        # Animated navigation bar
│   │   └── ui/
│   │       ├── Button.tsx        # Animated button with variants
│   │       ├── Card.tsx          # Hoverable card with GSAP
│   │       ├── ErrorMessage.tsx  # Error display component
│   │       ├── Loading.tsx       # Loading spinner
│   │       ├── Pagination.tsx    # Pagination controls
│   │       ├── SearchBar.tsx     # Animated search input
│   │       ├── Select.tsx        # Dropdown select
│   │       ├── StatBadge.tsx     # Stat display badge
│   │       └── index.ts          # Barrel export
│   ├── config/
│   │   └── constants.ts          # App-wide constants
│   ├── hooks/
│   │   ├── useAPI.ts             # API fetching hooks
│   │   └── useLocalStorage.ts   # LocalStorage hook
│   ├── pages/
│   │   ├── Home.tsx              # Landing page
│   │   ├── Weapons.tsx           # Weapons list
│   │   ├── WeaponDetail.tsx      # Weapon detail view
│   │   ├── Armor.tsx             # Armor list
│   │   ├── Perks.tsx             # Perks list (regular + legendary)
│   │   ├── Mutations.tsx         # Mutations list
│   │   ├── Consumables.tsx       # Consumables list
│   │   ├── Chat.tsx              # RAG Chat interface
│   │   └── BuildPlanner.tsx      # Build creation tool
│   ├── types/
│   │   └── api.ts                # TypeScript type definitions
│   ├── utils/
│   │   ├── api.ts                # API client functions
│   │   └── format.ts             # Formatting utilities
│   ├── App.tsx                   # Main app with HashRouter
│   ├── main.tsx                  # React entry point
│   └── index.css                 # Global styles + Tailwind
├── public/                       # Static assets
├── .env.example                  # Environment template
├── package.json                  # Dependencies
├── tsconfig.json                 # TypeScript config
├── vite.config.ts                # Vite config
└── tailwind.config.js            # Tailwind config
```

## 🎨 Key Components

### API Integration
All API calls are centralized in `src/utils/api.ts` with TypeScript types from `src/types/api.ts`.

### Custom Hooks
- **useAPI** - Generic data fetching with loading/error states
- **usePaginatedAPI** - Paginated data with page controls
- **useDebounce** - Debounced search inputs
- **useLocalStorage** - Persistent state storage

### GSAP Animations
- Page entrance animations (stagger, fade, slide)
- Hover effects on cards and buttons
- Smooth transitions throughout
- Uses `@gsap/react` hook for proper React integration

## 🔑 Features Detail

### Weapons & Armor
- Advanced filtering by type, class, slot
- Real-time search with debouncing
- Pagination controls
- Detailed view with full stats and modifiers

### Perks
- Toggle between regular and legendary perks
- Filter by SPECIAL stat
- View max ranks and requirements

### AI Chat
- RAG-powered responses using Claude AI
- Context sources display
- Conversation history
- Example questions for quick start

### Build Planner
- SPECIAL stat allocation with visual sliders
- Point budget tracking
- Save builds to localStorage
- Share builds via encoded URL
- Load previously saved builds

## 🎯 GSAP Modules Used

Currently using:
- `gsap` core
- `@gsap/react` hook integration

### Additional GSAP Modules Available
If you want to enhance animations further, consider these GSAP plugins:

```bash
npm install gsap-trial
```

Recommended plugins:
- **ScrollTrigger** - Scroll-based animations
- **Draggable** - Drag-and-drop interactions
- **MotionPathPlugin** - Animate along paths
- **ScrollToPlugin** - Smooth scrolling
- **TextPlugin** - Text animations

## 📱 Responsive Design

- Mobile-first approach with Tailwind breakpoints
- Responsive grid layouts (1/2/3 columns)
- Mobile navigation drawer
- Touch-friendly controls

## 🚀 Deployment

### Build Output
```bash
npm run build
# Output: dist/
```

### Deploy to Static Hosting
The app uses HashRouter, so it works with any static host:

- **Netlify**: Drag & drop `dist/` folder
- **Vercel**: Import repo, zero config needed
- **GitHub Pages**: Deploy `dist/` to gh-pages branch
- **Firebase Hosting**: `firebase deploy`

No server-side routing configuration needed!

## 🔧 Troubleshooting

### API Connection Issues
- Verify backend is running on port 8000
- Check `VITE_API_URL` in `.env`
- Enable CORS in FastAPI backend

### Build Errors
- Run `npm install` to ensure dependencies
- Check TypeScript errors with `npm run build`
- Use `npm run lint` to catch issues

### Performance
- All API calls are cached in component state
- Debounced search prevents excessive requests
- Pagination limits data fetching

## 📄 License

MIT

## 🙋 Support

This is a personal academic project for ML/AI coursework. The backend is fully operational with 1,206+ items in a normalized MySQL database and RAG-powered AI chat.
