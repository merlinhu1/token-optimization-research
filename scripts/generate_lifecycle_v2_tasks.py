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
# Six Fastify test files fail on a clean checkout of the pinned commit in the sandboxed lane
# because the sandbox resolves `localhost` to ::1 first; the fixture preparation script removes
# them from the prepared base, so the suite command carries no exclusion list. See
# sources/evaluations/fixtures/medium/fastify-fastify/setup.sh.
FASTIFY_SUITE = "npm run unit -- --reporter=dot"

# Prompt design, derived from measured exploration variance across replicates.
#
# beets-concurrent-plugin-dispatch reproduced to 0.2% between replicates while siblings reached
# 27-57%. What separates it is precision about the *observable*, never about the location: naming
# files, symbols or tests is forbidden (ADR 0005) and would suppress the retrieval this study
# exists to measure. Four properties travel with the low-variance prompts:
#
#   1. A symptom distinctive enough that it could not describe anything else in the project, so the
#      search converges instead of sampling plausible areas.
#   2. A mechanism stated in terms a reader recognises as a known defect shape, so recognition takes
#      over from exploration once the right code is in view.
#   3. One required behavioural change; bundled requirements multiply the paths a run can take.
#   4. No design latitude in the repair, so two runs cannot pick different valid designs.
#
# The high-variance prompts each broke at least one. migration-text-paths bundled two requirements
# behind a rarely exercised entry point; subcommand-help-alignment carried a title that read as the
# opposite of its own completion condition.

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
            "slug": "unique-path-counter",
            "commit": "a8439e2d07",
            "title": "Continue a unique-name counter past nine",
            "symptom": (
                "When a destination file already exists, a numeric suffix is appended and incremented until the "
                "name is free. Once the existing suffix reaches two or more digits the counter restarts near zero "
                "instead of continuing, because the pattern that reads the existing suffix captures only its "
                "final digit. Single-digit suffixes already behave correctly."
            ),
            "done": "an existing numeric suffix of any length is read whole, so the next free name continues from it",
        },
        {
            "slug": "empty-string-field-split",
            "commit": "7b59604c54",
            "title": "Do not split an empty single-value field into a list",
            "symptom": (
                "Reading a single-value field that is empty and deriving its list counterpart searches the empty "
                "text for a separator, finds none, and takes a fallback path intended for text that simply has no "
                "separator in it. An empty value has nothing to split and should be left alone rather than routed "
                "through the splitting logic at all."
            ),
            "done": "an empty single-value field yields no list entries instead of being split",
        },
        {
            "slug": "date-query-alternation",
            "commit": "4a1e9164a1",
            "title": "Reject a malformed relative date instead of crashing",
            "symptom": (
                "A date query written with a stray pipe, as a user might type expecting it to mean 'or', crashes "
                "with an uncaught lookup error rather than the documented parse error. The pattern that "
                "recognises a relative date encloses its sign and its unit in character classes that also list a "
                "pipe, so the pipe is accepted as a valid unit and then fails when that unit is looked up."
            ),
            "done": "a date query containing a stray pipe raises the documented parse error instead of an uncaught lookup failure",
        },
        {
            "slug": "membership-query-hashable",
            "commit": "eb7c832fc9",
            "title": "Make a membership query hashable when its pattern is a sequence",
            "symptom": (
                "Hashing a query that tests membership in a collection raises an unhashable-type error whenever "
                "the collection is a list, which breaks any caller that puts such a query in a set or dictionary. "
                "The inherited hashing hashes the pattern directly, and a sequence pattern cannot be hashed "
                "as-is."
            ),
            "done": "a membership query hashes successfully whether its pattern is a list or another sequence",
        },
        {
            "slug": "spotify-uri-extraction",
            "commit": "6a051f9699",
            "title": "Extract a Spotify identifier from a native URI",
            "symptom": (
                "Pasting a native Spotify URI of the form used by the desktop application, rather than a web "
                "link, yields no identifier at all. The pattern that recognises Spotify identifiers accepts a "
                "bare identifier and a web URL, but has no branch for the URI form, so extraction returns "
                "nothing. The two forms already recognised must keep working."
            ),
            "done": "a native Spotify URI yields the same identifier as the equivalent web link",
        },
        {
            "slug": "lyrics-keep-synced-override",
            "commit": "d9a1bde1c9",
            "title": "Allow a run to override the keep-synced setting",
            "symptom": (
                "The switch that skips items already holding synced lyrics can only be turned on from the command "
                "line. When the configuration enables it there is no way to turn it off for a single run, so a "
                "manual fetch cannot be forced to reprocess those items. Its help text also describes "
                "re-downloading rather than skipping, which is the opposite of what it does."
            ),
            "done": "the keep-synced behaviour can be switched off for one run from the command line, and its help text describes what it does",
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
            "title": "Join a nested route prefix with exactly one separator",
            "symptom": (
                "Registering a plugin under a nested prefix produces a route path containing two consecutive "
                "separators whenever the enclosing prefix already ends with one and the plugin's own prefix does "
                "not begin with one. The opposite arrangement, where the plugin's prefix supplies the separator, "
                "is already handled and must keep working."
            ),
            "done": "a nested prefix joins to its enclosing prefix with exactly one separator, whichever side supplies it",
        },
        {
            "slug": "serializer-compiler-flag",
            "commit": "d76dbcd58b",
            "title": "Derive each custom-compiler flag from its own factory function",
            "symptom": (
                "An instance given a custom serializer compiler is not recorded as having one, and an instance "
                "given only a custom validator compiler is recorded as having both. The two flags that record "
                "which custom compilers were supplied are read from the same member of the compiler factory, so "
                "the serializer flag reports whether a validator was supplied."
            ),
            "done": "the validator flag reflects a supplied validator compiler and the serializer flag reflects a supplied serializer compiler, independently",
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
