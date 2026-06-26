# django-36492-sqlite-boolean-literal-regression

## Fixture

- Fixture ID: `large-django-django`
- Project: `django-django`
- Upstream: `django/django`
- Real issue/PR source: `#36492`
- Pinned fixed commit: `4bbc27c8686f10f9556cef02dbfa9f5157fbcf56`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair boolean exact lookup compilation for databases without native boolean fields while preserving annotation and expression behavior.

## Why this is relatively complex

Requires backend feature/operation behavior and ORM lookup compilation across literal, annotation, Exists, Case, and RawSQL paths.

The seed patch reverses production-code portions of a real upstream fix across 6 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the pinned fixed commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/archive/historical-fixtures/django-django/tasks/django-36492-sqlite-boolean-literal-regression/agent-prompt.txt`
- SHA-256: `a3d839de4a4f16980091723b5f84f5bd5d7414073a8787546315922b007cb1ad`

## Verifier

```bash
sources/evaluations/archive/historical-fixtures/django-django/tasks/django-36492-sqlite-boolean-literal-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
PYTHONPATH=. python tests/runtests.py lookup.tests.LookupTests.test_exact_booleanfield lookup.tests.LookupTests.test_exact_booleanfield_annotation --verbosity 2
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
