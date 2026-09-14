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

/** The 4 px grid, as the spacings a component may use. */
export const SPACING = [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64] as const

/** Three radii, by the size of the thing: a control, a card, a panel. */
export const RADII = { control: 8, card: 12, panel: 16 } as const
