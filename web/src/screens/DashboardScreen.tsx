import { useQueries, useQuery } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'

import { RegisterRepo } from './RegisterRepo'
import { RepoCard } from './RepoCard'
import type { Change, Index, RegisteredRepo } from '../api/client'
import { queries } from '../api/queries'
import { accentText } from '../app/accents'
import { Card } from '../ui/Card'
import { ProgressRing } from '../ui/ProgressRing'
import { Skeleton } from '../ui/Skeleton'
import { EmptyState, ErrorState } from '../ui/States'
import { classes } from '../ui/classes'

/** What Specdeck opens on: where every registered repository stands, and what is in flight. */
export function DashboardScreen() {
  const repos = useQuery(queries.repos())
  const indexes = useQueries({
    queries: (repos.data ?? []).map((repo) => queries.index(repo.id)),
  })

  const known = new Map<string, Index>()
  for (const [position, result] of indexes.entries()) {
    const repo = repos.data?.[position]
    if (repo !== undefined && result.data !== undefined) known.set(repo.id, result.data)
  }

  return (
    <div className="mx-auto flex max-w-[1100px] flex-col gap-32">
      <div className="flex flex-col gap-16">
        <h1 className="text-xl font-semibold text-text">Repositories</h1>
        <RegisterRepo />
      </div>

      {repos.isPending && <Skeletons />}

      {repos.error !== null && (
        <ErrorState
          what="Could not reach the Specdeck server"
          reason={repos.error.message}
          onRetry={() => void repos.refetch()}
        />
      )}

      {repos.data?.length === 0 && (
        <EmptyState
          what="No repositories yet"
          why="Register the path of a repository that has an openspec/ directory, and its changes, specs and tasks will appear here."
        />
      )}

      {repos.data !== undefined && repos.data.length > 0 && (
        <>
          <section className="grid grid-cols-2 gap-16">
            {repos.data.map((repo) => (
              <RepoCard key={repo.id} repo={repo} index={known.get(repo.id)} />
            ))}
          </section>
          <InFlight repos={repos.data} indexes={known} />
        </>
      )}
    </div>
  )
}

/**
 * Everything in flight, everywhere, most recently touched first.
 *
 * This is the question Specdeck exists to answer — what was I doing — and answering it today
 * means opening four terminals and running `openspec list` in each.
 */
function InFlight({
  repos,
  indexes,
}: {
  repos: RegisteredRepo[]
  indexes: Map<string, Index>
}) {
  const flying = repos
    .flatMap((repo) =>
      (indexes.get(repo.id)?.changes ?? [])
        .filter((change) => change.status === 'in-progress')
        .map((change) => ({ repo, change })),
    )
    .sort((one, other) => touched(other.change) - touched(one.change))

  return (
    <section className="flex flex-col gap-16">
      <h2 className="text-lg font-medium text-text">In flight now</h2>
      {flying.length === 0 ? (
        <EmptyState
          what="Nothing in flight"
          why="No change is being worked on in any registered repository right now."
        />
      ) : (
        <div className="flex flex-col gap-8">
          {flying.map(({ repo, change }) => (
            <Card key={`${repo.id}/${change.id}`} className="py-12">
              <Link
                to="/repos/$repoId/changes/$changeId"
                params={{ repoId: repo.id, changeId: change.id }}
                className="flex items-center justify-between gap-16"
              >
                <div className="flex min-w-0 flex-col gap-4">
                  <span className="truncate text-sm font-medium text-text">{change.id}</span>
                  <span className={classes('text-xs', accentText(repo.id))}>{repo.name}</span>
                </div>
                <ProgressRing done={change.tasks.done} total={change.tasks.total} />
              </Link>
            </Card>
          ))}
        </div>
      )}
    </section>
  )
}

function touched(change: Change): number {
  const when = change.last_modified
  return when === null || when === undefined ? 0 : Date.parse(when)
}

function Skeletons() {
  return (
    <div className="grid grid-cols-2 gap-16">
      <Skeleton className="h-112" />
      <Skeleton className="h-112" />
    </div>
  )
}
