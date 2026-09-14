import type { components } from './schema'

/**
 * What the server answers at `/api/health`.
 *
 * The shape comes from the server's own OpenAPI document, through
 * `pnpm api:types`. No type of this API is written by hand.
 */
export type Health = components['schemas']['Health']

/** Ask the server who it is. Same origin: Vite proxies `/api` while developing. */
export async function fetchHealth(signal?: AbortSignal): Promise<Health> {
  const response = await fetch('/api/health', signal === undefined ? {} : { signal })
  if (!response.ok) {
    throw new Error(`The server answered ${response.status} to /api/health.`)
  }
  return (await response.json()) as Health
}
