import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'

import { ServerError, api } from '../api/client'
import { Button } from '../ui/Button'

/**
 * Registering a repository by path — the same manual registration as `specdeck add`.
 *
 * When the path is not a root, what is shown is the server's own sentence: which path it
 * looked at and which file it expected there. That is the difference between a message that
 * tells you it was a typo and one that leaves you guessing.
 */
export function RegisterRepo() {
  const [path, setPath] = useState('')
  const queryClient = useQueryClient()

  const register = useMutation({
    mutationFn: (where: string) => api.register(where),
    onSuccess: async () => {
      setPath('')
      await queryClient.invalidateQueries({ queryKey: ['repos'] })
    },
  })

  return (
    <form
      className="flex flex-col gap-8"
      onSubmit={(event) => {
        event.preventDefault()
        if (path.trim().length > 0) register.mutate(path.trim())
      }}
    >
      <div className="flex items-center gap-8">
        <input
          value={path}
          onChange={(event) => {
            setPath(event.target.value)
          }}
          placeholder="/path/to/a/repository"
          aria-label="Path of the repository to register"
          className="h-40 min-w-0 flex-1 rounded-[8px] bg-raised px-12 font-mono text-sm text-text placeholder:text-faint focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
        />
        <Button type="submit" tone="accent" disabled={register.isPending}>
          {register.isPending ? 'Reading…' : 'Register'}
        </Button>
      </div>
      {register.error !== null && (
        <p role="alert" className="font-mono text-xs text-removed">
          {register.error instanceof ServerError
            ? register.error.message
            : String(register.error)}
        </p>
      )}
    </form>
  )
}
