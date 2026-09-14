import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { SpecScreen } from './SpecScreen'
import { aSpec } from './fixtures'
import { renderWithData } from './query-harness'
import { queries } from '../api/queries'

async function showing(spec: ReturnType<typeof aSpec>) {
  return renderWithData(
    <SpecScreen />,
    [[queries.spec('r', 'task-management').queryKey, spec]],
    '/repos/r/specs/task-management',
  )
}

const withRequirements = aSpec({
  requirement_count: 1,
  requirements: [
    {
      name: 'Una tarea se puede dar por hecha',
      text: 'La aplicación DEBE permitir marcarla.',
      location: { file: 'openspec/specs/task-management/spec.md', line: 8 },
      scenarios: [
        {
          name: 'Marcar una tarea',
          location: { file: 'openspec/specs/task-management/spec.md', line: 13 },
          steps: ['**WHEN** alguien la marca', '**THEN** queda hecha'],
        },
      ],
    },
  ],
})

describe('reading a capability', () => {
  it('shows its purpose, its requirements and their scenarios', async () => {
    await showing(withRequirements)

    expect(await screen.findByText(/Qué puede hacer alguien/)).toBeTruthy()
    expect(screen.getByText('Una tarea se puede dar por hecha')).toBeTruthy()
    expect(screen.getByText('Marcar una tarea')).toBeTruthy()
  })

  it('shows a scenario as the condition and the outcome it is', async () => {
    await showing(withRequirements)

    // Not a bullet list indistinguishable from the prose around it.
    expect(await screen.findByText('WHEN')).toBeTruthy()
    expect(screen.getByText('THEN')).toBeTruthy()
    expect(screen.getByText('alguien la marca')).toBeTruthy()
  })

  it('shows the requirements of a capability that never wrote a purpose', async () => {
    await showing(aSpec({ ...withRequirements, purpose: null }))

    expect(await screen.findByText('Una tarea se puede dar por hecha')).toBeTruthy()
    expect(screen.queryByText(/Qué puede hacer alguien/)).toBeNull()
  })
})
