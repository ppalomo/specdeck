import { ACCENTS, type Accent } from '../theme/tokens'

/**
 * Which of the eight accents a repository wears.
 *
 * Worked out from the identifier rather than stored, so it is the same on every screen and
 * after every restart without the registry having to remember anything. If somebody ever
 * wants to choose, that becomes a field on the registry and this becomes the default.
 */
export function accentOf(repoId: string): Accent {
  let sum = 0
  for (const character of repoId) sum = (sum * 31 + character.charCodeAt(0)) % 100_000

  return ACCENTS[sum % ACCENTS.length] ?? 1
}

const TEXT: Record<Accent, string> = {
  1: 'text-accent-1',
  2: 'text-accent-2',
  3: 'text-accent-3',
  4: 'text-accent-4',
  5: 'text-accent-5',
  6: 'text-accent-6',
  7: 'text-accent-7',
  8: 'text-accent-8',
}

const BACKGROUND: Record<Accent, string> = {
  1: 'bg-accent-1',
  2: 'bg-accent-2',
  3: 'bg-accent-3',
  4: 'bg-accent-4',
  5: 'bg-accent-5',
  6: 'bg-accent-6',
  7: 'bg-accent-7',
  8: 'bg-accent-8',
}

export const accentText = (repoId: string): string => TEXT[accentOf(repoId)]
export const accentBackground = (repoId: string): string => BACKGROUND[accentOf(repoId)]
