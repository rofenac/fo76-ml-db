// API Response Types

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Weapon Types
export interface Weapon {
  weapon_id: number;
  name: string;
  type: string;
  weapon_class: string;
  damage: number;
  fire_rate: number | null;
  range: number | null;
  accuracy: number | null;
  ap_cost: number | null;
  ammo_capacity: number | null;
  ammo_type: string | null;
  level_requirement: number;
  weight: number;
  value: number;
  two_shot_modifier: number | null;
  aae_modifier: number | null;
  bloodied_modifier: number | null;
  furious_modifier: number | null;
  vampire_modifier: number | null;
  damage_per_action_point: number | null;
  dps: number | null;
}

export interface WeaponDetail extends Weapon {
  damage_type?: string;
  related_perks?: string[];
  affected_perks?: Perk[];
  notes?: string;
}

// Armor Types
export interface Armor {
  armor_id: number;
  name: string;
  type: string;
  armor_class: string;
  slot: string;
  set_name: string | null;
  damage_resistance: number;
  energy_resistance: number;
  radiation_resistance: number;
  level_requirement: number;
  weight: number;
  value: number;
  ballistic_weave: boolean;
  ultralight: boolean;
}

export interface ArmorDetail extends Armor {
  set_pieces?: Armor[];
  related_perks?: string[];
  notes?: string;
}

// Perk Types
export interface Perk {
  perk_id: number;
  name: string;
  special_stat: string;
  max_rank: number;
  level_requirement: number;
  description: string;
}

export interface PerkRank {
  rank: number;
  description: string;
  cost: number;
}

export interface PerkDetail extends Perk {
  ranks: PerkRank[];
  related_items?: string[];
}

export interface LegendaryPerk {
  legendary_perk_id: number;
  name: string;
  max_rank: number;
  description: string;
}

export interface LegendaryPerkDetail extends LegendaryPerk {
  ranks: PerkRank[];
}

// Mutation Types
export interface Mutation {
  mutation_id: number;
  name: string;
  positive_effects: string;
  negative_effects: string;
  suppression_perk: string | null;
}

export interface MutationDetail extends Mutation {
  related_perks?: Perk[];
  notes?: string;
}

// Consumable Types
export interface Consumable {
  consumable_id: number;
  name: string;
  category: string;
  effects: string;
  duration_minutes: number | null;
  weight: number;
  value: number;
}

export interface ConsumableDetail extends Consumable {
  related_perks?: string[];
  notes?: string;
}

// RAG Types
export interface RAGQueryRequest {
  query: string;
  max_results?: number;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  context_used: ContextItem[];
  total_results: number;
  processing_time: number;
}

export interface ContextItem {
  item_id: number;
  item_name: string;
  item_type: string;
  similarity: number;
  snippet?: string;
}

// Filter Types
export interface WeaponFilters {
  type?: string;
  weapon_class?: string;
  min_damage?: number;
  max_damage?: number;
  ammo_type?: string;
  search?: string;
}

export interface ArmorFilters {
  type?: string;
  armor_class?: string;
  slot?: string;
  set_name?: string;
  search?: string;
}

export interface PerkFilters {
  special_stat?: string;
  search?: string;
}

// Build Types
export interface CharacterBuild {
  id?: string;
  name: string;
  description: string;
  level: number;
  special_stats: SpecialStats;
  perks: BuildPerk[];
  legendary_perks: BuildLegendaryPerk[];
  weapons: number[]; // weapon_ids
  armor: number[]; // armor_ids
  mutations: number[]; // mutation_ids
  consumables: number[]; // consumable_ids
  created_at?: string;
  updated_at?: string;
}

export interface SpecialStats {
  strength: number;
  perception: number;
  endurance: number;
  charisma: number;
  intelligence: number;
  agility: number;
  luck: number;
}

export interface BuildPerk {
  perk_id: number;
  rank: number;
}

export interface BuildLegendaryPerk {
  legendary_perk_id: number;
  rank: number;
}
