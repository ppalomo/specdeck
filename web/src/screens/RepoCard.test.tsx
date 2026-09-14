import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { RepoCard } from './RepoCard'
import { aChange, aRepo, anIndex } from './fixtures'
import { renderInRouter } from './router-harness'

describe('a repository at a glance', () => {
  it('says how much is done, how much is in flight and how much it describes', async () => {
    await renderInRouter(
      <RepoCard
        repo={aRepo()}
        index={anIndex({
          changes: [aChange({ tasks: { groups: [], total: 25, done: 12 } })],
          specs: [{ id: 'a', purpose: null, requirements: [], requirement_count: 1, touched_by: [] }],
        })}
      />,
    )

    expect(screen.getByText('specdeck')).toBeTruthy()
    expect(screen.getByText('12/25')).toBeTruthy()
    expect(screen.getByText('1 change in flight')).toBeTruthy()
    expect(screen.getByText('1 capability')).toBeTruthy()
  })

  it('says when the path has gone, and why', async () => {
    await renderInRouter(
      <RepoCard
        repo={aRepo({ availability: { available: false, reason: 'the path no longer exists' } })}
      />,
    )

    // Not a zero. "Nothing here" and "could not look" lead somewhere different.
    expect(screen.getByText('the path no longer exists')).toBeTruthy()
    expect(screen.queryByText('0/0')).toBeNull()
  })

  it('says when the CLI could not be asked, without hiding what was read', async () => {
    await renderInRouter(
      <RepoCard
        repo={aRepo({
          canonical: { available: false, reason: 'the openspec executable is not installed' },
        })}
        index={anIndex({ changes: [aChange({ tasks: { groups: [], total: 4, done: 1 } })] })}
      />,
    )

    expect(screen.getByText(/validation unavailable/)).toBeTruthy()
    expect(screen.getByText(/not installed/)).toBeTruthy()
    // What the disk did say is still there.
    expect(screen.getByText('1/4')).toBeTruthy()
  })

  it('marks a store as one', async () => {
    await renderInRouter(<RepoCard repo={aRepo({ kind: 'store' })} index={anIndex()} />)

    expect(screen.getByText('store')).toBeTruthy()
  })
})
