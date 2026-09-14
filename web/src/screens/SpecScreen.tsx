import { useQuery } from '@tanstack/react-query'
import { useParams } from '@tanstack/react-router'

import { queries } from '../api/queries'
import { Skeleton } from '../ui/Skeleton'
import { ErrorState } from '../ui/States'

/** One capability, as it is in force today. */
export function SpecScreen() {
  const { repoId, _splat: specId } = useParams({ from: '/repos/$repoId/specs/$' })
  const spec = useQuery(queries.spec(repoId, specId ?? ''))

  if (spec.error !== null) {
    return (
      <ErrorState
        what={`Could not read ${specId ?? 'that capability'}`}
        reason={spec.error.message}
        onRetry={() => void spec.refetch()}
      />
    )
  }
  if (spec.data === undefined) return <Skeleton className="h-160" />

  return (
    <article className="mx-auto flex max-w-[900px] flex-col gap-32">
      <header className="flex flex-col gap-8">
        <h1 className="text-xl font-semibold break-words text-text">{spec.data.id}</h1>
        {/* A capability with no Purpose section shows its requirements anyway, rather than
            having one invented for it. */}
        {spec.data.purpose !== null && spec.data.purpose !== undefined && (
          <p className="max-w-[72ch] text-sm text-muted">{spec.data.purpose}</p>
        )}
        <p className="text-xs text-faint">
          {spec.data.requirement_count}{' '}
          {spec.data.requirement_count === 1 ? 'requirement' : 'requirements'}
        </p>
      </header>

      <div className="flex flex-col gap-24">
        {spec.data.requirements.map((requirement, position) => (
          <section key={requirement.name} className="flex flex-col gap-12">
            <h2 className="text-base font-medium text-text">
              <span className="font-mono text-xs text-faint">{position + 1}. </span>
              {requirement.name}
            </h2>
            <p className="max-w-[72ch] text-sm whitespace-pre-wrap text-muted">{requirement.text}</p>
            <div className="flex flex-col gap-8">
              {requirement.scenarios.map((scenario) => (
                <div key={scenario.name} className="flex flex-col gap-8 rounded-[12px] bg-surface p-16">
                  <h3 className="text-sm font-medium text-text">{scenario.name}</h3>
                  <dl className="flex flex-col gap-4">
                    {scenario.steps.map((step) => (
                      <Step key={step} step={step} />
                    ))}
                  </dl>
                </div>
              ))}
            </div>
          </section>
        ))}
      </div>
    </article>
  )
}

/** A scenario step, shown as the condition and the outcome it is rather than as a bullet. */
function Step({ step }: { step: string }) {
  const plain = step.replaceAll('**', '')
  const [, keyword = '', rest = plain] = /^(WHEN|THEN|AND|GIVEN)\s+(.*)$/s.exec(plain) ?? []

  return (
    <div className="flex items-start gap-8">
      <dt className="w-48 shrink-0 font-mono text-xs font-medium text-faint">{keyword}</dt>
      <dd className="text-sm text-muted">{rest}</dd>
    </div>
  )
}
