# The client, for development: Vite serving the interface and forwarding /api to the
# server. It shares the server's network namespace, so both see the same loopback.
FROM node:22-trixie-slim

RUN corepack enable

WORKDIR /app/web

# The dependencies first, from the lockfile, so editing the code does not reinstall them.
COPY web/package.json web/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY web ./

EXPOSE 4821
CMD ["pnpm", "dev", "--host", "0.0.0.0"]
