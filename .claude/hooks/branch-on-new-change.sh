#!/usr/bin/env bash
# Creates and checks out a branch named after an OpenSpec change, so feature work
# never lands directly on the default branch.
#
# Fires from a PostToolUse hook on Bash commands matching `openspec new change *`,
# so it only runs once the change directory actually exists.
#
# Deliberately does nothing when already on a non-default branch: that means work
# is in progress and switching underneath it would be worse than staying put.

set -uo pipefail

payload=$(cat)

# The command may carry redirections or pipes, so take the first kebab-case token
# after "new change" rather than assuming it is the last argument.
name=$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' |
  sed -n "s/.*openspec new change[[:space:]]*['\"]\{0,1\}\([A-Za-z0-9][A-Za-z0-9._-]*\).*/\1/p" |
  head -1)

[ -n "$name" ] || exit 0
git rev-parse --git-dir >/dev/null 2>&1 || exit 0

current=$(git branch --show-current 2>/dev/null)

case "$current" in
  main|master|"") ;;
  *)
    printf '{"systemMessage":"Change %s created. Already on branch %s, so no new branch was made."}\n' "$name" "$current"
    exit 0
    ;;
esac

if git show-ref --verify --quiet "refs/heads/$name"; then
  git checkout "$name" >/dev/null 2>&1 &&
    printf '{"systemMessage":"Branch %s already existed; switched to it."}\n' "$name"
else
  git checkout -b "$name" >/dev/null 2>&1 &&
    printf '{"systemMessage":"Created and switched to branch %s for this change."}\n' "$name"
fi
