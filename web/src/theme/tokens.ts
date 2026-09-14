/**
 * The token names, read back out of the stylesheet.
 *
 * Kept as names rather than values: the values live in `index.css` and nowhere else, and a
 * second copy of them here would be a second source of truth that drifts by the second week.
 */

export const LAYERS = ['base', 'surface', 'raised'] as const
export const TEXT = ['text', 'muted', 'faint'] as const
export const OPERATIONS = ['added', 'modified', 'removed', 'renamed'] as const
export const STATUSES = ['done', 'ready', 'blocked', 'skipped'] as const
export const ACCENTS = [1, 2, 3, 4, 5, 6, 7, 8] as const

export type Layer = (typeof LAYERS)[number]
export type Operation = (typeof OPERATIONS)[number]
export type Status = (typeof STATUSES)[number]
export type Accent = (typeof ACCENTS)[number]

/** The grid every spacing sits on, in pixels. */
export const GRID = 4

export function onTheGrid(pixels: number): boolean {
  return Number.isInteger(pixels / GRID)
}

/** Three radii, by the size of the thing: a control, a card, a panel. */
export const RADII = { control: 8, card: 12, panel: 16 } as const

/**
 * The class names for the layers and the accents, written out rather than built.
 *
 * Tailwind emits only the classes it can read in the source. A name assembled at runtime —
 * `bg-accent-${n}` — is never read, so the class is never emitted and the element renders
 * with no background at all: no error, no warning, just nothing there. Writing them out is
 * what makes them exist.
 */
export const LAYER_CLASS: Record<Layer, string> = {
  base: 'bg-base',
  surface: 'bg-surface',
  raised: 'bg-raised',
}

export const ACCENT_CLASS: Record<Accent, string> = {
  1: 'bg-accent-1',
  2: 'bg-accent-2',
  3: 'bg-accent-3',
  4: 'bg-accent-4',
  5: 'bg-accent-5',
  6: 'bg-accent-6',
  7: 'bg-accent-7',
  8: 'bg-accent-8',
}

export const TEXT_CLASS: Record<(typeof TEXT)[number], string> = {
  text: 'text-text',
  muted: 'text-muted',
  faint: 'text-faint',
}
