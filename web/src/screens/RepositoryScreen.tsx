import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Link, useParams } from '@tanstack/react-router'
import { RefreshCw } from 'lucide-react'

import type { Change, Index, Spec } from '../api/client'
import { api } from '../api/client'
import { queries } from '../api/queries'
import { accentText } from '../app/accents'
import { OperationLabel } from '../ui/Label'
import { Button } from '../ui/Button'
import { Card } from '../ui/Card'
import { ProgressRing } from '../ui/ProgressRing'
import { Skeleton } from '../ui/Skeleton'
import { EmptyState, ErrorState } from '../ui/States'
import { classes } from '../ui/classes'
import { operationOf } from '../ui/operations'

const COLUMNS: { status: Change['status']; title: string }[] = [
  { status: 'planning', title: 'Planning' },
  { status: 'in-progress', title: 'In progress' },
  { status: 'complete', title: 'Complete' },
  { status: 'archived', title: 'Archived' },
]

export function RepositoryScreen() {
  const { repoId } = useParams({ from: '/repos/$repoId' })
  const index = useQuery(queries.index(repoId))
  const queryClient = useQueryClient()

  const read = useMutation({
    mutationFn: () => api.read(repoId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['repos'] })
    },
  })

  if (index.error !== null) {
    return (
      <ErrorState
        what="Could not read this repository"
        reason={index.error.message}
        onRetry={() => void index.refetch()}
      />
    )
  }

  if (index.data === undefined) return <Skeleton className="h-160" />

  return (
    <div className="mx-auto flex max-w-[1100px] flex-col gap-32">
      <Header
        index={index.data}
        reading={read.isPending}
        onRead={() => {
          read.mutate()
        }}
      />
      <Board index={index.data} repoId={repoId} />
      <Capabilities index={index.data} repoId={repoId} />
    </div>
  )
}

function Header({
  index,
  reading,
  onRead,
}: {
  index: Index
  reading: boolean
  onRead: () => void
}) {
  return (
    <header className="flex items-start justify-between gap-16">
      <div className="flex flex-col gap-4">
        <h1 className={classes('text-xl font-semibold', accentText(index.repo.id))}>
          {index.repo.name}
        </h1>
        <p className="font-mono text-xs text-faint">{index.repo.path}</p>
        <p className="text-xs text-muted">
          {index.schema_name ?? 'no schema'} · read <Read at={index.built_at} />
        </p>
      </div>
      <Button tone="quiet" size="small" onClick={onRead} disabled={reading}>
        <RefreshCw aria-hidden size={16} strokeWidth={1.75} />
        {reading ? 'Reading…' : 'Read again'}
      </Button>
    </header>
  )
}

/**
 * When what is on screen was read.
 *
 * Nothing watches the files yet, so this ages silently. Saying when it was read is the only
 * honest answer to "is this current?" that can be given today.
 */
function Read({ at }: { at: string }) {
  return <time dateTime={at}>{new Date(at).toLocaleTimeString()}</time>
}

function Board({ index, repoId }: { index: Index; repoId: string }) {
  const all = [...index.changes, ...index.archived]

  if (all.length === 0) {
    return (
      <EmptyState
        what="No changes yet"
        why="This repository has no changes in openspec/changes/, active or archived."
      />
    )
  }

  return (
    <section className="grid grid-cols-4 gap-16">
      {COLUMNS.map(({ status, title }) => {
        const column = all.filter((change) => change.status === status)
        return (
          <div key={status} className="flex flex-col gap-8">
            <h2 className="text-sm font-medium text-muted">
              {title} <span className="text-faint">{column.length}</span>
            </h2>
            {/* An empty column is information: that nothing is complete is worth seeing. */}
            {column.length === 0 ? (
              <p className="rounded-[8px] bg-surface px-12 py-16 text-xs text-faint">None</p>
            ) : (
              column.map((change) => (
                <ChangeCard key={change.id} change={change} repoId={repoId} />
              ))
            )}
          </div>
        )
      })}
    </section>
  )
}

function ChangeCard({ change, repoId }: { change: Change; repoId: string }) {
  const done = change.artifacts.filter((artifact) => artifact.status === 'done').length

  return (
    <Card className="p-12">
      <Link
        to="/repos/$repoId/changes/$changeId"
        params={{ repoId, changeId: change.id }}
        className="flex flex-col gap-8"
      >
        <span className="text-sm font-medium break-words text-text">{change.id}</span>
        <ProgressRing done={change.tasks.done} total={change.tasks.total} />
        <span className="text-xs text-faint">
          {done}/{change.artifacts.length} artifacts · {change.deltas.length} deltas
        </span>
      </Link>
    </Card>
  )
}

function Capabilities({ index, repoId }: { index: Index; repoId: string }) {
  if (index.specs.length === 0) {
    return (
      <EmptyState
        what="No capabilities yet"
        why="Nothing has been synced into openspec/specs/ in this repository."
      />
    )
  }

  return (
    <section className="flex flex-col gap-16">
      <h2 className="text-lg font-medium text-text">Capabilities</h2>
      <div className="grid grid-cols-3 gap-16">
        {index.specs.map((spec) => (
          <Card key={spec.id} className="p-12">
            <Link
              to="/repos/$repoId/specs/$"
              params={{ repoId, _splat: spec.id }}
              className="flex flex-col gap-8"
            >
              <span className="text-sm font-medium break-words text-text">{spec.id}</span>
              <span className="text-xs text-faint">
                {spec.requirement_count}{' '}
                {spec.requirement_count === 1 ? 'requirement' : 'requirements'}
              </span>
              <TouchedBy spec={spec} />
            </Link>
          </Card>
        ))}
      </div>
    </section>
  )
}

/** Which active changes are proposing something about this capability — as the server says. */
function TouchedBy({ spec }: { spec: Spec }) {
  if (spec.touched_by.length === 0) return null

  return (
    <div className="flex flex-wrap items-center gap-4">
      {spec.touched_by.map(({ change, operation }) => (
        <OperationLabel key={`${change}/${operation}`} operation={operationOf(operation)} />
      ))}
    </div>
  )
}
