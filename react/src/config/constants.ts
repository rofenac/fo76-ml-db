// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Endpoints
export const API_ENDPOINTS = {
  WEAPONS: '/api/weapons',
  ARMOR: '/api/armor',
  PERKS: '/api/perks',
  LEGENDARY_PERKS: '/api/perks/legendary',
  MUTATIONS: '/api/mutations',
  CONSUMABLES: '/api/consumables',
  RAG_QUERY: '/api/rag/query',
  STATS: '/stats',
  HEALTH: '/health',
} as const;

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// SPECIAL Stats
export const SPECIAL_STATS = [
  { key: 'strength', label: 'Strength', abbr: 'S', color: 'text-red-400' },
  { key: 'perception', label: 'Perception', abbr: 'P', color: 'text-yellow-400' },
  { key: 'endurance', label: 'Endurance', abbr: 'E', color: 'text-orange-400' },
  { key: 'charisma', label: 'Charisma', abbr: 'C', color: 'text-pink-400' },
  { key: 'intelligence', label: 'Intelligence', abbr: 'I', color: 'text-blue-400' },
  { key: 'agility', label: 'Agility', abbr: 'A', color: 'text-green-400' },
  { key: 'luck', label: 'Luck', abbr: 'L', color: 'text-purple-400' },
] as const;

export const MIN_SPECIAL = 1;
export const MAX_SPECIAL = 15;

// Level Constraints
export const MAX_LEVEL = 1000;
export const LEGENDARY_PERK_UNLOCK_LEVEL = 50;

// Weapon Types
export const WEAPON_TYPES = [
  'Ranged',
  'Melee',
  'Thrown',
  'Placed',
  'Heavy',
] as const;

// Armor Types
export const ARMOR_TYPES = [
  'Regular Armor',
  'Power Armor',
] as const;

// Armor Slots
export const ARMOR_SLOTS = [
  'Helmet',
  'Chest',
  'Left Arm',
  'Right Arm',
  'Left Leg',
  'Right Leg',
] as const;

// Theme Colors (Fallout-inspired)
export const THEME_COLORS = {
  primary: '#60A5FA', // blue-400
  secondary: '#34D399', // green-400
  accent: '#FBBF24', // yellow-400
  warning: '#F59E0B', // orange-500
  error: '#EF4444', // red-500
  success: '#10B981', // green-500
  info: '#3B82F6', // blue-500
} as const;

// Animation Durations (in seconds)
export const ANIMATION = {
  fast: 0.3,
  normal: 0.5,
  slow: 0.8,
  verySlow: 1.2,
} as const;

// LocalStorage Keys
export const STORAGE_KEYS = {
  BUILDS: 'fo76_character_builds',
  CURRENT_BUILD: 'fo76_current_build',
  FAVORITES: 'fo76_favorites',
  RECENT_SEARCHES: 'fo76_recent_searches',
} as const;
