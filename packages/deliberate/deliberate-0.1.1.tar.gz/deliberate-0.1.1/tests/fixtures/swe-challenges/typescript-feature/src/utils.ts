/**
 * String utilities library.
 * Task: Add a new function to validate email addresses.
 */

export function capitalize(str: string): string {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function truncate(str: string, maxLength: number): string {
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - 3) + '...';
}

export function slugify(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
}

// TODO: Add isValidEmail function
// Requirements:
// - Return true for valid emails like "user@example.com"
// - Return false for invalid emails like "user@" or "@example.com"
// - Handle edge cases like empty strings
