#!/usr/bin/env bash
# Static validation of a Karate feature in folio-integration-tests.
# Usage: validate-feature.sh <path/to/feature.feature> <runner Java file> <root feature file>
# Example:
#   validate-feature.sh \
#     acquisitions/src/main/resources/thunderjet/mod-orders/features/my-test.feature \
#     acquisitions/src/test/java/org/folio/OrdersExtendedApiTest.java \
#     acquisitions/src/main/resources/thunderjet/mod-orders/orders.feature
# Requires: python3, pip package gherkin-official (pip install gherkin-official).
set -u
FEATURE="$1"; RUNNER="$2"; ROOT="$3"
PROJECT_DIR="${FEATURE%%/src/main/resources/*}"
CONFIG="$PROJECT_DIR/src/main/resources/karate-config.js"
NAME="$(basename "$FEATURE" .feature)"
FAIL=0
fail() { echo "FAIL: $*"; FAIL=1; }
ok()   { echo "ok:   $*"; }

# 1. Gherkin syntax
if python3 -I - "$FEATURE" <<'EOF'
import sys
from gherkin.parser import Parser
doc = Parser().parse(open(sys.argv[1], encoding="utf-8").read())
names = [c["scenario"]["name"] for c in doc["feature"]["children"] if "scenario" in c]
print("      scenarios:", len(names))
EOF
then ok "Gherkin parses"; else fail "Gherkin does not parse"; fi

# 2. Reusable keys exist in karate-config.js
REPO_ROOT="$(dirname "$PROJECT_DIR")"
for key in $(grep -oE "call(once)? [A-Za-z_][A-Za-z0-9_]*" "$FEATURE" | awk '{print $2}' | sort -u); do
  case "$key" in read|login) continue ;; esac
  # uuid1..uuid100 are generated in a loop in karate-config.js (karate.set("uuid"+i, ...))
  if [[ "$key" =~ ^uuid[0-9]+$ ]] && grep -q 'karate.set("uuid"+i' "$CONFIG"; then ok "helper $key (generated in karate-config.js)"; continue; fi
  if grep -qE "^[[:space:]]*$key[[:space:]]*:" "$CONFIG"; then ok "reusable $key"
  elif grep -rqsE "def $key = function" "$REPO_ROOT/common/src/main/resources/common/util/"; then ok "helper $key (common/util)"
  else fail "reusable $key not in karate-config.js or common/util"; fi
done

# 3. Conventions
LEN=$(basename "$FEATURE" | wc -c); [ "$LEN" -le 81 ] && ok "file name length $((LEN-1))" || fail "file name too long ($((LEN-1)) > 80)"
grep -qE "^[[:space:]]+\* print '" "$FEATURE" && fail "* print inside scenarios" || ok "no * print in scenarios"
grep -q "@parallel=false" "$FEATURE" && fail "@parallel=false used" || ok "no @parallel=false"
head -1 "$FEATURE" | grep -qE "^# For [A-Z]+-[0-9]+" && ok "header comment" || fail "first line must be '# For <JIRA-KEY>, <TestRail URL>'"
SCEN=$(grep -cE "^[[:space:]]*Scenario( Outline)?:" "$FEATURE")
CTAGS=$(grep -cE "^[[:space:]]*@C[0-9]+[[:space:]]*$" "$FEATURE")
[ "$SCEN" -eq "$CTAGS" ] && ok "$CTAGS @C tags for $SCEN scenarios" || fail "$CTAGS @C tags for $SCEN scenarios"
for id in $(grep -oE "^[[:space:]]*@C[0-9]+" "$FEATURE" | tr -d ' @C'); do
  head -1 "$FEATURE" | grep -q "cases/view/$id" && ok "C$id linked in header" || fail "C$id missing from header URL list"
done

# 4. Registration
[ "$(grep -c "\"$NAME\"" "$RUNNER")" -eq 1 ] && ok "registered once in $(basename "$RUNNER")" || fail "not registered exactly once in $(basename "$RUNNER")"
[ "$(grep -c "features/$NAME.feature" "$ROOT")" -eq 1 ] && ok "registered once in $(basename "$ROOT")" || fail "not registered exactly once in $(basename "$ROOT")"

exit $FAIL
