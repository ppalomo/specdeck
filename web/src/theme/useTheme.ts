import { useCallback, useState } from 'react'

import { type Theme, applyTheme, currentTheme } from './theme'

/** The theme, and the one way to change it. */
export function useTheme(): { theme: Theme; setTheme: (theme: Theme) => void; toggle: () => void } {
  const [theme, remember] = useState<Theme>(currentTheme)

  const setTheme = useCallback((next: Theme) => {
    applyTheme(next)
    remember(next)
  }, [])

  const toggle = useCallback(() => {
    setTheme(currentTheme() === 'dark' ? 'light' : 'dark')
  }, [setTheme])

  return { theme, setTheme, toggle }
}
