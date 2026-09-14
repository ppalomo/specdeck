import { classes } from './classes'

/**
 * How much of a change is done, at a glance and in words.
 *
 * A change whose `tasks.md` has no checkboxes is not zero per cent. Drawing it as an empty
 * ring says "none of this has been done", when what is true is that there is nothing to do
 * yet — and those two lead somewhere completely different when you are deciding what to pick
 * up next.
 */

const SIZE = 40
const STROKE = 4
const RADIUS = (SIZE - STROKE) / 2
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export function ProgressRing({
  done,
  total,
  className,
}: {
  done: number
  total: number
  className?: string
}) {
  if (total === 0) {
    return (
      <span
        className={classes('inline-flex items-center gap-8 text-xs text-faint', className)}
        data-progress="none"
      >
        <EmptyRing />
        No tasks yet
      </span>
    )
  }

  const proportion = Math.min(1, Math.max(0, done / total))

  return (
    <span
      className={classes('inline-flex items-center gap-8 text-xs text-muted', className)}
      data-progress={`${String(done)}/${String(total)}`}
      role="img"
      aria-label={`${String(done)} of ${String(total)} tasks done`}
    >
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${String(SIZE)} ${String(SIZE)}`}>
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--colour-line)"
          strokeWidth={STROKE}
        />
        <circle
          cx={SIZE / 2}
          cy={SIZE / 2}
          r={RADIUS}
          fill="none"
          stroke="var(--colour-accent)"
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={CIRCUMFERENCE * (1 - proportion)}
          transform={`rotate(-90 ${String(SIZE / 2)} ${String(SIZE / 2)})`}
          // From one value to the next rather than jumping, and not at all for anyone who
          // asked for less movement — the media query in the stylesheet takes care of that.
          style={{
            transition: 'stroke-dashoffset var(--duration-settled) var(--ease-soft)',
          }}
        />
      </svg>
      <span className="font-mono tabular-nums">
        {done}/{total}
      </span>
    </span>
  )
}

function EmptyRing() {
  return (
    <svg width={SIZE} height={SIZE} viewBox={`0 0 ${String(SIZE)} ${String(SIZE)}`} aria-hidden>
      <circle
        cx={SIZE / 2}
        cy={SIZE / 2}
        r={RADIUS}
        fill="none"
        stroke="var(--colour-line)"
        strokeWidth={STROKE}
        strokeDasharray="2 6"
      />
    </svg>
  )
}
