/**
 * Which theme the interface is in, and where that is remembered.
 *
 * The choice is applied to the root element by a script in the HTML, before anything is
 * downloaded — see `index.html`. Anything that waits for React to mount happens after the
 * first paint, and by then the wrong theme has already been seen. This module is the part
 * that runs afterwards: reading the choice back, and changing it.
 */

export type Theme = 'dark' | 'light'

/** Dark is not the absence of a choice. It is the one Specdeck is designed in. */
export const DEFAULT_THEME: Theme = 'dark'

export const THEME_KEY = 'specdeck.theme'
export const THEME_ATTRIBUTE = 'data-theme'

export function isTheme(value: unknown): value is Theme {
  return value === 'dark' || value === 'light'
}

/** What was chosen last time, or the default when nothing was. */
export function storedTheme(): Theme {
  try {
    const stored: unknown = window.localStorage.getItem(THEME_KEY)
    return isTheme(stored) ? stored : DEFAULT_THEME
  } catch {
    // A browser with storage denied still gets an interface, in the default theme.
    return DEFAULT_THEME
  }
}

/** The theme the document is showing right now, which the HTML has already set. */
export function currentTheme(): Theme {
  const applied = document.documentElement.getAttribute(THEME_ATTRIBUTE)
  return isTheme(applied) ? applied : storedTheme()
}

export function applyTheme(theme: Theme): void {
  document.documentElement.setAttribute(THEME_ATTRIBUTE, theme)
  try {
    window.localStorage.setItem(THEME_KEY, theme)
  } catch {
    // Not remembering it is worse than not applying it, but only a little.
  }
}
