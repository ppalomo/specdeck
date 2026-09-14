import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Loading, Skeleton } from './Skeleton'

describe('waiting for something for the first time', () => {
  it('shows the shape of what is coming', () => {
    render(
      <Loading when skeleton={<Skeleton className="h-40" />}>
        <p>Two changes</p>
      </Loading>,
    )

    expect(screen.getByTestId('skeleton')).toBeTruthy()
    expect(screen.queryByText('Two changes')).toBeNull()
  })
})

describe('refreshing something already on screen', () => {
  it('is not loading, so nothing is replaced by a grey rectangle', () => {
    render(
      <Loading when={false} skeleton={<Skeleton className="h-40" />}>
        <p>Two changes</p>
      </Loading>,
    )

    expect(screen.queryByTestId('skeleton')).toBeNull()
    expect(screen.getByText('Two changes')).toBeTruthy()
  })
})

describe('a skeleton', () => {
  it('is not read out, because it says nothing', () => {
    render(<Skeleton className="h-40" />)

    expect(screen.getByTestId('skeleton').getAttribute('aria-hidden')).toBe('true')
  })
})
