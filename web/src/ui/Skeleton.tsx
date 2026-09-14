import type { ReactNode } from 'react'

import { classes } from './classes'

/**
 * The shape of what is coming, while it is coming.
 *
 * Only the first time. Refreshing is not loading: something that is already on screen and is
 * being checked for changes must not be replaced by a grey rectangle, or every refresh reads
 * as the interface losing its place.
 */
export function Skeleton({ className }: { className?: string }) {
  return (
    <span
      data-testid="skeleton"
      aria-hidden
      className={classes('block animate-pulse rounded-[8px] bg-raised', className)}
    />
  )
}

export function Loading({
  when,
  skeleton,
  children,
}: {
  /** True only while there is nothing to show yet. */
  when: boolean
  skeleton: ReactNode
  children: ReactNode
}) {
  return when ? <>{skeleton}</> : <>{children}</>
}
