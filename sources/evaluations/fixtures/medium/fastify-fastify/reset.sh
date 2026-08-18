#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$PROJECT_DIR/repo"
COMMIT="94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd"
# Reset to the prepared base setup.sh tagged, not to the raw pin: the prepared base is the
# pinned tree minus the six loopback-dependent test files, and resetting past it would put
# those failures back into every run.
PREPARED_TAG="lifecycle-fixture-base"
PREPARED_COMMIT="$(python3 -c '
import json, sys
sequences = json.load(open(sys.argv[1]))["sequences"]
sequence = next(s for s in sequences if s["id"] == "fastify-lifecycle-sequence-v2")
print(sequence["initial_snapshot"]["prepared_removals"]["prepared_commit"])
' "$(cd "$PROJECT_DIR/../../../../.." && pwd)/data/workflow-task-sequences.json")"
if [ ! -d "$REPO/.git" ]; then
  echo "Missing repo checkout; run $PROJECT_DIR/setup.sh first." >&2
  exit 2
fi
if ! git -C "$REPO" rev-parse --verify --quiet "$PREPARED_TAG^{commit}" >/dev/null; then
  echo "Missing prepared base tag $PREPARED_TAG; run $PROJECT_DIR/setup.sh first." >&2
  exit 2
fi
RESOLVED="$(git -C "$REPO" rev-parse "$PREPARED_TAG^{commit}")"
if [ "$RESOLVED" != "$PREPARED_COMMIT" ]; then
  echo "Prepared base $RESOLVED does not match expected $PREPARED_COMMIT; re-run $PROJECT_DIR/setup.sh." >&2
  exit 1
fi
BASE_PARENT="$(git -C "$REPO" rev-parse "$PREPARED_COMMIT^")"
if [ "$BASE_PARENT" != "$COMMIT" ]; then
  echo "Prepared base is not built on pinned commit $COMMIT (parent $BASE_PARENT)." >&2
  exit 1
fi
git -C "$REPO" reset --hard "$PREPARED_COMMIT"
git -C "$REPO" clean -fdx
git -C "$REPO" status --short
