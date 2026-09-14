import { readFileSync } from 'node:fs'
import { resolve as resolvePath } from 'node:path'

import { describe, expect, it } from 'vitest'

import { contrast } from '../src/theme/contrast'
import { ACCENTS, LAYERS, OPERATIONS, STATUSES, TEXT } from '../src/theme/tokens'

/**
 * Every colour that carries meaning, over every layer it can sit on, in both themes.
 *
 * The values are read out of `index.css` rather than repeated here: the stylesheet is where
 * they live, and a second copy would drift by the second week and then agree with itself
 * while disagreeing with the product.
 */
const READABLE = 4.5

const css = readFileSync(resolvePath(import.meta.dirname, '../src/index.css'), 'utf8')

function declarationsOf(selector: string): Map<string, string> {
  const block = new RegExp(`${selector}\\s*\\{([^}]*)\\}`, 's').exec(css)
  const found = new Map<string, string>()
  if (block === null) return found

  const declarations = block[1] ?? ''
  for (const [, name, value] of declarations.matchAll(/(--colour-[\w-]+)\s*:\s*([^;]+);/g)) {
    if (name !== undefined && value !== undefined) found.set(name, value.trim())
  }
  return found
}

const dark = declarationsOf(':root')
const light = new Map([...dark, ...declarationsOf(":root\\[data-theme='light'\\]")])

/** Follow a token through however many `var()` hops it takes to reach a colour. */
function valueOf(declarations: Map<string, string>, name: string): string {
  let value = declarations.get(name)
  for (let hop = 0; hop < 8 && value?.startsWith('var('); hop += 1) {
    value = declarations.get(value.slice(4, -1).trim())
  }
  if (value === undefined) throw new Error(`no such token: ${name}`)
  return value
}

const MEANINGFUL = [
  ...TEXT.map((name) => `--colour-${name}`),
  ...OPERATIONS.map((name) => `--colour-${name}`),
  ...STATUSES.map((name) => `--colour-${name}`),
  ...ACCENTS.map((number) => `--colour-accent-${String(number)}`),
]

describe.each([
  ['dark', dark],
  ['light', light],
] as const)('the %s theme', (theme, declarations) => {
  it('declares every token it is supposed to', () => {
    expect(declarations.size).toBeGreaterThan(0)
    for (const token of MEANINGFUL) expect(valueOf(declarations, token)).toMatch(/^oklch\(/)
  })

  it.each(MEANINGFUL)('reads %s against every layer it can sit on', (token) => {
    for (const layer of LAYERS) {
      const ratio = contrast(valueOf(declarations, token), valueOf(declarations, `--colour-${layer}`))

      expect(
        ratio,
        `${token} on --colour-${layer} in ${theme} is only ${ratio.toFixed(2)}:1`,
      ).toBeGreaterThanOrEqual(READABLE)
    }
  })
})

describe('the arithmetic itself', () => {
  it('agrees with the ratios everybody knows', () => {
    expect(contrast('oklch(100% 0 0)', 'oklch(0% 0 0)')).toBeCloseTo(21, 0)
    expect(contrast('oklch(50% 0 0)', 'oklch(50% 0 0)')).toBeCloseTo(1, 5)
  })
})
