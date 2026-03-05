/**
 * Placeholder utilities for prompt templates.
 *
 * Handles detection, extraction, and replacement of {{name}} patterns
 * in prompt template strings.
 */

/** Extract unique placeholder names from template text. */
export function extractPlaceholders(template: string): string[] {
  const matches = template.match(/\{\{([^}]+)\}\}/g) || []
  const names = matches.map(m => m.slice(2, -2).trim())
  return [...new Set(names)]
}

/** Returns true if the text still contains unfilled {{...}} placeholders. */
export function hasUnfilledPlaceholders(text: string): boolean {
  return /\{\{[^}]+\}\}/.test(text)
}

/** Replace all {{name}} placeholders with corresponding values. */
export function fillPlaceholders(
  template: string,
  values: Record<string, string>,
): string {
  return template.replace(/\{\{([^}]+)\}\}/g, (_match, name: string) => {
    const trimmed = name.trim()
    return values[trimmed] !== undefined ? values[trimmed] : `{{${trimmed}}}`
  })
}
