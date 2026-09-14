import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it } from 'vitest'

import { THEME_ATTRIBUTE } from './theme'
import { useTheme } from './useTheme'

describe('changing the theme', () => {
  beforeEach(() => {
    window.localStorage.clear()
    document.documentElement.setAttribute(THEME_ATTRIBUTE, 'dark')
  })

  it('starts from what the document is already showing', () => {
    document.documentElement.setAttribute(THEME_ATTRIBUTE, 'light')

    const { result } = renderHook(() => useTheme())

    expect(result.current.theme).toBe('light')
  })

  it('applies and remembers the other one', () => {
    const { result } = renderHook(() => useTheme())

    act(() => {
      result.current.toggle()
    })

    expect(result.current.theme).toBe('light')
    expect(document.documentElement.getAttribute(THEME_ATTRIBUTE)).toBe('light')
  })

  it('goes back', () => {
    const { result } = renderHook(() => useTheme())

    act(() => {
      result.current.toggle()
    })
    act(() => {
      result.current.toggle()
    })

    expect(result.current.theme).toBe('dark')
  })
})
