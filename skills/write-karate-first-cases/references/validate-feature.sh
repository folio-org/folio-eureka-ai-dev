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
  sed '/^Feature:/q' "$FEATURE" | grep -q "cases/view/$id" && ok "C$id linked in header" || fail "C$id missing from the header comments before Feature:"
done
grep -qE "^[[:space:]]*Scenario Outline:" "$FEATURE" && fail "Scenario Outline used (use a Karate table + one reusable call)" || ok "no Scenario Outline"
# Reusables already loaded in karate-config.js must not be read() again in the feature
for path in $(grep -oE "read\('classpath:[^']+/reusable/[^']+\.feature'\)" "$FEATURE" | sed -E "s/read\('classpath:([^']+)'\)/\1/" | sort -u); do
  grep -q "$path" "$CONFIG" && fail "reusable $path is already loaded in karate-config.js; call it by its key" || ok "reusable read $path (not in config)"
done
# Unquoted embedded expressions in call arguments: { id: #(x) } instead of { id: '#(x)' }
grep -nE "call [A-Za-z_]+ \{[^}]*:[[:space:]]*#\(" "$FEATURE" | sed 's/^/      /' | grep -q . && fail "unquoted #(...) in call arguments; use '#(...)'" || ok "embedded expressions quoted"
# Shared IDs: callonce uuid in Background breaks parallel scenarios
grep -qE "callonce uuid[0-9]*" "$FEATURE" && fail "callonce uuid used; generate IDs with 'call uuid' inside each scenario" || ok "no callonce uuid"

# Team rules that need scenario context: step numbering, retry/match mixing, headers at the end
python3 -I - "$FEATURE" <<'EOF' || FAIL=1
import re, sys
lines = open(sys.argv[1], encoding="utf-8").read().splitlines()
bad = 0
scen, nums, body = None, [], []
def close():
    global bad
    if scen is None:
        return
    if nums and nums != list(range(1, len(nums) + 1)):
        print(f"FAIL: '{scen}': step comments {nums} are not 1..N without gaps"); bad = 1
    code = [l.strip() for l in body if l.strip() and not l.strip().startswith("#")]
    if code and code[-1].startswith("* configure headers"):
        print(f"FAIL: '{scen}': ends with 'configure headers'"); bad = 1
    block = []
    for l in body + ["Given"]:
        s = l.strip()
        if s.startswith("Given ") or s == "Given":
            if any(b.startswith("And retry until") for b in block) and any(b.startswith("And match") or b.startswith("Then match") for b in block):
                print(f"FAIL: '{scen}': 'retry until' and 'match' in the same request block"); bad = 1
            block = []
        block.append(s)
for l in lines:
    m = re.match(r"\s*Scenario(?: Outline)?:\s*(.*)", l)
    if m:
        close(); scen, nums, body = m.group(1), [], []
        continue
    if scen is not None:
        body.append(l)
        n = re.match(r"\s*# (\d+)\. ", l)
        if n:
            nums.append(int(n.group(1)))
close()
print("ok:   step numbering, retry/match blocks, headers" if not bad else "", end="\n" if not bad else "")
sys.exit(bad)
EOF

# 4. Registration
[ "$(grep -c "\"$NAME\"" "$RUNNER")" -eq 1 ] && ok "registered once in $(basename "$RUNNER")" || fail "not registered exactly once in $(basename "$RUNNER")"
OTHERS=$(grep -rlE "\"$NAME\"" "$PROJECT_DIR/src/test/java" | grep -v "$(basename "$RUNNER")")
[ -z "$OTHERS" ] && ok "not registered in any other runner" || fail "also registered in: $(echo $OTHERS | xargs -n1 basename | tr '\n' ' ')"
[ "$(grep -c "features/$NAME.feature" "$ROOT")" -eq 1 ] && ok "registered once in $(basename "$ROOT")" || fail "not registered exactly once in $(basename "$ROOT")"

exit $FAIL
