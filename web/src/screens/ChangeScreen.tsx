import { useQuery } from '@tanstack/react-query'
import { useParams } from '@tanstack/react-router'
import { useState } from 'react'

import type { Artifact, ArtifactDocument, Change, Issue, TaskGroup } from '../api/client'
import { queries } from '../api/queries'
import { OperationLabel, StatusLabel } from '../ui/Label'
import { Markdown } from '../ui/Markdown'
import { ProgressRing } from '../ui/ProgressRing'
import { Skeleton } from '../ui/Skeleton'
import { EmptyState, ErrorState } from '../ui/States'
import { classes } from '../ui/classes'
import { operationOf, statusOf } from '../ui/operations'

const FIXED = ['Tasks', 'Deltas', 'Validation'] as const

export function ChangeScreen() {
  const { repoId, changeId } = useParams({ from: '/repos/$repoId/changes/$changeId' })
  const change = useQuery(queries.change(repoId, changeId))
  const [tab, setTab] = useState<string>('Tasks')

  if (change.error !== null) {
    return (
      <ErrorState
        what={`Could not read ${changeId}`}
        reason={change.error.message}
        onRetry={() => void change.refetch()}
      />
    )
  }
  if (change.data === undefined) return <Skeleton className="h-160" />

  const written = change.data.documents.find((one) => titleOf(one) === tab)

  return (
    <div className="mx-auto flex max-w-[900px] flex-col gap-32">
      <header className="flex flex-col gap-12">
        <h1 className="text-xl font-semibold break-words text-text">{change.data.id}</h1>
        <div className="flex items-center gap-16">
          <StatusOfChange change={change.data} />
          <ProgressRing done={change.data.tasks.done} total={change.data.tasks.total} />
        </div>
        <Pipeline artifacts={change.data.artifacts} />
      </header>

      <nav className="flex flex-wrap gap-8" role="tablist">
        {[...inSchemaOrder(change.data).map(titleOf), ...FIXED].map((name) => (
          <button
            key={name}
            type="button"
            role="tab"
            aria-selected={tab === name}
            onClick={() => {
              setTab(name)
            }}
            className={classes(
              'rounded-[8px] px-12 py-8 text-sm transition-colors duration-150',
              tab === name ? 'bg-raised text-text' : 'text-muted hover:text-text',
            )}
          >
            {name}
          </button>
        ))}
      </nav>

      {written !== undefined && <Markdown>{written.text}</Markdown>}
      {tab === 'Tasks' && <Tasks groups={change.data.tasks.groups} />}
      {tab === 'Deltas' && <Deltas change={change.data} />}
      {tab === 'Validation' && <Validation change={change.data} />}
    </div>
  )
}

/**
 * The prose tabs, in the order the root's schema puts its artifacts in.
 *
 * A proposal is written before a design, and reading them the other way round is reading
 * them backwards. Sorting by name would have said Design, Proposal — which is alphabetical
 * and wrong.
 */
function inSchemaOrder(change: Change): ArtifactDocument[] {
  const order = new Map(change.artifacts.map((artifact, position) => [artifact.id, position]))
  const last = change.artifacts.length

  return [...change.documents].sort(
    (one, other) => (order.get(one.artifact) ?? last) - (order.get(other.artifact) ?? last),
  )
}

/** An artifact's tab is its own name, capitalised: the schema decides what there is. */
function titleOf(document: ArtifactDocument): string {
  return document.artifact.charAt(0).toUpperCase() + document.artifact.slice(1)
}

function StatusOfChange({ change }: { change: Change }) {
  return (
    <span className="font-mono text-xs uppercase text-muted">
      {change.status}
      {change.archived_on !== null && change.archived_on !== undefined && ` · ${change.archived_on}`}
    </span>
  )
}

/**
 * The artifacts, in the order the root's own schema declares them.
 *
 * A hole is normal and is left alone: tasks written while design is not is an ordinary state
 * of a change, and tidying it would show something the disk does not say.
 */
function Pipeline({ artifacts }: { artifacts: Artifact[] }) {
  if (artifacts.length === 0) {
    return (
      <p className="text-xs text-muted">
        The pipeline is unavailable — the OpenSpec CLI could not be asked about this
        repository.
      </p>
    )
  }

  return (
    <ol className="flex flex-wrap items-center gap-8">
      {artifacts.map((artifact) => (
        <li key={artifact.id} className="flex items-center gap-8">
          <span className="flex items-center gap-4">
            <span className="text-xs text-muted">{artifact.id}</span>
            <StatusLabel status={statusOf(artifact.status)} />
          </span>
        </li>
      ))}
    </ol>
  )
}

function Tasks({ groups }: { groups: TaskGroup[] }) {
  if (groups.length === 0) {
    return <EmptyState what="No tasks" why="This change has no tasks.md, or it has no checkboxes in it." />
  }

  return (
    <div className="flex flex-col gap-24">
      {groups.map((group) => {
        const done = group.tasks.filter((task) => task.done).length
        return (
          <section key={`${group.location.file}:${String(group.location.line)}`} className="flex flex-col gap-8">
            <div className="flex items-center justify-between gap-16">
              <h2 className="text-base font-medium text-text">{group.title}</h2>
              <ProgressRing done={done} total={group.tasks.length} />
            </div>
            <ul className="flex flex-col gap-4">
              {group.tasks.map((task) => (
                <li
                  key={`${task.location.file}:${String(task.location.line)}`}
                  className="flex items-start gap-8 rounded-[8px] bg-surface px-12 py-8"
                >
                  {/* Read-only on purpose. Specdeck never writes to a repository, and a
                      checkbox that looks clickable promises otherwise. */}
                  <input
                    type="checkbox"
                    checked={task.done}
                    readOnly
                    disabled
                    aria-label={task.text}
                    className="mt-4"
                  />
                  <span className="flex min-w-0 flex-col gap-4">
                    <span className={classes('text-sm', task.done ? 'text-faint' : 'text-text')}>
                      {task.number !== '' && (
                        <span className="font-mono text-xs text-faint">{task.number} </span>
                      )}
                      {task.text}
                    </span>
                    <span className="font-mono text-xs text-faint">
                      {task.location.file}:{task.location.line}
                    </span>
                  </span>
                </li>
              ))}
            </ul>
          </section>
        )
      })}
    </div>
  )
}

function Deltas({ change }: { change: Change }) {
  if (change.deltas.length === 0) {
    return <EmptyState what="No deltas" why="This change proposes no change to any capability." />
  }

  const byCapability = new Map<string, typeof change.deltas>()
  for (const delta of change.deltas) {
    byCapability.set(delta.capability, [...(byCapability.get(delta.capability) ?? []), delta])
  }

  return (
    <div className="flex flex-col gap-24">
      {[...byCapability].map(([capability, deltas]) => (
        <section key={capability} className="flex flex-col gap-12">
          <h2 className="text-base font-medium text-text">{capability}</h2>
          {deltas.map((delta) => (
            <div key={delta.operation} className="flex flex-col gap-8">
              <OperationLabel operation={operationOf(delta.operation)} />
              {delta.requirements.map((requirement) => (
                <div key={requirement.name} className="flex flex-col gap-8 rounded-[12px] bg-surface p-16">
                  <h3 className="text-sm font-medium text-text">{requirement.name}</h3>
                  <p className="max-w-[72ch] text-sm text-muted">{requirement.text}</p>
                  {requirement.scenarios.map((scenario) => (
                    <div key={scenario.name} className="flex flex-col gap-4 rounded-[8px] bg-raised p-12">
                      <span className="text-xs font-medium text-text">{scenario.name}</span>
                      {scenario.steps.map((step) => (
                        <span key={step} className="font-mono text-xs text-muted">
                          {step.replaceAll('**', '')}
                        </span>
                      ))}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          ))}
        </section>
      ))}
    </div>
  )
}

/**
 * Errors and warnings, counted apart.
 *
 * A repository whose specs are written in Spanish carries hundreds of standing style
 * warnings while passing every check. One number that adds the levels together turns "this
 * is fine" into "there are 165 problems".
 */
function Validation({ change }: { change: Change }) {
  if (change.validation === null || change.validation === undefined) {
    return (
      <EmptyState
        what="Validation unavailable"
        why="The OpenSpec CLI could not be asked about this repository, so nothing here has been checked."
      />
    )
  }

  const { valid, issues, errors, warnings } = change.validation

  return (
    <div className="flex flex-col gap-16">
      <p className="text-sm text-text">
        {valid ? 'Valid' : 'Not valid'} · {errors} {errors === 1 ? 'error' : 'errors'} ·{' '}
        {warnings} {warnings === 1 ? 'warning' : 'warnings'}
      </p>
      {issues.length === 0 ? (
        <EmptyState what="Nothing to report" why="OpenSpec found nothing to say about this change." />
      ) : (
        <ul className="flex flex-col gap-4">
          {issues.map((issue, position) => (
            <IssueLine key={`${issue.path}:${String(position)}`} issue={issue} />
          ))}
        </ul>
      )}
    </div>
  )
}

function IssueLine({ issue }: { issue: Issue }) {
  const tone =
    issue.level === 'ERROR' ? 'text-removed' : issue.level === 'WARNING' ? 'text-modified' : 'text-faint'

  return (
    <li className="flex items-start gap-8 rounded-[8px] bg-surface px-12 py-8">
      <span className={classes('font-mono text-xs font-medium', tone)}>{issue.level}</span>
      <span className="flex min-w-0 flex-col gap-4">
        <span className="text-sm text-text">{issue.message}</span>
        <span className="font-mono text-xs text-faint">{issue.path}</span>
      </span>
    </li>
  )
}
