/**
 * Utility functions for formatting data
 */

export function formatNumber(num: number | null | undefined, decimals = 0): string {
  if (num === null || num === undefined) return 'N/A';
  return num.toFixed(decimals);
}

export function formatPercent(num: number | null | undefined, decimals = 1): string {
  if (num === null || num === undefined) return 'N/A';
  return `${(num * 100).toFixed(decimals)}%`;
}

export function formatWeight(weight: number | null | undefined): string {
  if (weight === null || weight === undefined) return 'N/A';
  return `${weight.toFixed(1)} lbs`;
}

export function formatValue(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';
  return `${value} caps`;
}

export function formatDuration(minutes: number | null | undefined): string {
  if (minutes === null || minutes === undefined) return 'Permanent';
  if (minutes < 60) return `${minutes}m`;
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
}

export function formatDamage(damage: number | null | undefined): string {
  if (damage === null || damage === undefined) return 'N/A';
  return damage.toString();
}

export function formatRange(range: number | null | undefined): string {
  if (range === null || range === undefined) return 'N/A';
  return `${range}m`;
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function formatSpecialStat(stat: string): string {
  const statMap: Record<string, string> = {
    strength: 'S',
    perception: 'P',
    endurance: 'E',
    charisma: 'C',
    intelligence: 'I',
    agility: 'A',
    luck: 'L',
  };
  return statMap[stat.toLowerCase()] || stat;
}

export function getRarityColor(value: number | null | undefined, max: number): string {
  if (value === null || value === undefined) return 'text-gray-400';
  const percentage = (value / max) * 100;

  if (percentage >= 80) return 'text-purple-400'; // Legendary
  if (percentage >= 60) return 'text-blue-400';   // Rare
  if (percentage >= 40) return 'text-green-400';  // Uncommon
  return 'text-gray-400';                         // Common
}

export function getStatColor(stat: string): string {
  const colorMap: Record<string, string> = {
    strength: 'text-red-400',
    perception: 'text-yellow-400',
    endurance: 'text-orange-400',
    charisma: 'text-pink-400',
    intelligence: 'text-blue-400',
    agility: 'text-green-400',
    luck: 'text-purple-400',
  };
  return colorMap[stat.toLowerCase()] || 'text-gray-400';
}
