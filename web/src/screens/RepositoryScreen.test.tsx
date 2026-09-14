import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { RepositoryScreen } from './RepositoryScreen'
import { aChange, aSpec, anIndex } from './fixtures'
import { renderWithData } from './query-harness'
import { queries } from '../api/queries'

async function showing(index: ReturnType<typeof anIndex>) {
  return renderWithData(<RepositoryScreen />, [[queries.index('r').queryKey, index]], '/repos/r')
}

describe('the header of a repository', () => {
  it('says where it is, what schema it follows and when this was read', async () => {
    await showing(anIndex())

    expect(await screen.findByText('/Users/someone/specdeck')).toBeTruthy()
    expect(screen.getByText(/spec-driven/)).toBeTruthy()
    // Nothing watches the files, so when it was read is the only honest answer to
    // "is this current?".
    expect(screen.getByText(/read/)).toBeTruthy()
    expect(screen.getByRole('button', { name: /Read again/ })).toBeTruthy()
  })
})

describe('the changes of a repository', () => {
  it('puts each one under its state', async () => {
    await showing(
      anIndex({
        changes: [aChange({ id: 'flying', status: 'in-progress' })],
        archived: [aChange({ id: 'filed', status: 'archived', archived_on: '2026-08-01' })],
      }),
    )

    expect(await screen.findByText('flying')).toBeTruthy()
    expect(screen.getByText('filed')).toBeTruthy()
    expect(screen.getByText('In progress')).toBeTruthy()
    expect(screen.getByText('Archived')).toBeTruthy()
  })

  it('says a column is empty rather than hiding it', async () => {
    await showing(anIndex({ changes: [aChange({ status: 'in-progress' })] }))

    // That nothing is complete is information. A column that disappears hides it.
    expect(await screen.findAllByText('None')).toHaveLength(3)
  })

  it('says a repository with no changes has none, without looking broken', async () => {
    await showing(anIndex({ changes: [], archived: [] }))

    expect(await screen.findByText('No changes yet')).toBeTruthy()
    expect(screen.queryByTestId('error-state')).toBeNull()
  })
})

describe('the capabilities of a repository', () => {
  it('lists them with their requirement counts', async () => {
    await showing(anIndex({ specs: [aSpec({ id: 'reports', requirement_count: 3 })] }))

    expect(await screen.findByText('reports')).toBeTruthy()
    expect(screen.getByText('3 requirements')).toBeTruthy()
  })

  it('says which active changes are touching one, and how', async () => {
    await showing(
      anIndex({
        specs: [
          aSpec({
            id: 'reports',
            touched_by: [{ change: 'retire-old-reports', operation: 'MODIFIED' }],
          }),
        ],
      }),
    )

    expect(await screen.findByText('modified')).toBeTruthy()
  })
})
