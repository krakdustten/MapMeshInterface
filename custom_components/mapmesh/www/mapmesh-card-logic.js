/** Pure helpers for the MapMe Lovelace card (testable in Node). */

export const HERO_STAT_DEFS = [
  { key: "unique_hexes", label: "Hexes" },
  { key: "total_samples", label: "Samples" },
  { key: "active_days", label: "Days" },
];

export const MORE_STAT_DEFS = [
  { key: "pioneer_hexes", label: "Pioneer hexes" },
  { key: "unique_repeaters", label: "Repeaters" },
  { key: "rx_hexes", label: "RX hexes" },
  { key: "days_since_first", label: "Days since first" },
  { key: "road_trip_peak", label: "Road trip peak" },
  { key: "grinder_peak", label: "Grinder peak" },
];

const ICON_EMOJI = {
  map: "🗺️",
  fire: "🔥",
  chart: "📊",
  car: "🚗",
  sunrise: "🌅",
  rocket: "🚀",
  satellite: "📡",
  signal: "📡",
  dish: "📡",
  flame: "🔥",
};

const TIER_ORDER = ["bronze", "silver", "gold", "platinum", "diamond"];

const TIER_DISPLAY = {
  bronze: "Bronze",
  silver: "Silver",
  gold: "Gold",
  platinum: "Platinum",
  diamond: "Diamond",
};

/**
 * @param {unknown} value
 * @returns {string}
 */
export function formatNumber(value) {
  if (value === null || value === undefined || value === "") return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return "—";
  return n.toLocaleString();
}

/**
 * @param {{ value?: unknown, next?: unknown } | null | undefined} badge
 * @returns {number | null}
 */
export function badgeProgress(badge) {
  if (!badge) return null;
  const { value, next } = badge;
  if (value === null || value === undefined || next === null || next === undefined) {
    return null;
  }
  const nextN = Number(next);
  if (!nextN || Number.isNaN(nextN)) return null;
  const valueN = Number(value);
  if (Number.isNaN(valueN)) return null;
  return Math.min(100, Math.round((valueN / nextN) * 100));
}

/**
 * @param {Record<string, unknown> | null | undefined} attrs
 * @returns {{ key: string, label: string, value: unknown }[]}
 */
export function heroStats(attrs) {
  const source = attrs || {};
  return HERO_STAT_DEFS.map(({ key, label }) => ({
    key,
    label,
    value: source[key],
  }));
}

/**
 * Secondary stats excluding the hero trio. Omits missing/null values.
 * @param {Record<string, unknown> | null | undefined} attrs
 * @returns {{ key: string, label: string, value: unknown }[]}
 */
export function moreStats(attrs) {
  const source = attrs || {};
  const heroKeys = new Set(HERO_STAT_DEFS.map((d) => d.key));
  return MORE_STAT_DEFS.filter(({ key }) => {
    if (heroKeys.has(key)) return false;
    const value = source[key];
    return value !== null && value !== undefined && value !== "";
  }).map(({ key, label }) => ({
    key,
    label,
    value: source[key],
  }));
}

/**
 * @param {string | null | undefined} icon
 * @returns {string}
 */
export function iconEmoji(icon) {
  if (!icon) return "🏅";
  return ICON_EMOJI[icon] || "🏅";
}

/**
 * @param {string | null | undefined} tier
 * @returns {string | null}
 */
export function nextTierLabel(tier) {
  if (!tier) return null;
  const idx = TIER_ORDER.indexOf(String(tier).toLowerCase());
  if (idx < 0 || idx >= TIER_ORDER.length - 1) return null;
  return TIER_DISPLAY[TIER_ORDER[idx + 1]];
}

/**
 * @param {{ value?: unknown, next?: unknown, tier?: string, label?: string } | null | undefined} badge
 * @returns {{ current: string, goal: string | null } | null}
 */
export function progressFooter(badge) {
  if (!badge || badge.value === null || badge.value === undefined) return null;
  const current = formatNumber(badge.value);
  if (badge.next === null || badge.next === undefined) {
    return { current, goal: null };
  }
  const nextName = nextTierLabel(badge.tier) || "next";
  return {
    current,
    goal: `${formatNumber(badge.next)} for ${nextName}`,
  };
}

/**
 * @param {unknown} text
 * @returns {string}
 */
export function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
