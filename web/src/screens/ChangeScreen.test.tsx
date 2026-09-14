import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { ChangeScreen } from './ChangeScreen'
import { aChange } from './fixtures'
import { queries } from '../api/queries'

/**
 * The change screen reads its change from the route, so these mount it with the query already
 * answered rather than with a server behind it.
 */
async function showing(change: ReturnType<typeof aChange>) {
  const { renderWithData } = await import('./query-harness')
  return renderWithData(<ChangeScreen />, [
    [queries.change('r', 'add-reminders').queryKey, change],
  ])
}

describe('the pipeline of a change', () => {
  it('keeps its hole rather than tidying it', async () => {
    await showing(
      aChange({
        artifacts: [
          { id: 'proposal', status: 'done', files: [], requires: [] },
          { id: 'design', status: 'ready', files: [], requires: [] },
          { id: 'tasks', status: 'done', files: [], requires: [] },
        ],
      }),
    )

    // Tasks written while design is not is ordinary, and reordering it would show something
    // the disk does not say.
    const shown = screen.getAllByText(/^(done|ready)$/).map((node) => node.textContent)
    expect(shown).toEqual(['done', 'ready', 'done'])
  })

  it('says the pipeline is unavailable rather than inventing one', async () => {
    await showing(aChange({ artifacts: [] }))

    expect(screen.getByText(/pipeline is unavailable/)).toBeTruthy()
  })
})

describe('the tasks of a change', () => {
  const withTasks = aChange({
    tasks: {
      total: 2,
      done: 1,
      groups: [
        {
          title: '1. El modelo',
          location: { file: 'openspec/changes/add-reminders/tasks.md', line: 1 },
          tasks: [
            {
              number: '1.1',
              text: 'Añadir la hora',
              done: true,
              location: { file: 'openspec/changes/add-reminders/tasks.md', line: 3 },
            },
            {
              number: '1.2',
              text: 'Escribir el envío',
              done: false,
              location: { file: 'openspec/changes/add-reminders/tasks.md', line: 5 },
            },
          ],
        },
      ],
    },
  })

  it('shows them in the groups they are written in, with what is left', async () => {
    await showing(withTasks)

    expect(screen.getByText('1. El modelo')).toBeTruthy()
    // Twice over: the change's own progress in the header, and the group's beside its title.
    expect(screen.getAllByText('1/2')).toHaveLength(2)
    expect(screen.getByText(/Escribir el envío/)).toBeTruthy()
  })

  it('says which file and line each task is written on', async () => {
    await showing(withTasks)

    expect(screen.getByText('openspec/changes/add-reminders/tasks.md:5')).toBeTruthy()
  })

  it('cannot be ticked, because Specdeck never writes to a repository', async () => {
    await showing(withTasks)

    const boxes = screen.getAllByRole('checkbox')
    expect(boxes.every((box) => (box as HTMLInputElement).disabled)).toBe(true)

    boxes[1]?.click()
    expect((boxes[1] as HTMLInputElement).checked).toBe(false)
  })
})

describe('the validation of a change', () => {
  it('counts errors and warnings apart', async () => {
    await showing(
      aChange({
        validation: {
          valid: true,
          errors: 0,
          warnings: 2,
          issues: [
            { level: 'WARNING', path: 'specs/a/spec.md', message: 'should contain SHALL' },
            { level: 'WARNING', path: 'specs/b/spec.md', message: 'should contain SHALL' },
          ],
        },
      }),
    )

    screen.getByRole('tab', { name: 'Validation' }).click()

    // Two warnings and still valid. One mixed number would read as "2 problems".
    expect(await screen.findByText(/Valid · 0 errors · 2 warnings/)).toBeTruthy()
  })

  it('says when there is nothing to validate against', async () => {
    await showing(aChange({ validation: null }))

    screen.getByRole('tab', { name: 'Validation' }).click()

    expect(await screen.findByText('Validation unavailable')).toBeTruthy()
  })
})


describe('the prose of a change', () => {
  it('shows an artifact as a tab of its own, named after the artifact', async () => {
    await showing(
      aChange({
        // Given to the screen the way the disk gives them: sorted by filename, so design
        // first. What is shown has to follow the schema, not the alphabet.
        artifacts: [
          { id: 'proposal', status: 'done', files: [], requires: [] },
          { id: 'design', status: 'done', files: [], requires: [] },
        ],
        documents: [
          { artifact: 'design', file: 'openspec/changes/x/design.md', text: '## Context\n\nEsto.' },
          { artifact: 'proposal', file: 'openspec/changes/x/proposal.md', text: '## Why\n\nPorque sí.' },
        ],
      }),
    )

    // What tabs exist follows from what the change has, not from a list written here, and
    // they come in the order the schema puts the artifacts in rather than alphabetically.
    const tabs = screen.getAllByRole('tab').map((tab) => tab.textContent)
    expect(tabs).toEqual(['Proposal', 'Design', 'Tasks', 'Deltas', 'Validation'])
  })

  it('renders it when its tab is chosen', async () => {
    await showing(
      aChange({
        documents: [
          { artifact: 'proposal', file: 'openspec/changes/x/proposal.md', text: '## Why\n\nPorque sí.' },
        ],
      }),
    )

    screen.getByRole('tab', { name: 'Proposal' }).click()

    expect(await screen.findByText('Porque sí.')).toBeTruthy()
  })

  it('offers no prose tabs for a change whose artifacts could not be read', async () => {
    await showing(aChange({ documents: [] }))

    expect(screen.queryByRole('tab', { name: 'Proposal' })).toBeNull()
    expect(screen.getByRole('tab', { name: 'Tasks' })).toBeTruthy()
  })
})
