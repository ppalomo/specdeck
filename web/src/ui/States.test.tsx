import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { Button } from './Button'
import { EmptyState, ErrorState } from './States'

describe('having nothing to show', () => {
  it('says what would be here, why it is not, and what to do', () => {
    render(
      <EmptyState
        what="No changes in flight"
        why="This repository has no change being worked on right now."
        action={<Button tone="accent">Propose one</Button>}
      />,
    )

    expect(screen.getByText('No changes in flight')).toBeTruthy()
    expect(screen.getByText(/no change being worked on/)).toBeTruthy()
    expect(screen.getByRole('button', { name: 'Propose one' })).toBeTruthy()
  })

  it('does not look like something went wrong', () => {
    render(<EmptyState what="No changes in flight" why="Nothing is being worked on." />)

    // An ordinary Tuesday is not an error, and must not be dressed as one.
    expect(screen.queryByTestId('error-state')).toBeNull()
  })
})

describe('something having gone wrong', () => {
  it('says what was being attempted and what stopped it, in the words it was given', () => {
    render(
      <ErrorState
        what="Could not reach the server"
        reason="the openspec executable is not installed or not on the PATH"
      />,
    )

    expect(screen.getByText('Could not reach the server')).toBeTruthy()
    // The server's own words, not a translation of them into something vaguer.
    expect(screen.getByText(/not installed or not on the PATH/)).toBeTruthy()
  })

  it('offers to try again, and does', () => {
    const retry = vi.fn()
    render(<ErrorState what="Could not read it" reason="the path no longer exists" onRetry={retry} />)

    screen.getByRole('button', { name: 'Try again' }).click()

    expect(retry).toHaveBeenCalledOnce()
  })

  it('does not offer to try again when there is nothing to try', () => {
    render(<ErrorState what="Could not read it" reason="the path no longer exists" />)

    expect(screen.queryByRole('button')).toBeNull()
  })
})
