#!/usr/bin/env bash
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
repo="${WORKFLOW_REPO:-$PROJECT_DIR/repo}"
mode="${1:-all}"
behavior() { (cd "$repo" && go test ./internal/configs -run 'StateMigration|StateStoreProvider|Migrate' -count=1); }
structure() {
  python3 - "$repo/internal/configs/state_migrate_file.go" <<'PY'
from pathlib import Path
import re, sys
text = Path(sys.argv[1]).read_text()
assert re.search(r'type\s+StateStoreProviderRequirement\s+struct\s*\{', text), "missing dedicated StateStoreProviderRequirement type"
assert re.search(r'StateStoreProvider\s+\*StateStoreProviderRequirement\b', text), "StateMigrationInstructions does not own the dedicated requirement type"
assert re.search(r'func\s+decodeStateStoreProviderBlock\([^)]*\)\s*\(\*StateStoreProviderRequirement,\s*hcl\.Diagnostics\)', text), "decoder does not return the dedicated requirement type"
print("state-store-provider-structure-ok")
PY
}
case "$mode" in behavior) behavior ;; structure) structure ;; all) behavior; structure ;; *) echo "usage: verify.sh [behavior|structure|all]" >&2; exit 2 ;; esac
