import { useEffect, useState } from 'react'

import { type Health, fetchHealth } from '../api/health'

type State =
  | { kind: 'asking' }
  | { kind: 'answered'; health: Health }
  | { kind: 'unreachable'; reason: string }

/**
 * Which Specdeck is on the other end.
 *
 * The whole of the interface used to be this line. It stays because it is the one thing on
 * this page that proves the client still reaches the server it was built against.
 */
export function ServerLine() {
  const [state, setState] = useState<State>({ kind: 'asking' })

  useEffect(() => {
    const controller = new AbortController()
    fetchHealth(controller.signal)
      .then((health) => {
        setState({ kind: 'answered', health })
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        setState({ kind: 'unreachable', reason: String(error) })
      })
    return () => {
      controller.abort()
    }
  }, [])

  if (state.kind === 'asking') return <span>Asking the server who it is…</span>
  if (state.kind === 'unreachable') return <span className="text-removed">{state.reason}</span>

  return (
    <span className="font-mono">
      {state.health.name} <span data-testid="version">{state.health.version}</span>
    </span>
  )
}
