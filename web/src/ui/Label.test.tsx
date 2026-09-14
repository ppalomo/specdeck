import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { OperationLabel, StatusLabel } from './Label'
import { OPERATIONS, STATUSES } from '../theme/tokens'

describe('an operation label', () => {
  it.each(OPERATIONS)('writes %s as well as painting it', (operation) => {
    render(<OperationLabel operation={operation} />)

    // Readable by someone who cannot tell these four tones apart.
    expect(screen.getByText(operation)).toBeTruthy()
  })

  it.each(OPERATIONS)('paints %s in the one colour that means it', (operation) => {
    render(<OperationLabel operation={operation} />)

    expect(screen.getByText(operation).className).toContain(`text-${operation}`)
  })
})

describe('a status label', () => {
  it.each(STATUSES)('writes %s as well as painting it', (status) => {
    render(<StatusLabel status={status} />)

    expect(screen.getByText(status)).toBeTruthy()
  })

  it.each(STATUSES)('paints %s in the one colour that means it', (status) => {
    render(<StatusLabel status={status} />)

    expect(screen.getByText(status).className).toContain(`text-${status}`)
  })
})

describe('the same state in two places', () => {
  it('is the same label, because there is only one', () => {
    const { container: inAPipeline } = render(<StatusLabel status="blocked" />)
    const { container: inAList } = render(<StatusLabel status="blocked" />)

    expect(inAPipeline.innerHTML).toBe(inAList.innerHTML)
  })
})
