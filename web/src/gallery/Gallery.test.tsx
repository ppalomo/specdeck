import { render, screen } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { Gallery } from './Gallery'
import { OPERATIONS, STATUSES } from '../theme/tokens'
import { THEME_ATTRIBUTE } from '../theme/theme'

beforeEach(() => {
  window.localStorage.clear()
  document.documentElement.setAttribute(THEME_ATTRIBUTE, 'dark')
  vi.stubGlobal(
    'fetch',
    vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ name: 'Specdeck', status: 'ok', version: '0.1.0' }),
      }),
    ),
  )
})

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('the design system, shown', () => {
  it.each(OPERATIONS)('shows what %s looks like', (operation) => {
    render(<Gallery />)

    expect(screen.getByText(operation)).toBeTruthy()
  })

  it.each(STATUSES)('shows what %s looks like', (status) => {
    render(<Gallery />)

    expect(screen.getAllByText(status).length).toBeGreaterThan(0)
  })

  it('shows a change at every stage of being done, including having nothing to do', () => {
    render(<Gallery />)

    expect(screen.getByText('12/25')).toBeTruthy()
    expect(screen.getByText('9/9')).toBeTruthy()
    expect(screen.getByText('No tasks yet')).toBeTruthy()
  })

  it('shows both of the states that are usually left until last', () => {
    render(<Gallery />)

    expect(screen.getByText('No changes in flight')).toBeTruthy()
    expect(screen.getByText('Could not read this repository')).toBeTruthy()
  })

  it('lets the theme be changed from the page itself', () => {
    render(<Gallery />)

    screen.getByRole('button', { name: 'Switch theme' }).click()

    expect(document.documentElement.getAttribute(THEME_ATTRIBUTE)).toBe('light')
  })

  it('still says which server is on the other end', async () => {
    render(<Gallery />)

    expect((await screen.findByTestId('version')).textContent).toBe('0.1.0')
  })
})
