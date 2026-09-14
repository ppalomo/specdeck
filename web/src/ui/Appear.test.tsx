import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { Appear } from './Appear'

/** jsdom answers no media query on its own, so the one that matters here is answered for it. */
function asksForLessMovement(reduced: boolean): void {
  vi.stubGlobal(
    'matchMedia',
    vi.fn((query: string) => ({
      matches: reduced && query.includes('prefers-reduced-motion'),
      media: query,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      onchange: null,
      dispatchEvent: vi.fn(),
    })),
  )
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('content arriving', () => {
  it('is still readable for someone who asked for less movement', () => {
    asksForLessMovement(true)

    render(
      <Appear>
        <p>Two changes in flight</p>
      </Appear>,
    )

    // The whole point: no movement, and nothing lost.
    expect(screen.getByText('Two changes in flight')).toBeTruthy()
    expect(document.querySelector('[style*="opacity"]')).toBeNull()
  })

  it('moves for everybody else, and shows the same thing', () => {
    asksForLessMovement(false)

    render(
      <Appear>
        <p>Two changes in flight</p>
      </Appear>,
    )

    expect(screen.getByText('Two changes in flight')).toBeTruthy()
  })
})
