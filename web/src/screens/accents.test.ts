import { describe, expect, it } from 'vitest'

import { accentOf } from '../app/accents'

describe('the accent a repository wears', () => {
  it('is the same one every time, so a card is recognisable without reading it', () => {
    expect(accentOf('specdeck-dbd3eb')).toBe(accentOf('specdeck-dbd3eb'))
  })

  it('is one of the eight', () => {
    for (const id of ['a', 'specdeck-dbd3eb', 'full-ff9a0a', 'x-000000']) {
      expect(accentOf(id)).toBeGreaterThanOrEqual(1)
      expect(accentOf(id)).toBeLessThanOrEqual(8)
    }
  })

  it('spreads across all eight rather than favouring one', () => {
    const worn = new Set(
      Array.from({ length: 60 }, (_, index) => accentOf(`repo-${String(index)}abc`)),
    )

    expect(worn.size).toBeGreaterThanOrEqual(6)
  })
})
