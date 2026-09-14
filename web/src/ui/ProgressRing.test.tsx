import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ProgressRing } from './ProgressRing'

describe('the progress of a change', () => {
  it('says the numbers, not only the drawing', () => {
    render(<ProgressRing done={12} total={25} />)

    expect(screen.getByText('12/25')).toBeTruthy()
    expect(screen.getByRole('img', { name: '12 of 25 tasks done' })).toBeTruthy()
  })

  it('fills the ring in proportion', () => {
    const { container } = render(<ProgressRing done={1} total={4} />)
    const [, filled] = container.querySelectorAll('circle')
    const circumference = Number(filled?.getAttribute('stroke-dasharray'))

    // A quarter done leaves three quarters of the ring still to draw.
    expect(Number(filled?.getAttribute('stroke-dashoffset'))).toBeCloseTo(circumference * 0.75, 5)
  })

  it('closes the ring when everything is done', () => {
    const { container } = render(<ProgressRing done={9} total={9} />)
    const [, filled] = container.querySelectorAll('circle')

    expect(Number(filled?.getAttribute('stroke-dashoffset'))).toBeCloseTo(0, 5)
  })

  it('says there are no tasks rather than drawing nought per cent', () => {
    render(<ProgressRing done={0} total={0} />)

    // "Nothing to do yet" and "none of this has been done" lead somewhere different.
    expect(screen.getByText('No tasks yet')).toBeTruthy()
    expect(screen.queryByText('0/0')).toBeNull()
  })

  it('moves from one value to the next instead of jumping', () => {
    const { container } = render(<ProgressRing done={3} total={10} />)
    const [, filled] = container.querySelectorAll('circle')

    expect(filled?.getAttribute('style')).toContain('stroke-dashoffset')
  })
})
