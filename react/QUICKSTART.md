# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure API
Create `.env` file:
```bash
echo "VITE_API_URL=http://localhost:8000" > .env
```

### 3. Start Development Server
```bash
npm run dev
```

Visit **http://localhost:5173** 🎉

---

## 🔧 Full Setup (First Time)

### Prerequisites
- Node.js 18+ installed
- Backend API running on port 8000

### Backend Setup (if not running)
```bash
# From project root
cd ../api
python main.py
```

### Frontend Setup
```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start dev server
npm run dev
```

---

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server on port 5173 |
| `npm run build` | Build for production → `dist/` |
| `npm run preview` | Preview production build |
| `npm run lint` | Check code quality |

---

## 🎯 First Steps After Starting

1. **Explore Database**
   - Click "Weapons" to browse 262 weapons
   - Try filters and search

2. **Ask the AI**
   - Go to "AI Chat"
   - Try: "What are the best weapons for a stealth build?"

3. **Build a Character**
   - Visit "Build Planner"
   - Allocate SPECIAL points
   - Save your build

---

## 🐛 Common Issues

### Port Already in Use
```bash
# Kill process on port 5173
npx kill-port 5173
npm run dev
```

### API Not Connected
1. Check backend is running (port 8000)
2. Verify `.env` has correct URL
3. Check browser console for CORS errors

### Build Fails
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📱 Testing Features

### Weapons Page
- Browse weapons
- Filter by type/class
- Search by name
- Click any weapon for details

### AI Chat
- Ask questions about builds
- View context sources
- See conversation history

### Build Planner
- Allocate SPECIAL stats
- Save builds locally
- Share via URL

---

## 🎨 Tech Stack Quick Reference

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Tailwind + DaisyUI** - Styling
- **GSAP** - Animations
- **Vite** - Build tool
- **HashRouter** - Client routing

---

## 📚 Next Steps

1. Read [FRONTEND_README.md](./FRONTEND_README.md) for full documentation
2. Check [DEVELOPMENT_GUIDELINES.md](./DEVELOPMENT_GUIDELINES.md) for code patterns
3. Explore the codebase structure in `src/`

---

## 💡 Tips

- **Hot Reload**: Changes update instantly
- **Type Safety**: Let TypeScript catch errors
- **Component Library**: Use DaisyUI classes
- **GSAP**: All animations are in component files
- **API Types**: Defined in `src/types/api.ts`

Happy building! 🎮
