# Specdeck's commands. Four intentions, one command each, the same on a developer's
# machine and in continuous integration:
#
#   make install   put the repository in working order from a clean clone
#   make dev       run the server and the client, both reloading
#   make check     the only definition of "green"
#   make build     the distributable package, with the interface inside
#
# Everything else here exists because one of those four uses it.

WEB := web
STATIC := src/specdeck/static
HOST := 127.0.0.1
INTERFACE := 4821

.DEFAULT_GOAL := help
.PHONY: help install dev check build \
        require-tools \
        check-server-lint check-server-format check-server-types check-server-tests \
        check-contract check-client-lint check-client-types check-client-tests

help:
	@echo 'make install   install the server and the client from the lockfiles'
	@echo 'make dev       run both, reloading on change, at http://$(HOST):$(INTERFACE)'
	@echo 'make check     lint, types and tests on both sides, and the API contract'
	@echo 'make build     the Python package with the compiled interface inside'

# ---------------------------------------------------------------- what the machine needs

# Specdeck assumes uv, Node and pnpm. It names what is missing and installs nothing: a
# command that reaches outside the repository to change the machine is a command nobody
# can trust.
define require
	@command -v $(1) > /dev/null 2>&1 || { \
		echo 'Specdeck needs $(1), and this machine does not have it.'; \
		echo '  Install it with: $(2)'; \
		exit 1; \
	}
endef

require-tools:
	$(call require,uv,curl -LsSf https://astral.sh/uv/install.sh | sh)
	$(call require,node,https://nodejs.org — or your version manager)
	$(call require,pnpm,corepack enable pnpm)

# ------------------------------------------------------------------------------- install

install: require-tools
	uv sync --locked
	pnpm --dir $(WEB) install --frozen-lockfile

# ----------------------------------------------------------------------------------- dev

# Both processes in this shell's group, so cutting the command cuts the two of them and
# leaves nothing listening behind.
dev:
	@echo 'Specdeck: http://$(HOST):$(INTERFACE)'
	@trap 'kill 0' EXIT INT TERM; \
	uv run specdeck serve --reload & \
	pnpm --dir $(WEB) dev & \
	wait

# --------------------------------------------------------------------------------- check

# Fails on the first check that fails, and make names the one it was running.
check: check-server-lint check-server-format check-server-types check-server-tests \
       check-contract check-client-lint check-client-types check-client-tests
	@echo 'Everything is green.'

check-server-lint:
	@echo '--> server: lint'
	uv run ruff check .

check-server-format:
	@echo '--> server: format'
	uv run ruff format --check .

check-server-types:
	@echo '--> server: types'
	uv run pyright

check-server-tests:
	@echo '--> server: tests'
	uv run pytest

check-contract:
	@echo '--> contract: the client types still match the server'
	pnpm --dir $(WEB) api:check

check-client-lint:
	@echo '--> client: lint'
	pnpm --dir $(WEB) lint

check-client-types:
	@echo '--> client: types'
	pnpm --dir $(WEB) typecheck

check-client-tests:
	@echo '--> client: tests'
	pnpm --dir $(WEB) test

# --------------------------------------------------------------------------------- build

# The interface is compiled into `src/specdeck/static/` and the package is built around it,
# so what ships is one thing to install: the server finds the interface next to its own
# code and serves it without a single Node process on the machine that runs it.
build: require-tools
	@echo '--> interface: compiling into $(STATIC)'
	pnpm --dir $(WEB) build
	@echo '--> package: building with the interface inside'
	uv build
	@echo 'The package is in dist/, with the interface inside it.'
