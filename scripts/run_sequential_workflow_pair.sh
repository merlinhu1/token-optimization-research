#!/usr/bin/env bash
# Run a shared-baseline + treatment sequential workflow evaluation for one sequence.
#
# Usage:
#   scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1
#   scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1 --treatment-profile retrieval-codegraph
#   REPLICATE_INDEX=1 scripts/run_sequential_workflow_pair.sh beets-maintenance-sequence-v1 --timeout-per-task 2400
#
# Extra arguments are passed through to scripts/run_codex_workflow_evaluation.py.
set -euo pipefail

# Keep repo-local validation available in non-login shells used by schedulers/agents.
export PATH="/opt/data/bin:/opt/data/.local/bin:${PATH}"

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'USAGE'
Usage: scripts/run_sequential_workflow_pair.sh <sequence-id> [--treatment-profile <profile-id>] [runner options]

Runs comparable lanes in order:
  1. one canonical baseline-bare-codex per sequence/date/replicate, reused across treatments
  2. the selected treatment profile (default: retrieval-leanctx)

Environment:
  REPLICATE_INDEX            replicate index to pass to both lanes (default: 0)
  FORCE_BASELINE_RERUN=1     rerun the canonical baseline even if a completed one exists

Examples:
  scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1
  scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1 --treatment-profile retrieval-codegraph
  REPLICATE_INDEX=1 scripts/run_sequential_workflow_pair.sh beets-maintenance-sequence-v1 --timeout-per-task 2400
  scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1 --source-codex-home /path/to/.codex

Useful discovery:
  python3 scripts/run_codex_workflow_evaluation.py --list-sequences
USAGE
  exit 0
fi

sequence_id="$1"
shift
replicate_index="${REPLICATE_INDEX:-0}"
treatment_profile="retrieval-leanctx"
runner_args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --treatment-profile)
      if [[ $# -lt 2 ]]; then
        echo "--treatment-profile requires a profile id" >&2
        exit 2
      fi
      treatment_profile="$2"
      shift 2
      ;;
    --treatment-profile=*)
      treatment_profile="${1#--treatment-profile=}"
      shift
      ;;
    *)
      runner_args+=("$1")
      shift
      ;;
  esac
done

run_lane() {
  local profile_id="$1"
  shift
  echo "== sequential workflow: ${sequence_id} :: ${profile_id} :: r${replicate_index} :: comparison ${treatment_profile} =="
  python3 scripts/run_codex_workflow_evaluation.py \
    --sequence-id "$sequence_id" \
    --profile-id "$profile_id" \
    --comparison-profile-id "$treatment_profile" \
    --replicate-index "$replicate_index" \
    "$@"
}

baseline_session_id="$(python3 - "$sequence_id" "$replicate_index" <<'PY'
import sys
import scripts.run_codex_workflow_evaluation as runner

seq = runner.load_sequence(sys.argv[1])
project_id = runner.PROJECT_META[seq["fixture_id"]]["project_id"]
print(runner.canonical_baseline_session_id(project_id, int(sys.argv[2])))
PY
)"

baseline_ready="$(python3 - "$baseline_session_id" <<'PY'
import json
import sys
from pathlib import Path

root = Path.cwd()
session_id = sys.argv[1]
registry = root / "data/workflow-sessions.json"
if not registry.exists():
    print("0")
    raise SystemExit
doc = json.loads(registry.read_text())
for session in doc.get("sessions", []):
    if session.get("session_id") != session_id:
        continue
    accepted = session.get("interpretation", {}).get("accepted_for_objective") is True
    completed = session.get("status") == "completed"
    artifacts = session.get("artifacts", {}) if isinstance(session.get("artifacts"), dict) else {}
    required = [artifacts.get(key) for key in ("run_record", "final_diff", "evidence_bundle", "manifest")]
    have_artifacts = all(path and (root / path).exists() for path in required)
    print("1" if accepted and completed and have_artifacts else "0")
    raise SystemExit
print("0")
PY
)"

if [[ "${FORCE_BASELINE_RERUN:-0}" == "1" || "$baseline_ready" != "1" ]]; then
  run_lane baseline-bare-codex "${runner_args[@]}"
else
  echo "== sequential workflow: ${sequence_id} :: baseline-bare-codex :: r${replicate_index} :: reuse canonical ${baseline_session_id} =="
fi
run_lane "$treatment_profile" "${runner_args[@]}"

if [[ "${SKIP_PAIR_VALIDATION:-0}" == "1" ]]; then
  echo "== validation skipped by SKIP_PAIR_VALIDATION=1 (matrix controller validates after merge) =="
  exit 0
fi

safe_sequence_id="${sequence_id//[^A-Za-z0-9_.-]/_}"
safe_treatment_profile="${treatment_profile//[^A-Za-z0-9_.-]/_}"
validation_tmp="${TMPDIR:-/tmp}"
mkdir -p "$validation_tmp"

echo "== validation =="
python3 scripts/validate_repository.py
git diff --check
truthmark check --json >"$validation_tmp/truthcheck_sequential_workflow_pair_${safe_sequence_id}_${safe_treatment_profile}_r${replicate_index}.json"
truthmark index --json >"$validation_tmp/truthindex_sequential_workflow_pair_${safe_sequence_id}_${safe_treatment_profile}_r${replicate_index}.json"
echo "Pair complete. Inspect sources/evaluations/workflow-sessions/ and data/workflow-sessions.json."
