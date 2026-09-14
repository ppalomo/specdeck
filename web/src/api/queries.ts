import { queryOptions } from '@tanstack/react-query'

import { api } from './client'

/**
 * What each screen asks for, and under what name it is remembered.
 *
 * Keys are the shape of the route they belong to, so invalidating one repository does not
 * throw away what is known about the others.
 */
export const queries = {
  repos: () => queryOptions({ queryKey: ['repos'], queryFn: api.repos }),

  index: (repoId: string) =>
    queryOptions({ queryKey: ['repos', repoId], queryFn: () => api.index(repoId) }),

  changes: (repoId: string) =>
    queryOptions({ queryKey: ['repos', repoId, 'changes'], queryFn: () => api.changes(repoId) }),

  change: (repoId: string, changeId: string) =>
    queryOptions({
      queryKey: ['repos', repoId, 'changes', changeId],
      queryFn: () => api.change(repoId, changeId),
    }),

  specs: (repoId: string) =>
    queryOptions({ queryKey: ['repos', repoId, 'specs'], queryFn: () => api.specs(repoId) }),

  spec: (repoId: string, specId: string) =>
    queryOptions({
      queryKey: ['repos', repoId, 'specs', specId],
      queryFn: () => api.spec(repoId, specId),
    }),
}
