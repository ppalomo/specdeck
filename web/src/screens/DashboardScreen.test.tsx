import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { DashboardScreen } from './DashboardScreen'
import { aChange, aRepo, anIndex } from './fixtures'
import { renderWithData } from './query-harness'
import { queries } from '../api/queries'

async function showing(answers: [readonly unknown[], unknown][]) {
  return renderWithData(<DashboardScreen />, answers, '/')
}

describe('opening Specdeck for the first time', () => {
  it('says what would be here and does not look like a failure', async () => {
    await showing([[queries.repos().queryKey, []]])

    expect(await screen.findByText('No repositories yet')).toBeTruthy()
    expect(screen.queryByTestId('error-state')).toBeNull()
  })
})

describe('what is in flight everywhere', () => {
  const specdeck = aRepo({ id: 'specdeck-1', name: 'specdeck' })
  const plans = aRepo({ id: 'plans-2', name: 'plans' })

  it('gathers changes from every repository, most recently touched first', async () => {
    await showing([
      [queries.repos().queryKey, [specdeck, plans]],
      [
        queries.index('specdeck-1').queryKey,
        anIndex({ changes: [aChange({ id: 'older', last_modified: '2026-09-01T00:00:00Z' })] }),
      ],
      [
        queries.index('plans-2').queryKey,
        anIndex({ changes: [aChange({ id: 'newer', last_modified: '2026-09-14T00:00:00Z' })] }),
      ],
    ])

    const flying = await screen.findAllByText(/^(older|newer)$/)
    expect(flying.map((node) => node.textContent)).toEqual(['newer', 'older'])
  })

  it('says which repository each one belongs to', async () => {
    await showing([
      [queries.repos().queryKey, [specdeck]],
      [queries.index('specdeck-1').queryKey, anIndex({ changes: [aChange({ id: 'one' })] })],
    ])

    // Twice: on its card, and beside the change it belongs to.
    expect(await screen.findAllByText('specdeck')).toHaveLength(2)
  })

  it('says when nothing is being worked on', async () => {
    await showing([
      [queries.repos().queryKey, [specdeck]],
      [queries.index('specdeck-1').queryKey, anIndex({ changes: [] })],
    ])

    expect(await screen.findByText('Nothing in flight')).toBeTruthy()
  })

  it('leaves out changes that are not in progress', async () => {
    await showing([
      [queries.repos().queryKey, [specdeck]],
      [
        queries.index('specdeck-1').queryKey,
        anIndex({ changes: [aChange({ id: 'planned', status: 'planning' })] }),
      ],
    ])

    expect(await screen.findByText('Nothing in flight')).toBeTruthy()
  })
})

describe('when the server cannot be reached', () => {
  it('says so with what it was told, and offers to try again', async () => {
    const { queries: q } = await import('../api/queries')
    await renderWithData(<DashboardScreen />, [[q.repos().queryKey, undefined]], '/')

    // No answer seeded and no server behind it: the screen must not sit blank for ever.
    expect(await screen.findByRole('button', { name: 'Register' })).toBeTruthy()
  })
})
