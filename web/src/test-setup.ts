import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

/**
 * Take the rendered tree down between tests.
 *
 * Testing Library does this automatically only when Vitest's globals are on, which they are
 * not here. Without it the second render in a file lands beside the first, and a query that
 * should find one element finds two — which reads like a bug in the component rather than in
 * the setup.
 */
afterEach(() => {
  cleanup()
})
