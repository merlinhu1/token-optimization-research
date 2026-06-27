#!/usr/bin/env bash
# Run the paired baseline + treatment sequential workflow evaluation for one sequence.
#
# Usage:
#   scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1
#   scripts/run_sequential_workflow_pair.sh terraform-maintenance-sequence-v1 --treatment-profile retrieval-codegraph
#   REPLICATE_INDEX=1 scripts/run_sequential_workflow_pair.sh beets-maintenance-sequence-v1 --timeout-per-task 2400
#
# Extra arguments are passed through to scripts/run_codex_workflow_evaluation.py.
set -euo pipefail

if [[ $# -lt 1 || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'USAGE'
Usage: scripts/run_sequential_workflow_pair.sh <sequence-id> [--treatment-profile <profile-id>] [runner options]

Runs both comparable lanes in order:
  1. baseline-bare-codex
  2. the selected treatment profile (default: retrieval-leanctx)

Environment:
  REPLICATE_INDEX   replicate index to pass to both lanes (default: 0)

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

run_lane baseline-bare-codex "${runner_args[@]}"
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
