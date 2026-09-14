import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Card } from './Card'

describe('a card', () => {
  it('stands off the background by its layer and its shadow, not by a border', () => {
    render(<Card data-testid="card">Nothing yet</Card>)
    const className = screen.getByTestId('card').className

    expect(className).toContain('bg-surface')
    expect(className).toContain('shadow-[var(--shadow-surface)]')
    expect(className).not.toMatch(/\bborder\b/)
  })
})
