import { readFileSync, readdirSync } from 'node:fs'
import { resolve } from 'node:path'

import { describe, expect, it } from 'vitest'

import { GRID, RADII, onTheGrid } from '../src/theme/tokens'

/**
 * Every spacing on the 4 px grid, every radius one of three.
 *
 * A value outside the grid is a decision nobody took — somebody nudged something by 3 px
 * because it looked better in the one place they were looking. Enough of those and two
 * screens written a month apart stop looking like the same product, and by then there is no
 * single thing to fix.
 */
const components = resolve(import.meta.dirname, '../src')

function sourcesUnder(directory: string): string[] {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = resolve(directory, entry.name)
    if (entry.isDirectory()) return sourcesUnder(path)
    if (!/\.tsx?$/.test(entry.name) || entry.name.includes('.test.')) return []
    return [path]
  })
}

const sources = sourcesUnder(components).map((path) => ({
  name: path.slice(components.length + 1),
  text: readFileSync(path, 'utf8'),
}))

/**
 * Tailwind spacing utilities, in the forms the components use them.
 *
 * A fraction like `w-3/4` is a proportion of its container rather than a length, so it is
 * not on this grid and is not asked to be.
 */
const SPACINGS = /\b(?:p|px|py|pt|pr|pb|pl|m|mx|my|gap|gap-x|gap-y|size|w|h)-(\d+)(?![\d/])/g
const RADIUS = /\brounded-\[(\d+)px\]/g

describe('the grid', () => {
  it('is what the interface is built on', () => {
    expect(sources.length).toBeGreaterThan(5)
  })

  it.each(sources)('holds in $name', ({ text }) => {
    for (const [utility, value] of text.matchAll(SPACINGS)) {
      expect(onTheGrid(Number(value)), `${utility} is not on the ${String(GRID)} px grid`).toBe(
        true,
      )
    }
  })

  it.each(sources)('has only the three radii in $name', ({ text }) => {
    for (const [utility, value] of text.matchAll(RADIUS)) {
      expect(
        Object.values(RADII),
        `${utility} is not one of the three radii`,
      ).toContain(Number(value))
    }
  })
})
