import type { Operation, Status } from '../theme/tokens'

/**
 * The contract speaks in OpenSpec's words and the tokens in ours.
 *
 * OpenSpec writes an operation as `ADDED`; the design system names the colour `added`. One
 * function rather than a cast at each call site, so the day a fifth operation appears this
 * is the place that stops compiling.
 */
const OPERATIONS: Record<string, Operation> = {
  ADDED: 'added',
  MODIFIED: 'modified',
  REMOVED: 'removed',
  RENAMED: 'renamed',
}

export function operationOf(written: string): Operation {
  return OPERATIONS[written] ?? 'modified'
}

const STATUSES: Record<string, Status> = {
  done: 'done',
  ready: 'ready',
  blocked: 'blocked',
  skipped: 'skipped',
}

export function statusOf(written: string): Status {
  return STATUSES[written] ?? 'blocked'
}
