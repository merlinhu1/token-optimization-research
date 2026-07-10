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
  1. one reviewed canonical baseline-bare-codex per frozen protocol fingerprint/replicate, reused across treatments
  2. the selected treatment profile (default: retrieval-leanctx)

Environment:
  REPLICATE_INDEX            replicate index to pass to both lanes (default: 0)

Session evidence is append-only: this helper reuses an eligible canonical baseline and never overwrites an existing session ID. Use a new REPLICATE_INDEX when an occupied baseline is excluded or unsuitable.

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
fingerprint = runner.baseline_protocol_fingerprint(seq)
print(runner.canonical_baseline_session_id(project_id, int(sys.argv[2]), fingerprint))
PY
)"

treatment_session_id="$(python3 - "$sequence_id" "$treatment_profile" "$replicate_index" <<'PY'
import sys
import scripts.run_codex_workflow_evaluation as runner

seq = runner.load_sequence(sys.argv[1])
project_id = runner.PROJECT_META[seq["fixture_id"]]["project_id"]
fingerprint = runner.baseline_protocol_fingerprint(seq)
print(runner.canonical_treatment_session_id(project_id, sys.argv[2], int(sys.argv[3]), fingerprint))
PY
)"

session_identity() {
  python3 - "$sequence_id" "$1" "$replicate_index" "$2" <<'PY'
import json
import sys
from pathlib import Path
import scripts.run_codex_workflow_evaluation as runner

root = Path.cwd()
seq = runner.load_sequence(sys.argv[1])
profile_id = sys.argv[2]
fallback_session_id = sys.argv[4]
doc = json.loads((root / "data/workflow-sessions.json").read_text())
session = runner.find_pool_profile_record(doc, seq, profile_id, int(sys.argv[3]))
print(f"{session.get('session_id') if session else fallback_session_id}\t{runner.reviewed_session_reuse_state(session, root)}")
PY
}

baseline_identity="$(session_identity baseline-bare-codex "$baseline_session_id")"
IFS=$'\t' read -r baseline_session_id baseline_state <<<"$baseline_identity"

if [[ "$baseline_state" == "missing" ]]; then
  run_lane baseline-bare-codex "${runner_args[@]}"
  echo "Canonical baseline ${baseline_session_id} completed execution but requires a recorded software-quality review with score >= 4 and objective acceptance before treatment spend. Review it, then rerun this pair command." >&2
  exit 3
elif [[ "$baseline_state" == "reusable" ]]; then
  echo "== sequential workflow: ${sequence_id} :: baseline-bare-codex :: r${replicate_index} :: reuse reviewed canonical ${baseline_session_id} =="
elif [[ "$baseline_state" == "review-pending" ]]; then
  echo "Canonical baseline ${baseline_session_id} is execution-ready but quality-review pending. Record the review and objective acceptance before treatment spend." >&2
  exit 3
else
  echo "Canonical baseline ${baseline_session_id} already exists but is not reusable. Evidence is append-only; select a new REPLICATE_INDEX instead of overwriting it." >&2
  exit 2
fi

treatment_identity="$(session_identity "$treatment_profile" "$treatment_session_id")"
IFS=$'\t' read -r treatment_session_id treatment_state <<<"$treatment_identity"
if [[ "$treatment_state" == "missing" ]]; then
  run_lane "$treatment_profile" "${runner_args[@]}"
  echo "Treatment ${treatment_session_id} completed execution but requires the same recorded quality review and objective acceptance before comparison." >&2
  exit 3
elif [[ "$treatment_state" == "review-pending" ]]; then
  echo "Treatment ${treatment_session_id} is execution-ready but quality-review pending. Record the review and objective acceptance, then rerun this pair command." >&2
  exit 3
elif [[ "$treatment_state" == "reusable" ]]; then
  echo "== sequential workflow: ${sequence_id} :: ${treatment_profile} :: r${replicate_index} :: reuse reviewed ${treatment_session_id} =="
else
  echo "Treatment ${treatment_session_id} already exists but is not reusable. Evidence is append-only; select a new REPLICATE_INDEX instead of overwriting it." >&2
  exit 2
fi

python3 - "$sequence_id" "$treatment_profile" "$replicate_index" <<'PY'
import json
import sys
from pathlib import Path
import scripts.run_codex_workflow_evaluation as runner

seq = runner.load_sequence(sys.argv[1])
project_id = runner.PROJECT_META[seq["fixture_id"]]["project_id"]
fingerprint = runner.baseline_protocol_fingerprint(seq)
comparison_id = f"baseline-{runner.artifact_lane_label(project_id)}-{runner.DATE.replace('-', '')}-vs-{runner.artifact_profile_label(sys.argv[2])}-p-{fingerprint}-r{int(sys.argv[3])}"
path = Path("sources/evaluations/workflow-sessions") / f"{comparison_id}.json"
if path.exists():
    comparison = json.loads(path.read_text())
else:
    comparison = runner.write_comparison_if_ready(seq, "phase-2-sequential-workflow-v1", int(sys.argv[3]), sys.argv[2])
if not comparison:
    raise SystemExit("reviewed baseline/treatment did not produce a comparison")
print(json.dumps({"comparison_id": comparison["comparison_id"], "ranking_eligible": comparison["ranking_eligible"]}))
PY

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
