#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$PROJECT_DIR/../../../../.." && pwd)"
FIXTURE_ID="medium-beetbox-beets"

# Runs the active sequence's acceptance in the same order the controller does after the final
# prompt: every task verifier, then the project-wide compile. Task list and commands are read
# from the sequence registry rather than restated, so a task-family change cannot leave this
# script invoking a retired generation.
readarray -t VERIFIERS < <(python3 - "$ROOT/data/workflow-task-sequences.json" "$FIXTURE_ID" <<'PY'
import json, sys
sequences = json.load(open(sys.argv[1]))["sequences"]
sequence = next(
    s for s in sequences
    if s.get("fixture_id") == sys.argv[2] and s.get("status") == "active"
)
for task in sorted(sequence["tasks"], key=lambda t: t["order"]):
    print(task["verifier_command"])
print(sequence["project_compile_command"])
PY
)
PROJECT_COMPILE="${VERIFIERS[-1]}"
unset 'VERIFIERS[-1]'
for verifier in "${VERIFIERS[@]}"; do
  echo "verify: $verifier"
  WORKFLOW_REPO="$PROJECT_DIR/repo" "$ROOT/$verifier"
done
echo "verify: project-wide compile"
(cd "$PROJECT_DIR/repo" && eval "$PROJECT_COMPILE")
