/**
 * Utility formatters for TechQA UI display conforming to DESIGN.MD tokens.
 */

/**
 * Truncate text to a maximum length with an ellipsis.
 * @param {string} text
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(text, maxLength = 200) {
  if (!text || text.length <= maxLength) return text || "";
  return text.slice(0, maxLength).trim() + "...";
}

/**
 * Format a similarity score as a percentage string.
 * @param {number} score - Score between 0.0 and 1.0
 * @returns {string}
 */
export function formatScore(score) {
  if (typeof score !== "number" || isNaN(score)) return "0.0%";
  return `${(score * 100).toFixed(1)}%`;
}

/**
 * Format milliseconds into a human-readable latency string.
 * @param {number} ms - Milliseconds
 * @returns {string}
 */
export function formatLatency(ms) {
  if (!ms || ms < 0) return "0ms";
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

/**
 * Get color code or badge style based on similarity score conforming to DESIGN.MD.
 * @param {number} score - Similarity score
 * @returns {{ bg: string, text: string, border: string }}
 */
export function getScoreBadgeStyle(score) {
  if (score >= 0.8) {
    return { bg: "#e8f6f2", text: "#2e8876", border: "#c2e9de" };
  }
  if (score >= 0.6) {
    return { bg: "#faf0eb", text: "#cc785c", border: "#f2d8cd" };
  }
  return { bg: "#fdf7ee", text: "#b87c33", border: "#faebd3" };
}
