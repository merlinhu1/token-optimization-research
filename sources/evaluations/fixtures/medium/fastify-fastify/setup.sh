#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$PROJECT_DIR/repo"
URL="https://github.com/fastify/fastify.git"
COMMIT="94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd"
# Fixture preparation. The sequence declares upstream test files the sandboxed lane cannot run
# on a clean checkout of the pin, together with the reproducible commit that removing them
# produces; see initial_snapshot.prepared_removals in data/workflow-task-sequences.json for why.
# Both lists are read from there rather than restated, so this local fixture and the evaluation
# checkout cannot drift apart. The removal is committed and tagged, so the working tree stays
# clean and reset.sh restores the same prepared base.
SEQUENCES="$(cd "$PROJECT_DIR/../../../../.." && pwd)/data/workflow-task-sequences.json"
SEQUENCE_ID="fastify-lifecycle-sequence-v2"
PREPARED_TAG="lifecycle-fixture-base"
readarray -t PREPARED_SPEC < <(python3 - "$SEQUENCES" "$SEQUENCE_ID" <<'PY'
import json, sys
sequences = json.load(open(sys.argv[1]))["sequences"]
sequence = next(s for s in sequences if s["id"] == sys.argv[2])
removals = sequence["initial_snapshot"]["prepared_removals"]
identity = removals["commit_identity"]
print(removals["prepared_commit"])
print(removals["commit_message"])
print(identity["name"])
print(identity["email"])
print(identity["date"])
for path in removals["paths"]:
    print(path)
PY
)
PREPARED_COMMIT="${PREPARED_SPEC[0]}"
PREPARED_MESSAGE="${PREPARED_SPEC[1]}"
PREPARED_NAME="${PREPARED_SPEC[2]}"
PREPARED_EMAIL="${PREPARED_SPEC[3]}"
PREPARED_DATE="${PREPARED_SPEC[4]}"
REMOVED_TESTS=("${PREPARED_SPEC[@]:5}")
mkdir -p "$PROJECT_DIR/runs" "$PROJECT_DIR/tasks"
if [ ! -d "$REPO/.git" ]; then
  rm -rf "$REPO"
  git clone --filter=blob:none --no-checkout "$URL" "$REPO"
fi
GIT=(git -C "$REPO")
"${GIT[@]}" remote set-url origin "$URL"
"${GIT[@]}" reset --hard >/dev/null 2>&1 || true
"${GIT[@]}" clean -fdx
"${GIT[@]}" fetch --depth 1 origin "$COMMIT"
FETCHED="$("${GIT[@]}" rev-parse FETCH_HEAD)"
if [ "$FETCHED" != "$COMMIT" ]; then
  echo "Fetched $FETCHED, expected pinned commit $COMMIT" >&2
  exit 1
fi
"${GIT[@]}" checkout --detach "$COMMIT"
"${GIT[@]}" reset --hard "$COMMIT"
"${GIT[@]}" clean -fdx
"${GIT[@]}" rm -q -- "${REMOVED_TESTS[@]}"
# Fixed identity and date so the prepared base is a reproducible commit hash that registries
# and qualification evidence can pin, exactly as they pin the upstream commit.
GIT_AUTHOR_NAME="$PREPARED_NAME" GIT_AUTHOR_EMAIL="$PREPARED_EMAIL" \
GIT_COMMITTER_NAME="$PREPARED_NAME" GIT_COMMITTER_EMAIL="$PREPARED_EMAIL" \
GIT_AUTHOR_DATE="$PREPARED_DATE" GIT_COMMITTER_DATE="$PREPARED_DATE" \
  "${GIT[@]}" commit -q -m "$PREPARED_MESSAGE"
PREPARED="$("${GIT[@]}" rev-parse HEAD)"
if [ "$PREPARED" != "$PREPARED_COMMIT" ]; then
  echo "Prepared base $PREPARED, expected $PREPARED_COMMIT" >&2
  exit 1
fi
"${GIT[@]}" tag -f "$PREPARED_TAG" >/dev/null
echo "Prepared base $PREPARED (pinned $COMMIT, minus ${#REMOVED_TESTS[@]} loopback-dependent test files)"
(
  cd "$REPO"
  npm install --ignore-scripts --no-audit --no-fund
  )
"${GIT[@]}" status --short
