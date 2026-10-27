#!/usr/bin/env bash
# Show recent commits that touched a file (or a line range) in a cloned module, with Jira keys.
# Use it to prove a UI/API change was intended (outdated test) or to find the change that broke it (app bug).
# Usage: ticket.sh <workdir> <repo> <path> [<from line>,<to line>] [<since, e.g. 3.months>]
set -euo pipefail
work="$1"; repo="$2"; path="$3"; range="${4:-}"; since="${5:-6.months}"
dir="$work/repos/$repo"
[ -d "$dir/.git" ] || { echo "clone first: app_repo.sh $work $repo" >&2; exit 1; }
if [ -n "$range" ]; then
  git -C "$dir" log --since="$since" -n 8 --format='%h %cd %s' --date=short -L "$range:$path" --no-patch
else
  git -C "$dir" log --since="$since" -n 8 --format='%h %cd %s' --date=short -- "$path"
fi | sed -E 's/^/  /' | tee /dev/stderr | grep -oE '[A-Z][A-Z0-9]+-[0-9]+' | sort -u | sed 's/^/jira: /' || true
