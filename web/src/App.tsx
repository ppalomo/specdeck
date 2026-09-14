import { useEffect, useState } from 'react'

import { type Health, fetchHealth } from './api/health'

type State =
  | { kind: 'asking' }
  | { kind: 'answered'; health: Health }
  | { kind: 'unreachable'; reason: string }

/**
 * The whole interface, for now: proof that the client reaches the server through the
 * proxy and reads what it answers. The visual system arrives with `design-system`.
 */
export function App() {
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

  return (
    <main className="p-8 font-mono text-sm">
      {state.kind === 'asking' && <p>Asking the server who it is…</p>}
      {state.kind === 'answered' && (
        <p>
          {state.health.name} <span data-testid="version">{state.health.version}</span>
        </p>
      )}
      {state.kind === 'unreachable' && (
        <p role="alert">The server did not answer. {state.reason}</p>
      )}
    </main>
  )
}
