import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'

import { App } from './App'

afterEach(cleanup)

/** Answer `/api/health` with what the test decides the server said. */
function serverAnswers(body: unknown, status = 200): void {
  vi.stubGlobal(
    'fetch',
    vi.fn(() => Promise.resolve(new Response(JSON.stringify(body), { status }))),
  )
}

test('shows the name and the version the server answers', async () => {
  serverAnswers({ name: 'Specdeck', status: 'ok', version: '9.9.9' })

  render(<App />)

  expect((await screen.findByTestId('version')).textContent).toBe('9.9.9')
  expect(screen.getByText(/Specdeck/)).toBeDefined()
})

test('says so when the server does not answer', async () => {
  serverAnswers({}, 503)

  render(<App />)

  expect((await screen.findByRole('alert')).textContent).toContain('503')
})
