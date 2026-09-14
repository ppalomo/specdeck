import { QueryClient } from '@tanstack/react-query'

/**
 * What is on screen stays on screen.
 *
 * Keeping the previous answer while the next one travels is the rule "nothing flickers" made
 * structural rather than a discipline: there is never a moment with nothing in it, and no
 * component has to remember to arrange that.
 */
export function makeQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        placeholderData: <T,>(previous: T): T => previous,
        staleTime: 30_000,
        retry: false,
        refetchOnWindowFocus: false,
      },
    },
  })
}
