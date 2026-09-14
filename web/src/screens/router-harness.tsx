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

/**
 * A component that contains links, rendered where links work.
 *
 * TanStack's `Link` needs a router above it, and a router resolves its route before it
 * renders anything — so this waits for that, rather than leaving every test to discover an
 * empty document and blame the component.
 */
export async function renderInRouter(element: ReactNode): Promise<RenderResult> {
  const root = createRootRoute({ component: () => element })
  const router = createRouter({
    routeTree: root.addChildren([
      createRoute({ getParentRoute: () => root, path: '/', component: () => null }),
    ]),
    history: createMemoryHistory({ initialEntries: ['/'] }),
  })

  await router.load()

  // The provider is typed against the router the application registers; this one is built
  // for the test, so it is named as that type rather than escaped through `any`.
  return render(<RouterProvider router={router as unknown as RegisteredRouter} />)
}
