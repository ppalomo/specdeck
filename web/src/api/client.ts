import type { components } from './schema'

/**
 * Talking to the Specdeck server.
 *
 * Every shape here comes from the server's own OpenAPI document, through `pnpm api:types`.
 * Nothing about this API is described twice, so a model that changes on the server turns the
 * client red rather than turning it into a lie that compiles.
 */

export type RegisteredRepo = components['schemas']['RegisteredRepo']
export type Index = components['schemas']['Index']
export type Change = components['schemas']['Change']
export type Spec = components['schemas']['Spec']
export type Delta = components['schemas']['Delta']
export type Artifact = components['schemas']['Artifact']
export type ArtifactDocument = components['schemas']['ArtifactDocument']
export type Availability = components['schemas']['Availability']
export type Issue = components['schemas']['Issue']
export type Requirement = components['schemas']['Requirement']
export type TaskGroup = components['schemas']['TaskGroup']

/** What the server said went wrong, kept in its own words. */
export class ServerError extends Error {
  // Written out rather than declared in the parameter list: parameter properties are the one
  // TypeScript feature that emits code, and this client is compiled by erasing types only.
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ServerError'
    this.status = status
  }
}

async function ask<T>(path: string, init?: RequestInit): Promise<T> {
  const sending = init?.body !== undefined
  const response = await fetch(path, {
    ...init,
    ...(sending ? { headers: { 'content-type': 'application/json' } } : {}),
  })

  if (!response.ok) {
    throw new ServerError(response.status, await explain(response))
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

/**
 * The server's own words for what went wrong.
 *
 * FastAPI puts them in `detail`, and they are written to be read by whoever has to fix the
 * problem — which path was looked at, which file was missing. Replacing them with something
 * of ours would throw away the only part of the message that helps.
 */
async function explain(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json()
    if (typeof body === 'object' && body !== null && 'detail' in body) {
      const { detail } = body
      if (typeof detail === 'string') return detail
    }
  } catch {
    // A response that is not JSON says what it can through its status alone.
  }
  return `The server answered ${String(response.status)}.`
}

export const api = {
  repos: (): Promise<RegisteredRepo[]> => ask('/api/repos'),
  index: (repoId: string): Promise<Index> => ask(`/api/repos/${encodeURIComponent(repoId)}`),
  changes: (repoId: string): Promise<Change[]> =>
    ask(`/api/repos/${encodeURIComponent(repoId)}/changes`),
  change: (repoId: string, changeId: string): Promise<Change> =>
    ask(`/api/repos/${encodeURIComponent(repoId)}/changes/${encodeURIComponent(changeId)}`),
  specs: (repoId: string): Promise<Spec[]> =>
    ask(`/api/repos/${encodeURIComponent(repoId)}/specs`),
  spec: (repoId: string, specId: string): Promise<Spec> =>
    // Not encoded: a capability may be nested, and `identity/user-auth` is one name whose
    // slash is part of the path rather than part of the name.
    ask(`/api/repos/${encodeURIComponent(repoId)}/specs/${specId}`),

  register: (path: string): Promise<RegisteredRepo> =>
    ask('/api/repos', { method: 'POST', body: JSON.stringify({ path }) }),
  unregister: (repoId: string): Promise<void> =>
    ask(`/api/repos/${encodeURIComponent(repoId)}`, { method: 'DELETE' }),
  read: (repoId: string): Promise<Index> =>
    ask(`/api/repos/${encodeURIComponent(repoId)}/reading`, { method: 'POST' }),
}
