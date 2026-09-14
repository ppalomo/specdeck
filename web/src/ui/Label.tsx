import { classes } from './classes'
import type { Operation, Status } from '../theme/tokens'

/**
 * The two labels that carry Specdeck's fixed meanings: what state an artifact is in, and
 * what a delta proposes to do.
 *
 * Both always write the word as well as painting it. Colour alone excludes anyone who cannot
 * tell these particular tones apart, and there is no version of this interface where knowing
 * that a delta is a REMOVED rather than an ADDED is optional.
 *
 * Screens use these rather than styling their own, which is the only way the same state looks
 * the same in the pipeline of a change and in a list of changes.
 */

const OPERATION_COLOURS: Record<Operation, string> = {
  added: 'text-added',
  modified: 'text-modified',
  removed: 'text-removed',
  renamed: 'text-renamed',
}

const STATUS_COLOURS: Record<Status, string> = {
  done: 'text-done',
  ready: 'text-ready',
  blocked: 'text-blocked',
  skipped: 'text-skipped',
}

const shared =
  'inline-flex items-center gap-4 rounded-[8px] bg-raised px-8 py-4 ' +
  'font-mono text-xs font-medium uppercase tracking-wide'

export function OperationLabel({ operation }: { operation: Operation }) {
  return (
    <span className={classes(shared, OPERATION_COLOURS[operation])} data-operation={operation}>
      <Dot />
      {operation}
    </span>
  )
}

export function StatusLabel({ status }: { status: Status }) {
  return (
    <span className={classes(shared, STATUS_COLOURS[status])} data-status={status}>
      <Dot />
      {status}
    </span>
  )
}

/** The colour, as a shape, for the times a word alone is not quick enough to scan. */
function Dot() {
  return <span aria-hidden className="size-8 rounded-full bg-current" />
}
