import { motion, useReducedMotion } from 'motion/react'
import type { ReactNode } from 'react'

/**
 * Content arriving, rather than appearing out of nowhere.
 *
 * Used where something replaces a skeleton or is revealed. Deliberately small: a fade and a
 * few pixels, inside the system's range, because the point is to let the eye follow what
 * changed and not to put on a show.
 *
 * Somebody who has asked their system for less movement gets none. Shortening a transition
 * is still movement, and the setting exists for people to whom that matters more than it
 * does to whoever wrote the animation.
 */
export function Appear({ children, className }: { children: ReactNode; className?: string }) {
  const still = useReducedMotion()

  if (still === true) {
    return <div className={className}>{children}</div>
  }

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: [0.22, 0.61, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}
