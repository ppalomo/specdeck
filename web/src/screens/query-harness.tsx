import { QueryClientProvider } from '@tanstack/react-query'
import type { RegisteredRouter } from '@tanstack/react-router'
import {
  RouterProvider,
  createMemoryHistory,
  createRootRoute,
  createRoute,
  createRouter,
} from '@tanstack/react-router'
import { type RenderResult, render } from '@testing-library/react'
import type { ReactNode } from 'react'

import { makeQueryClient } from '../app/queryClient'

/**
 * A screen, mounted with its answers already given.
 *
 * The screens read their parameters from the route and their data from the query cache, so
 * this provides both. Seeding the cache rather than faking `fetch` keeps the test about what
 * the screen does with an answer, not about how it asked for it.
 */
export async function renderWithData(
  element: ReactNode,
  answers: [readonly unknown[], unknown][],
  path = '/repos/r/changes/add-reminders',
): Promise<RenderResult> {
  const queryClient = makeQueryClient()
  for (const [key, data] of answers) queryClient.setQueryData(key, data)

  const root = createRootRoute({ component: () => element })
  const router = createRouter({
    routeTree: root.addChildren([
      createRoute({ getParentRoute: () => root, path: '/repos/$repoId/changes/$changeId', component: () => null }),
      createRoute({ getParentRoute: () => root, path: '/repos/$repoId/specs/$', component: () => null }),
      createRoute({ getParentRoute: () => root, path: '/repos/$repoId', component: () => null }),
      createRoute({ getParentRoute: () => root, path: '/', component: () => null }),
    ]),
    history: createMemoryHistory({ initialEntries: [path] }),
  })

  await router.load()

  return render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router as unknown as RegisteredRouter} />
    </QueryClientProvider>,
  )
}
