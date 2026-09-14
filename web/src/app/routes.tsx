import {
  createRootRoute,
  createRoute,
  createRouter,
  createHashHistory,
} from '@tanstack/react-router'

import { Shell } from './Shell'
import { Gallery } from '../gallery/Gallery'
import { ChangeScreen } from '../screens/ChangeScreen'
import { DashboardScreen } from '../screens/DashboardScreen'
import { RepositoryScreen } from '../screens/RepositoryScreen'
import { SpecScreen } from '../screens/SpecScreen'

/**
 * Every screen is a URL.
 *
 * Which means reloading leaves you where you were, and a link to a change is a link. The
 * alternative — state in React and one page — has no answer to "send me that".
 */
const root = createRootRoute({ component: Shell })

const dashboard = createRoute({ getParentRoute: () => root, path: '/', component: DashboardScreen })

const repository = createRoute({
  getParentRoute: () => root,
  path: '/repos/$repoId',
  component: RepositoryScreen,
})

const change = createRoute({
  getParentRoute: () => root,
  path: '/repos/$repoId/changes/$changeId',
  component: ChangeScreen,
})

const spec = createRoute({
  getParentRoute: () => root,
  // A capability may be nested — `identity/user-auth` is one name — so the rest of the path
  // is the identifier rather than a single segment.
  path: '/repos/$repoId/specs/$',
  component: SpecScreen,
})

const system = createRoute({ getParentRoute: () => root, path: '/system', component: Gallery })

export const routeTree = root.addChildren([dashboard, repository, change, spec, system])

export function makeRouter() {
  return createRouter({ routeTree, history: createHashHistory() })
}

declare module '@tanstack/react-router' {
  interface Register {
    router: ReturnType<typeof makeRouter>
  }
}
