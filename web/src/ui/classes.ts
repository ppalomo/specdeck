import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Join class names, letting the last one about a given property win.
 *
 * Without the merge, a component's own `p-16` and a caller's `p-24` both end up in the class
 * list and which one applies is down to the order Tailwind happened to emit them in. With
 * it, the caller wins, which is what everyone expects and almost nobody gets.
 */
export function classes(...values: ClassValue[]): string {
  return twMerge(clsx(values))
}
