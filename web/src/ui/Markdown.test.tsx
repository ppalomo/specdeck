import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Markdown } from './Markdown'

describe('an artifact read as a document', () => {
  it('renders its headings, lists and emphasis', () => {
    render(
      <Markdown>{'## Why\n\nPorque sí.\n\n- Una cosa\n- **Otra**\n'}</Markdown>,
    )

    expect(screen.getByRole('heading', { name: 'Why' })).toBeTruthy()
    expect(screen.getByText('Porque sí.')).toBeTruthy()
    expect(screen.getAllByRole('listitem')).toHaveLength(2)
    expect(screen.getByText('Otra').tagName).toBe('STRONG')
  })

  it('caps the column at a reading width however wide the window is', () => {
    render(<Markdown>{'Una línea larga de prosa.'}</Markdown>)

    // A line that crosses a 27-inch screen is not read, it is scanned.
    expect(screen.getByText('Una línea larga de prosa.').className).toContain('max-w-[72ch]')
  })

  it('gives a wide table its own scrolling box, so the page never moves sideways', () => {
    const { container } = render(
      <Markdown>{'| One | Two |\n| --- | --- |\n| a | b |\n'}</Markdown>,
    )

    const table = container.querySelector('table')
    expect(table).not.toBeNull()
    expect(table?.parentElement?.className).toContain('overflow-x-auto')
  })

  it('keeps a code block inside its own box too', () => {
    const { container } = render(<Markdown>{'```\nopenspec list --json\n```\n'}</Markdown>)

    expect(container.querySelector('pre')?.className).toContain('overflow-x-auto')
  })
})
