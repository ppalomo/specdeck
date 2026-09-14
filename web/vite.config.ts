import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

/** Where the Python server listens. Specdeck does not make this configurable. */
const SERVER = 'http://127.0.0.1:4820'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    // The same loopback the server listens on, so what is printed is what is
    // reachable and nothing of Specdeck is exposed to the network.
    host: '127.0.0.1',
    // A fixed port, and a failure rather than a silent move to another one, so that the
    // address `make dev` prints is the address the interface actually opens on.
    port: 4821,
    strictPort: true,
    // In development Vite serves the interface and forwards the API to the server, so the
    // client sees a single origin and the server needs no CORS.
    proxy: { '/api': { target: SERVER } },
  },
  test: {
    // The client is a browser program, so its tests run against a DOM.
    environment: 'jsdom',
    include: ['src/**/*.test.{ts,tsx}'],
    restoreMocks: true,
  },
})
