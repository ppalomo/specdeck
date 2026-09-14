#!/bin/sh
# The client's API types, generated from the server's own OpenAPI document.
#
#   scripts/api-types.sh           writes them
#   scripts/api-types.sh --check   says whether the written ones are still true
#
# Both go through the same command, so a difference is a difference in the contract and
# never in how the file happened to be produced.
set -eu

SCHEMA='src/api/schema.d.ts'
REGENERATE='pnpm --dir web api:types'

generate() {
  uv run --project .. specdeck openapi | openapi-typescript --output "$1"
}

if [ "${1:-}" != '--check' ]; then
  generate "$SCHEMA"
  exit 0
fi

# Same command, same basename, so the comparison can be byte for byte.
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT
generate "$scratch/schema.d.ts" > /dev/null

if cmp -s "$SCHEMA" "$scratch/schema.d.ts"; then
  echo "$SCHEMA matches the contract the server publishes."
  exit 0
fi

{
  echo
  echo "$SCHEMA is out of date: it is not what the server publishes right now."
  echo "Regenerate it with:  $REGENERATE"
  echo
  diff -u "$SCHEMA" "$scratch/schema.d.ts" || true
} >&2
exit 1
