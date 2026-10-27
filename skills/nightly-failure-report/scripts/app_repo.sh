#!/usr/bin/env bash
# Clone a FOLIO module (backend or UI) with full commit history but no blobs up front,
# so you can grep its code and run git log on a file.
# Usage: app_repo.sh <workdir> <repo name, e.g. mod-orders or ui-users>
# Prints the local path and the HEAD commit to use as "ref". Reuses an existing clone.
set -euo pipefail
work="$1"; repo="$2"
dir="$work/repos/$repo"
if [ ! -d "$dir/.git" ]; then
  mkdir -p "$work/repos"
  git clone -q --filter=blob:none "https://github.com/folio-org/$repo.git" "$dir"
fi
echo "$dir ref=$(git -C "$dir" log -1 --format='%h') ($(git -C "$dir" log -1 --format='%cd' --date=short))"
