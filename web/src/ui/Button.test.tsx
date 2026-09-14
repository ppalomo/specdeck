import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Button } from './Button'

describe('a button', () => {
  it('says what it is for', () => {
    render(<Button>Validate</Button>)

    expect(screen.getByRole('button', { name: 'Validate' })).toBeTruthy()
  })

  it('never submits a form by accident', () => {
    render(<Button>Open in editor</Button>)

    expect(screen.getByRole('button').getAttribute('type')).toBe('button')
  })

  it('lets a caller override what the variant decided', () => {
    render(<Button className="px-24">Copy command</Button>)

    // Not "px-16 px-24", which would leave the browser to pick one.
    const className = screen.getByRole('button').className
    expect(className).toContain('px-24')
    expect(className).not.toContain('px-16')
  })

  it('cannot be pressed when it is disabled', () => {
    render(<Button disabled>Archive</Button>)

    expect(screen.getByRole('button').hasAttribute('disabled')).toBe(true)
  })
})
