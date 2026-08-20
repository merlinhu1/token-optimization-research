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
            "slug": "library-file-error-message",
            "commit": "6e6fee93bf",
            "title": "Restore the path and reason in file read and write errors",
            "symptom": (
                "When reading or writing a media file fails, the reported error says only that a "
                "read or a write failed. The path that failed and the underlying reason are both "
                "lost, although the base error class already knows them and formats them into a "
                "message. The subclasses interpolate their parent into a string without asking it "
                "for that message, so what reaches the user is the placeholder text of an object "
                "rather than the detail the parent produced."
            ),
            "done": "a failed read or write reports the file path and the underlying reason alongside the operation that failed",
        },
        {
            "slug": "migration-text-paths",
            "commit": "2e3ca0a018",
            "title": "Migrate stored paths that were saved as text",
            "symptom": (
                "Converting a library to relative paths fails for users whose path values were set "
                "by hand through sqlite rather than written by the application, because those "
                "values come back as text where the migration expects bytes. The same scan also "
                "reads rows whose path is unset, which it cannot migrate and must not consider. "
                "Both the selection and the conversion need to account for this."
            ),
            "done": "the relative-path migration skips rows with no stored path and converts text path values without failing",
        },
        {
            "slug": "subcommand-help-alignment",
            "commit": "9e3f22b8be",
            "title": "Keep a short subcommand's description on its own line",
            "symptom": (
                "In the command listing, a subcommand whose name is short enough to share a line "
                "with its description is instead followed by a line break, so the description is "
                "pushed onto the next line and the column alignment the listing pays for is wasted. "
                "The separate handling of names too long to share a line must keep working."
            ),
            "done": "a subcommand short enough to share its line is followed by its description on that line instead of a break",
        },
        {
            "slug": "concurrent-plugin-dispatch",
            "commit": "ca36df2d00",
            "title": "Dispatch each metadata plugin to its own concurrent call",
            "symptom": (
                "Querying metadata sources concurrently returns the results of one source repeated "
                "instead of the results of each. The work submitted for every source closes over "
                "the loop variable rather than binding the source it was created for, so by the "
                "time the submitted work runs the variable holds whichever source was last in the "
                "sequence and every call targets that one."
            ),
            "done": "each metadata source contributes its own results when sources are queried concurrently",
        },
        {
            "slug": "cached-attribute-error-surface",
            "commit": "8a1f9d916a",
            "title": "Surface the real failure inside a cached attribute",
            "symptom": (
                "When the body of a lazily computed attribute raises a missing-attribute error, the "
                "attribute machinery treats it as the attribute itself being absent and falls back, "
                "so the reported failure names the outer attribute and hides where the error really "
                "came from. The failure should be re-raised as a different error class that stops "
                "the fallback, must still point at the line that actually failed, and must not print "
                "a second chained traceback for the same event."
            ),
            "done": "a missing-attribute failure inside a lazily computed attribute is reported against the line that raised it, without a chained duplicate traceback",
        },
        {
            "slug": "zero-penalty-display",
            "commit": "a734b9bce1",
            "title": "List only the penalties that actually applied",
            "symptom": (
                "The summary of why a match was penalised lists every penalty the comparison can "
                "produce, including those that scored nothing. A penalty that contributed no "
                "distance is not a reason the match was downgraded and should not appear among the "
                "reasons shown."
            ),
            "done": "the listed penalties include only those with a non-zero contribution",
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
