#!/usr/bin/env bash
# Static validation of a Karate feature in folio-integration-tests (any team).
# Usage: validate-feature.sh <path/to/feature.feature> [<runner Java file> | -] [<root feature file> | -]
#   Pass the runner and/or root feature the project uses to register features (see `karate-context.py profile <project>`);
#   use - for a registration step the project does not have.
# Example (acquisitions: FEATURES array + root feature):
#   validate-feature.sh \
#     acquisitions/src/main/resources/thunderjet/mod-orders/features/my-test.feature \
#     acquisitions/src/test/java/org/folio/OrdersExtendedApiTest.java \
#     acquisitions/src/main/resources/thunderjet/mod-orders/orders.feature
# Example (mod-circulation: root feature only):
#   validate-feature.sh mod-circulation/src/main/resources/vega/mod-circulation/features/my-test.feature - \
#     mod-circulation/src/main/resources/vega/mod-circulation/features/root.feature
# Requires: python3, pip package gherkin-official (pip install gherkin-official).
set -u
FEATURE="$1"; RUNNER="${2:--}"; ROOT="${3:--}"
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
for key in $(grep -vE "^[[:space:]]*#" "$FEATURE" | grep -oE "(^|[[:space:]=])call(once)? [A-Za-z_][A-Za-z0-9_]*" | awk '{print $NF}' | sort -u); do
  case "$key" in read|login) continue ;; esac
  # defined in the feature itself (def key = read(...) / function)
  if grep -qE "def $key[[:space:]]*=" "$FEATURE"; then ok "reusable $key (defined in the feature)"; continue; fi
  # uuid1..uuid100 are generated in a loop in karate-config.js (karate.set("uuid"+i, ...))
  if [[ "$key" =~ ^uuid[0-9]+$ ]] && grep -q 'karate.set("uuid"+i' "$CONFIG"; then ok "helper $key (generated in karate-config.js)"; continue; fi
  if grep -qE "^[[:space:]]*$key[[:space:]]*:" "$CONFIG"; then ok "reusable $key"
  elif grep -rqsE "def $key = function" "$REPO_ROOT/common/src/main/resources/common/util/"; then ok "helper $key (common/util)"
  elif grep -rqsE "def $key[[:space:]]*=" "$PROJECT_DIR/src/main/resources" --include="*.feature" -l | grep -qiE "/(global|util|reusable|common)[^/]*/|variables|init"; then ok "reusable $key (global/util feature of the project)"
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
STRICT=0; [ -d "$PROJECT_DIR/ai" ] && STRICT=1   # team rules file present: its rules are mandatory
python3 -I - "$FEATURE" "$STRICT" <<'EOF' || FAIL=1
import re, sys
lines = open(sys.argv[1], encoding="utf-8").read().splitlines()
strict = sys.argv[2] == "1"
bad = 0
def team_rule(msg):
    # retry/match and headers rules come from the acquisitions rules files; elsewhere they are recommendations
    global bad
    if strict:
        print("FAIL: " + msg); bad = 1
    else:
        print("WARN: " + msg + " (team rule in acquisitions; recommended here)")
scen, nums, body = None, [], []
def close():
    global bad
    if scen is None:
        return
    if nums and nums != list(range(1, len(nums) + 1)):
        print(f"FAIL: '{scen}': step comments {nums} are not 1..N without gaps"); bad = 1
    code = [l.strip() for l in body if l.strip() and not l.strip().startswith("#")]
    if code and code[-1].startswith("* configure headers"):
        team_rule(f"'{scen}': ends with 'configure headers'")
    block = []
    for l in body + ["Given"]:
        s = l.strip()
        if s.startswith("Given ") or s == "Given":
            if any(b.startswith("And retry until") for b in block) and any(b.startswith("And match") or b.startswith("Then match") for b in block):
                team_rule(f"'{scen}': 'retry until' and 'match' in the same request block")
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

# 4. Registration: in at most one runner, called by the given root feature once, and run by something
RUNNERS=$(grep -rlE "\"$NAME\"|runFeatureTest\(\s*\"[^\"]*$NAME(\.feature)?\"" "$PROJECT_DIR/src/test/java" 2>/dev/null)
NR=$(echo "$RUNNERS" | grep -c . )
[ "$NR" -le 1 ] && ok "registered in $NR runner(s)" || fail "registered in $NR runners: $(echo $RUNNERS | xargs -n1 basename | tr '\n' ' ')"
if [ "$RUNNER" != "-" ]; then
  echo "$RUNNERS" | grep -q "$(basename "$RUNNER")" && ok "registered in $(basename "$RUNNER")" || fail "not registered in $(basename "$RUNNER")"
fi
if [ "$ROOT" != "-" ]; then
  [ "$(grep -cE "read\('[^']*/?$NAME\.feature" "$ROOT")" -eq 1 ] && ok "called once from $(basename "$ROOT")" || fail "not called exactly once from $(basename "$ROOT")"
fi
[ "$NR" -ge 1 ] || [ "$ROOT" != "-" ] || fail "not registered anywhere: add it to a runner or a root feature"

exit $FAIL
