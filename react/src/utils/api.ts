import { API_BASE_URL, API_ENDPOINTS, DEFAULT_PAGE_SIZE } from '../config/constants';
import type {
  PaginatedResponse,
  Weapon,
  WeaponDetail,
  WeaponFilters,
  Armor,
  ArmorDetail,
  ArmorFilters,
  Perk,
  PerkDetail,
  PerkFilters,
  LegendaryPerk,
  LegendaryPerkDetail,
  Mutation,
  MutationDetail,
  Consumable,
  ConsumableDetail,
  RAGQueryRequest,
  RAGQueryResponse,
} from '../types/api';

// Generic fetch helper
async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.statusText}`);
  }

  return response.json();
}

// Build query string from filters
function buildQueryString<T extends Record<string, string | number | boolean | undefined | null>>(filters: T, page = 1, pageSize = DEFAULT_PAGE_SIZE): string {
  const params = new URLSearchParams();

  params.set('page', page.toString());
  params.set('page_size', pageSize.toString());

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.set(key, String(value));
    }
  });

  return params.toString();
}

// === Weapons API ===
export async function getWeapons(
  filters: WeaponFilters = {},
  page = 1,
  pageSize = DEFAULT_PAGE_SIZE
): Promise<PaginatedResponse<Weapon>> {
  const queryString = buildQueryString(filters, page, pageSize);
  return fetchAPI<PaginatedResponse<Weapon>>(`${API_ENDPOINTS.WEAPONS}?${queryString}`);
}

export async function getWeaponById(weaponId: number): Promise<WeaponDetail> {
  return fetchAPI<WeaponDetail>(`${API_ENDPOINTS.WEAPONS}/${weaponId}`);
}

export async function getWeaponTypes(): Promise<string[]> {
  return fetchAPI<string[]>(`${API_ENDPOINTS.WEAPONS}/types/list`);
}

export async function getWeaponClasses(): Promise<string[]> {
  return fetchAPI<string[]>(`${API_ENDPOINTS.WEAPONS}/classes/list`);
}

// === Armor API ===
export async function getArmor(
  filters: ArmorFilters = {},
  page = 1,
  pageSize = DEFAULT_PAGE_SIZE
): Promise<PaginatedResponse<Armor>> {
  const queryString = buildQueryString(filters, page, pageSize);
  return fetchAPI<PaginatedResponse<Armor>>(`${API_ENDPOINTS.ARMOR}?${queryString}`);
}

export async function getArmorById(armorId: number): Promise<ArmorDetail> {
  return fetchAPI<ArmorDetail>(`${API_ENDPOINTS.ARMOR}/${armorId}`);
}

export async function getArmorTypes(): Promise<string[]> {
  return fetchAPI<string[]>(`${API_ENDPOINTS.ARMOR}/types/list`);
}

export async function getArmorClasses(): Promise<string[]> {
  return fetchAPI<string[]>(`${API_ENDPOINTS.ARMOR}/classes/list`);
}

export async function getArmorSlots(): Promise<string[]> {
  return fetchAPI<string[]>(`${API_ENDPOINTS.ARMOR}/slots/list`);
}

export async function getArmorSets(): Promise<string[]> {
  return fetchAPI<string[]>(`${API_ENDPOINTS.ARMOR}/sets/list`);
}

// === Perks API ===
export async function getPerks(
  filters: PerkFilters = {},
  page = 1,
  pageSize = DEFAULT_PAGE_SIZE
): Promise<PaginatedResponse<Perk>> {
  const queryString = buildQueryString(filters, page, pageSize);
  return fetchAPI<PaginatedResponse<Perk>>(`${API_ENDPOINTS.PERKS}?${queryString}`);
}

export async function getPerkById(perkId: number): Promise<PerkDetail> {
  return fetchAPI<PerkDetail>(`${API_ENDPOINTS.PERKS}/${perkId}`);
}

export async function getLegendaryPerks(
  page = 1,
  pageSize = DEFAULT_PAGE_SIZE
): Promise<PaginatedResponse<LegendaryPerk>> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  return fetchAPI<PaginatedResponse<LegendaryPerk>>(`${API_ENDPOINTS.LEGENDARY_PERKS}?${params}`);
}

export async function getLegendaryPerkById(legendaryPerkId: number): Promise<LegendaryPerkDetail> {
  return fetchAPI<LegendaryPerkDetail>(`${API_ENDPOINTS.PERKS}/legendary/${legendaryPerkId}`);
}

export async function getSpecialList(): Promise<string[]> {
  return fetchAPI<string[]>(`${API_ENDPOINTS.PERKS}/special/list`);
}

// === Mutations API ===
export async function getMutations(
  page = 1,
  pageSize = DEFAULT_PAGE_SIZE
): Promise<PaginatedResponse<Mutation>> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  return fetchAPI<PaginatedResponse<Mutation>>(`${API_ENDPOINTS.MUTATIONS}?${params}`);
}

export async function getMutationById(mutationId: number): Promise<MutationDetail> {
  return fetchAPI<MutationDetail>(`${API_ENDPOINTS.MUTATIONS}/${mutationId}`);
}

// === Consumables API ===
export async function getConsumables(
  page = 1,
  pageSize = DEFAULT_PAGE_SIZE
): Promise<PaginatedResponse<Consumable>> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  return fetchAPI<PaginatedResponse<Consumable>>(`${API_ENDPOINTS.CONSUMABLES}?${params}`);
}

export async function getConsumableById(consumableId: number): Promise<ConsumableDetail> {
  return fetchAPI<ConsumableDetail>(`${API_ENDPOINTS.CONSUMABLES}/${consumableId}`);
}

export async function getConsumableCategories(): Promise<string[]> {
  return fetchAPI<string[]>(`${API_ENDPOINTS.CONSUMABLES}/categories/list`);
}

// === RAG API ===
export async function queryRAG(request: RAGQueryRequest): Promise<RAGQueryResponse> {
  return fetchAPI<RAGQueryResponse>(API_ENDPOINTS.RAG_QUERY, {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// === Health Check ===
export async function checkHealth(): Promise<{ status: string; database: string; version: string }> {
  return fetchAPI(API_ENDPOINTS.HEALTH);
}

// === Stats ===
export async function getStats(): Promise<{
  total_weapons: number;
  total_armor: number;
  total_perks: number;
  total_mutations: number;
  total_consumables: number;
}> {
  return fetchAPI(API_ENDPOINTS.STATS);
}
