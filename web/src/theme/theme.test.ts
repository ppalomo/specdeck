import { beforeEach, describe, expect, it } from 'vitest'

import { DEFAULT_THEME, THEME_ATTRIBUTE, THEME_KEY, applyTheme, currentTheme, storedTheme } from './theme'

describe('the theme', () => {
  beforeEach(() => {
    window.localStorage.clear()
    document.documentElement.setAttribute(THEME_ATTRIBUTE, 'dark')
  })

  it('is dark for someone who has never chosen', () => {
    expect(storedTheme()).toBe('dark')
    expect(DEFAULT_THEME).toBe('dark')
  })

  it('is remembered between sessions', () => {
    applyTheme('light')

    expect(window.localStorage.getItem(THEME_KEY)).toBe('light')
    // A new session reads the same answer back before anything is rendered.
    expect(storedTheme()).toBe('light')
  })

  it('is on the document itself, which is what the HTML already set', () => {
    applyTheme('light')

    expect(document.documentElement.getAttribute(THEME_ATTRIBUTE)).toBe('light')
    expect(currentTheme()).toBe('light')
  })

  it('falls back to the default when what was stored is nonsense', () => {
    window.localStorage.setItem(THEME_KEY, 'neon')

    expect(storedTheme()).toBe('dark')
  })
})
