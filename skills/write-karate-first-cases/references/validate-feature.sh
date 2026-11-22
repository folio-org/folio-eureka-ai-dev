#!/usr/bin/env bash
# Compatibility wrapper. Usage: validate-feature.sh <feature> [<runner Java file> | -] [<root feature file> | -] [extra validate-feature.py options]
# See validate-feature.py for the checks and levels (ERROR / WARN / INFO).
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
FEATURE="$1"; RUNNER="${2:--}"; ROOT="${3:--}"; shift $(( $# < 3 ? $# : 3 ))
ARGS=("$FEATURE")
[ "$RUNNER" != "-" ] && ARGS+=(--runner "$RUNNER")
[ "$ROOT" != "-" ] && ARGS+=(--root "$ROOT")
exec python3 -I "$HERE/validate-feature.py" "${ARGS[@]}" "$@"
