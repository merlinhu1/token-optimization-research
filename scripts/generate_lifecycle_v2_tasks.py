#!/usr/bin/env python3
"""Generate the Lifecycle V2 bounded task family from validated upstream regressions.

Lifecycle V1 put three large tasks in a sequence and let the last one carry roughly 45%
of the cost. That task also asked the agent to "identify any defect that would be
unacceptable to ship", which has no terminal condition -- the agent stops when it decides
it is satisfied -- and its step count swung 11 against 16 on Beets and 13 against 10 on
Fastify while the feature task held at 17 and 17. Aggregate variance was therefore mostly
one task's variance, and no amount of replication fixes a dominating term cheaply.

Lifecycle V2 replaces that shape with many small tasks of comparable size, each restoring
one named behaviour that a specific upstream test already covers. Two properties follow:

- Every task has a closed stopping condition. The described behaviour either works or it
  does not, so "done" is not a judgement call the agent makes about its own thoroughness.
- No single task dominates. The seeds are 478 to 2,158 characters on Beets and 520 to 855
  on Fastify, against three unbounded V1 tasks.

Retrieval demand is deliberately preserved: prompts state the observable symptom and never
name the file, function, or test involved, so locating the defect is still real work. That
is the part the tools under study are supposed to make cheaper, and removing it would make
the benchmark insensitive to 26 of the 84 active treatment profiles.

Every seed here was proven by execution before it was written down -- see
`scripts/mine_bounded_task_candidates.py`, which requires the seeded state to fail the
covering tests and the repaired state to pass them.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
GENERATION = "lifecycle-v2"

BEETS_SUITE = "uv run --offline --frozen pytest -q --tb=no"
# Six Fastify test files fail on a clean pinned checkout in the sandboxed lane because they
# open real sockets. Left in, they show the agent seven failures it did not cause and cannot
# fix, which is noise charged to the measurement. Excluding them keeps the suite a valid
# oracle: the seeded regressions still fail underneath.
FASTIFY_IGNORES = (
    "test/close.test.js",
    "test/custom-http-server.test.js",
    "test/https/custom-https-server.test.js",
    "test/request-error.test.js",
    "test/client-timeout.test.js",
    "test/versioned-routes.test.js",
)
FASTIFY_SUITE = "npm run unit -- --reporter=dot " + " ".join(f"-i {p}" for p in FASTIFY_IGNORES)

CLOSING = (
    "Implement the task completely and correctly. Search and inspect the repository as "
    "needed, including related definitions and call sites. Run individual tests or test "
    "files with the project test runner at any point while investigating. Choose the "
    "smallest coherent repair, run the project test suite once as your final verification "
    "step with `{suite}`, and preserve earlier task work in the persistent checkout.\n\n"
    "Do not modify tests, generated files, dependency locks, or evaluation controls. "
    "Do not use network-dependent commands."
)

FIXTURES: dict[str, dict[str, Any]] = {
    "beets": {
        "fixture_dir": ROOT / "sources/evaluations/fixtures/medium/beetbox-beets",
        "sequence_id": "beets-lifecycle-sequence-v2",
        "fixture_id": "medium-beetbox-beets",
        "suite": BEETS_SUITE,
        "is_production": lambda p: p.endswith(".py") and p.split("/")[0] in {"beets", "beetsplug"},
        "compile": lambda paths: " && ".join(
            f"uv run --offline --frozen python -m py_compile {p}" for p in paths
        ),
        "smoke": lambda tests: "uv run --offline --frozen pytest -q " + " ".join(tests),
        "project_compile": (
            'uv run --offline --frozen python -c "import ast, pathlib; '
            "[ast.parse(p.read_text(), filename=str(p)) for root in ('beets', 'beetsplug') "
            'for p in pathlib.Path(root).rglob(\'*.py\')]"'
        ),
    },
    "fastify": {
        "fixture_dir": ROOT / "sources/evaluations/fixtures/medium/fastify-fastify",
        "sequence_id": "fastify-lifecycle-sequence-v2",
        "fixture_id": "medium-fastify-fastify",
        "suite": FASTIFY_SUITE,
        "is_production": lambda p: p.endswith(".js") and (p.startswith("lib/") or p == "fastify.js"),
        "compile": lambda paths: " && ".join(f"node --check {p}" for p in paths),
        "smoke": lambda tests: " && ".join(f"node --test {t}" for t in tests),
        "project_compile": (
            "find lib -type f -name '*.js' -print0 | sort -z | xargs -0 -n1 node --check "
            "&& node --check fastify.js"
        ),
    },
}

# Each entry: the upstream commit whose production change is reversed, the behaviour the
# agent must restore, and the upstream tests that decide it. Prompts describe the symptom
# a user would report; they never name the file, function, or test.
TASKS: dict[str, list[dict[str, Any]]] = {
    "beets": [
        {
            "slug": "replace-command-callback",
            "commit": "d06774b14d",
            "title": "Restore the replace command's subcommand invocation",
            "symptom": (
                "The `replace` command fails as soon as it is invoked. Beets subcommands are "
                "called with the library, the parsed command-line options, and the remaining "
                "positional arguments, and this command's handler no longer accepts what the "
                "command framework passes it, so the call raises before any replacement work "
                "begins."
            ),
            "done": "invoking the replace command runs its normal argument handling instead of failing at the call boundary",
        },
        {
            "slug": "mpdstats-cli-overrides",
            "commit": "cf7c5e4eb2",
            "title": "Restore mpdstats command-line connection overrides",
            "symptom": (
                "The mpdstats command ignores the MPD host, port, and password given on the "
                "command line and always uses the configured values. Options supplied for a "
                "single invocation are expected to take precedence over configuration for that "
                "invocation only, and the decoding each option needs differs between them."
            ),
            "done": "host, port, and password supplied on the command line override the configured values for that run",
        },
        {
            "slug": "convert-missing-art",
            "commit": "755ca6f139",
            "title": "Skip album art that is recorded but absent",
            "symptom": (
                "Converting an album whose stored art path points at a file that no longer "
                "exists aborts the conversion. A recorded art path is not a guarantee that the "
                "file is present -- the cover may live in the album root rather than a per-disc "
                "directory -- and a missing source should be reported and stepped over rather "
                "than ending the run."
            ),
            "done": "conversion continues, logging the skipped art, when the recorded art file is not present",
        },
        {
            "slug": "importfeeds-symlink-failure",
            "commit": "65a01c2c2a",
            "title": "Keep importing when a feed link cannot be created",
            "symptom": (
                "An import stops with an error when the plugin that maintains a directory of "
                "links to imported music cannot create one of them. Link creation can fail for "
                "filesystem reasons that say nothing about the import itself, and the failure "
                "should be surfaced as a warning for that entry while the import proceeds."
            ),
            "done": "a link that cannot be created produces a warning and the import continues",
        },
        {
            "slug": "lyrics-rest-directory-config",
            "commit": "478ac8cb63",
            "title": "Honor the configured ReST output directory for lyrics",
            "symptom": (
                "The directory that lyrics are written to as ReST files can only be given on the "
                "command line. Setting it in configuration has no effect, because the option's "
                "default does not consult the plugin's configuration. The setting is optional and "
                "absent by default, and an explicit command-line value must still win."
            ),
            "done": "the ReST output directory can be set in configuration, with the command-line option overriding it",
        },
        {
            "slug": "musicbrainz-aliases-opt-in",
            "commit": "785f8b7a5c",
            "title": "Make artist aliases-as-credits opt-in",
            "symptom": (
                "Artist credits from MusicBrainz are always replaced by artist aliases. This "
                "changes tags for everyone whether they asked for it or not, and it should "
                "instead be a plugin setting that defaults to off, consulted where the credits "
                "are parsed."
            ),
            "done": "alias substitution happens only when the corresponding plugin setting is enabled, and defaults to off",
        },
        {
            "slug": "mbcollection-http-errors",
            "commit": "a0a88b5301",
            "title": "Handle MusicBrainz collection HTTP failures gracefully",
            "symptom": (
                "Updating a MusicBrainz collection lets a failed HTTP request escape as an "
                "unhandled error, ending the command. A remote service that is unreachable or "
                "returns an error is an expected condition for this operation and should be "
                "reported through the plugin's logging rather than terminating the run."
            ),
            "done": "an HTTP failure during a collection update is reported and handled instead of propagating",
        },
    ],
    "fastify": [
        {
            "slug": "trailer-duplicate-callback",
            "commit": "9026164f5a",
            "title": "Ignore duplicate trailer callback invocations",
            "symptom": (
                "A trailer callback that is invoked more than once -- which happens when a "
                "handler mixes a callback with an async return -- is counted more than once, so "
                "the bookkeeping that tracks outstanding trailers is wrong and the response can "
                "be finalised at the wrong time. Only the first invocation of a given trailer "
                "callback should have any effect."
            ),
            "done": "a trailer callback invoked repeatedly is honoured once and ignored thereafter",
        },
        {
            "slug": "nested-prefix-join",
            "commit": "2f597a9297",
            "title": "Join nested route prefixes without a doubled or missing separator",
            "symptom": (
                "Registering a plugin under a nested prefix can produce a malformed route path. "
                "When the enclosing prefix already ends with a separator and the plugin's own "
                "prefix does not begin with one, a separator is added anyway and the joined path "
                "contains two. The existing handling of the opposite case must keep working."
            ),
            "done": "nested prefixes join with exactly one separator in every combination of leading and trailing separators",
        },
        {
            "slug": "serializer-compiler-flag",
            "commit": "d76dbcd58b",
            "title": "Detect a custom serializer compiler correctly",
            "symptom": (
                "An instance configured with a custom serializer compiler is not recognised as "
                "having one, while an instance with only a custom validator compiler is "
                "sometimes treated as though it had both. The flag that records whether a custom "
                "serializer compiler was supplied is derived from the wrong member of the "
                "compiler factory."
            ),
            "done": "each custom-compiler flag reflects the presence of its own factory function",
        },
        {
            "slug": "sync-validator-throw",
            "commit": "d338dca5ab",
            "title": "Convert a synchronously thrown validator error into an internal error",
            "symptom": (
                "A custom validator that throws synchronously escapes the validation path "
                "uncaught, so the failure surfaces differently from the same fault in an "
                "asynchronous validator. A validator that throws is a server-side fault and must "
                "be reported as an internal error through the normal error path."
            ),
            "done": "a synchronously thrown validator error is captured and reported as an internal server error",
        },
        {
            "slug": "duplicated-route-method-array",
            "commit": "d9659819fb",
            "title": "Report duplicated routes registered with several methods",
            "symptom": (
                "Registering a route for more than one method at once loses the dedicated "
                "duplicate-route error when one of those methods is already declared. The check "
                "that recognises a duplicate assumes a single method value, so a multi-method "
                "registration is not matched and the caller receives an error without the "
                "framework's own error code."
            ),
            "done": "a duplicate is recognised when any of the registered methods collides, and the framework's duplicate-route error is raised",
        },
        {
            "slug": "head-route-web-stream",
            "commit": "dd02e428dd",
            "title": "Handle web stream payloads on automatic HEAD routes",
            "symptom": (
                "A handler that returns a web stream breaks the automatically generated HEAD "
                "route. Node streams are recognised and disposed of without sending a body, but "
                "a web stream is not, so it falls through to the branch that measures a buffer's "
                "length. A web stream should be cancelled, with any cancellation failure logged, "
                "and the response completed with no body."
            ),
            "done": "a HEAD request against a handler returning a web stream completes with no body and the stream cancelled",
        },
    ],
}

SETUP = """#!/usr/bin/env bash
set -euo pipefail
repo="${1:-${WORKFLOW_REPO:-}}"
[[ -n "$repo" ]] || { echo "usage: setup.sh <repo>" >&2; exit 2; }
git -C "$repo" apply "$(dirname "$0")/seed-regression.patch"
"""

RESET = """#!/usr/bin/env bash
set -euo pipefail
repo="${1:-${WORKFLOW_REPO:-}}"
[[ -n "$repo" ]] || { echo "usage: reset.sh <repo>" >&2; exit 2; }
git -C "$repo" apply --reverse "$(dirname "$0")/seed-regression.patch"
"""

VERIFY = """#!/usr/bin/env bash
set -uo pipefail
TASK_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$TASK_DIR/../.." && pwd)"
cd "${{WORKFLOW_REPO:-$PROJECT_DIR/repo}}"

# Controller-only Lifecycle V2 acceptance. These upstream cases are a narrow smoke for the
# task's essential behavior; broader checks remain diagnostic.
{compile} &&
  {smoke}
"""


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {result.stderr[:300]}")
    return result.stdout


def build(fixture: str) -> list[dict[str, Any]]:
    spec = FIXTURES[fixture]
    repo = spec["fixture_dir"] / "repo"
    generation_dir = spec["fixture_dir"] / "task-generations" / GENERATION
    entries: list[dict[str, Any]] = []

    for order, task in enumerate(TASKS[fixture], start=1):
        commit = task["commit"]
        changed = [
            line for line in git(repo, "show", "--name-only", "--format=", commit).splitlines() if line
        ]
        files = [line for line in changed if spec["is_production"](line)]
        tests = [line for line in changed if line.startswith("test/")]
        patch = git(repo, "diff", commit, f"{commit}^", "--", *files)

        task_id = f"{fixture}-{task['slug']}-v2"
        task_dir = generation_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "seed-regression.patch").write_text(patch)
        (task_dir / "setup.sh").write_text(SETUP)
        (task_dir / "reset.sh").write_text(RESET)
        compile_command = spec["compile"](files)
        smoke_command = spec["smoke"](tests)
        (task_dir / "verify.sh").write_text(
            VERIFY.format(compile=compile_command, smoke=smoke_command)
        )
        for script in ("setup.sh", "reset.sh", "verify.sh"):
            (task_dir / script).chmod(0o755)

        closing = CLOSING.format(suite=spec["suite"])
        prompt = (
            f"# {task['title']}\n\n{task['symptom']}\n\n"
            f"The task is complete when {task['done']}.\n\n{closing}\n"
        )
        (task_dir / "agent-prompt.txt").write_text(prompt)
        (task_dir / "task.md").write_text(
            f"# {task['title']}\n\n{task['symptom']}\n\n"
            f"Completion condition: {task['done']}.\n\n"
            f"Derived by reversing the production half of upstream `{commit}`; the covering "
            f"upstream tests are {', '.join(tests)}.\n"
        )

        entries.append({
            "id": task_id,
            "order": order,
            "task_class": "defect-repair",
            "prompt_path": str((task_dir / "agent-prompt.txt").relative_to(ROOT)),
            "verifier_command": str((task_dir / "verify.sh").relative_to(ROOT)),
            # Empty by design: these covering tests already ship in the pinned checkout,
            # so nothing is introduced that would need concealing from the model. The
            # oracle stays controller-only because the prompt never names them.
            "upstream_test_paths": [],
            "compatibility_rebased_test_paths": [],
            "model_concealed_paths": [],
            "expected_changed_paths": sorted(files),
            "model_visible_validation_anchors": [],
            "acceptance_visibility": "controller-only-compile-plus-essential-smoke",
            "model_visible_acceptance_asset_paths": [],
            "compile_command": compile_command,
            "essential_smoke_command": smoke_command,
        })
    return entries


def main() -> int:
    generated = {}
    for fixture in FIXTURES:
        entries = build(fixture)
        generated[FIXTURES[fixture]["sequence_id"]] = entries
        print(f"{fixture}: generated {len(entries)} bounded tasks")
    out = ROOT / "sources/evaluations/audits/lifecycle-v2-task-entries.json"
    out.write_text(json.dumps(generated, indent=2) + "\n")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
