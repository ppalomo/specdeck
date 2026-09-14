import type { HTMLAttributes, ReactNode } from 'react'

import { classes } from './classes'

/**
 * A card, told apart from what is under it by its layer and a soft shadow.
 *
 * Deliberately without a border. Twenty outlined cards make a grid of boxes where nothing
 * stands out, and standing out is the entire job of a dashboard.
 */
export function Card({
  className,
  children,
  ...rest
}: HTMLAttributes<HTMLDivElement> & { children: ReactNode }) {
  return (
    <div
      className={classes(
        'rounded-[12px] bg-surface p-16 shadow-[var(--shadow-surface)]',
        'transition-shadow duration-150 ease-[cubic-bezier(0.22,0.61,0.36,1)]',
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  )
}
