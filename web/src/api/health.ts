/**
 * What the server answers at `/api/health`.
 *
 * The shape is declared here only until 4.1 generates it from the server's own OpenAPI
 * document. Nothing else in the client may describe the API by hand.
 */
export type Health = {
  name: string
  status: 'ok'
  version: string
}

/** Ask the server who it is. Same origin: Vite proxies `/api` while developing. */
export async function fetchHealth(signal?: AbortSignal): Promise<Health> {
  const response = await fetch('/api/health', signal === undefined ? {} : { signal })
  if (!response.ok) {
    throw new Error(`The server answered ${response.status} to /api/health.`)
  }
  return (await response.json()) as Health
}
