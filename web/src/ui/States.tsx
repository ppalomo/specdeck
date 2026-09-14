import { FileQuestion, TriangleAlert } from 'lucide-react'
import type { ReactNode } from 'react'

import { Button } from './Button'
import { classes } from './classes'

/**
 * The two screens that are usually left until last and end up looking like a crash.
 *
 * Both say the same three things, because those are the three a person needs: what would be
 * here, why it is not, and what to do now. They look different from each other on purpose —
 * a repository with no changes in flight is an ordinary Tuesday, and it must not read as
 * something having gone wrong.
 */

function Frame({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div
      className={classes(
        'flex flex-col items-center gap-12 rounded-[12px] px-24 py-40 text-center',
        className,
      )}
    >
      {children}
    </div>
  )
}

export function EmptyState({
  what,
  why,
  action,
}: {
  /** What would be here, if there were any. */
  what: string
  /** Why there is not, in words that are not an apology. */
  why: string
  action?: ReactNode
}) {
  return (
    <Frame className="bg-surface">
      <FileQuestion aria-hidden size={20} strokeWidth={1.75} className="text-faint" />
      <p className="text-base font-medium text-text">{what}</p>
      <p className="max-w-[48ch] text-sm text-muted">{why}</p>
      {action}
    </Frame>
  )
}

export function ErrorState({
  what,
  reason,
  onRetry,
}: {
  /** What was being attempted when it failed. */
  what: string
  /** What stopped it, in the words the server used rather than ours. */
  reason: string
  onRetry?: () => void
}) {
  return (
    <Frame className="bg-surface" data-testid="error-state">
      <TriangleAlert aria-hidden size={20} strokeWidth={1.75} className="text-removed" />
      <p className="text-base font-medium text-text">{what}</p>
      <p className="max-w-[48ch] font-mono text-xs text-muted">{reason}</p>
      {onRetry !== undefined && (
        <Button tone="quiet" size="small" onClick={onRetry}>
          Try again
        </Button>
      )}
    </Frame>
  )
}
