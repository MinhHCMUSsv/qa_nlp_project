/**
 * Utility formatters for text display.
 */

/**
 * Truncate text to a maximum length with ellipsis.
 * @param {string} text
 * @param {number} maxLength
 * @returns {string}
 */
export function truncate(text, maxLength = 200) {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "...";
}

/**
 * Format a similarity score as a percentage.
 * @param {number} score - Score between 0 and 1
 * @returns {string}
 */
export function formatScore(score) {
  return `${(score * 100).toFixed(1)}%`;
}
