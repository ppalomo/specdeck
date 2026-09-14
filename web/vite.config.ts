import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

/** Where the Python server listens. Specdeck does not make this configurable. */
const SERVER = 'http://127.0.0.1:4820'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  build: {
    // The compiled interface lands inside the Python package, which is what makes the
    // built wheel carry it and the server able to serve it with no Node process around.
    // `emptyOutDir` has to be said out loud because the directory is outside Vite's root:
    // without it Vite refuses to clear it and stale files from an earlier build survive.
    outDir: '../src/specdeck/static',
    emptyOutDir: true,
  },
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
    // A bind mount into a container does not deliver filesystem events, so inside one the
    // watcher has to ask. On a real machine it listens, which is cheaper.
    watch: process.env.VITE_POLL === 'true' ? { usePolling: true, interval: 300 } : null,
  },
  test: {
    // The client is a browser program, so its tests run against a DOM.
    environment: 'jsdom',
    // Two suites. Under `src/` is the interface, tried in a DOM. Under `tests/` is what the
    // repository itself has to be true of — the palette's contrast, what the built page is
    // allowed to depend on — which reads files and needs Node rather than a browser.
    include: ['src/**/*.test.{ts,tsx}', 'tests/**/*.test.ts'],
    restoreMocks: true,
  },
})
