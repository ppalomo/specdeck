import { Link } from '@tanstack/react-router'
import { TriangleAlert } from 'lucide-react'

import type { Index, RegisteredRepo } from '../api/client'
import { accentText } from '../app/accents'
import { Card } from '../ui/Card'
import { ProgressRing } from '../ui/ProgressRing'
import { classes } from '../ui/classes'

/**
 * One registered repository, at a glance.
 *
 * Both things that can be missing are said out loud: a root whose path has gone, and a root
 * whose canonical state could not be read because the OpenSpec CLI is not on the machine.
 * Either one silently rendered as zero would be a card that reads "nothing to do here".
 */
export function RepoCard({ repo, index }: { repo: RegisteredRepo; index?: Index | undefined }) {
  const active = index?.changes ?? []
  const done = active.reduce((count, change) => count + change.tasks.done, 0)
  const total = active.reduce((count, change) => count + change.tasks.total, 0)

  return (
    <Card className="transition-shadow hover:shadow-[var(--shadow-raised)]">
      <Link to="/repos/$repoId" params={{ repoId: repo.id }} className="flex flex-col gap-16">
        <div className="flex items-start justify-between gap-16">
          <div className="flex min-w-0 flex-col gap-4">
            <span className={classes('text-base font-semibold', accentText(repo.id))}>
              {repo.name}
            </span>
            <span className="truncate font-mono text-xs text-faint">{repo.path}</span>
          </div>
          {repo.availability.available && <ProgressRing done={done} total={total} />}
        </div>

        {!repo.availability.available ? (
          <Unavailable reason={repo.availability.reason ?? 'it could not be read'} />
        ) : (
          <div className="flex items-center gap-16 text-xs text-muted">
            <span>
              {active.length} {active.length === 1 ? 'change' : 'changes'} in flight
            </span>
            <span>
              {index?.specs.length ?? 0}{' '}
              {(index?.specs.length ?? 0) === 1 ? 'capability' : 'capabilities'}
            </span>
            {repo.kind === 'store' && <span className="text-faint">store</span>}
          </div>
        )}

        {repo.availability.available && repo.canonical?.available === false && (
          <Unavailable reason={`validation unavailable — ${repo.canonical.reason ?? 'unknown'}`} />
        )}
      </Link>
    </Card>
  )
}

function Unavailable({ reason }: { reason: string }) {
  return (
    <p className="flex items-start gap-8 text-xs text-muted">
      <TriangleAlert aria-hidden size={16} strokeWidth={1.75} className="shrink-0 text-modified" />
      {reason}
    </p>
  )
}
