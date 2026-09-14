import type { Change, Index, RegisteredRepo, Spec } from '../api/client'

/**
 * Answers shaped like the server's, built from the generated types.
 *
 * They are typed as the contract, so a model that changes on the server breaks these rather
 * than letting a screen be tested against a shape that no longer exists.
 */

export function aRepo(over: Partial<RegisteredRepo> = {}): RegisteredRepo {
  return {
    id: 'specdeck-abc123',
    name: 'specdeck',
    path: '/Users/someone/specdeck',
    kind: 'repo',
    availability: { available: true, reason: null },
    canonical: { available: true, reason: null },
    built_at: '2026-09-14T10:00:00Z',
    ...over,
  }
}

export function aChange(over: Partial<Change> = {}): Change {
  return {
    id: 'add-reminders',
    status: 'in-progress',
    schema_name: 'spec-driven',
    artifacts: [],
    tasks: { groups: [], total: 0, done: 0 },
    deltas: [],
    documents: [],
    validation: null,
    last_modified: '2026-09-14T09:00:00Z',
    archived_on: null,
    ...over,
  }
}

export function aSpec(over: Partial<Spec> = {}): Spec {
  return {
    id: 'task-management',
    purpose: 'Qué puede hacer alguien con sus tareas.',
    requirements: [],
    requirement_count: 0,
    touched_by: [],
    ...over,
  }
}

export function anIndex(over: Partial<Index> = {}): Index {
  return {
    repo: { id: 'specdeck-abc123', name: 'specdeck', path: '/Users/someone/specdeck', kind: 'repo', availability: { available: true, reason: null } },
    schema_name: 'spec-driven',
    specs: [],
    changes: [],
    archived: [],
    canonical: { available: true, reason: null },
    unreadable: [],
    built_at: '2026-09-14T10:00:00Z',
    ...over,
  }
}
