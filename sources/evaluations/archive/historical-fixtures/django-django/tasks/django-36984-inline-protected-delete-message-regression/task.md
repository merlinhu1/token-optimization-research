# django-36984-inline-protected-delete-message-regression

## Fixture

- Fixture ID: `large-django-django`
- Project: `django-django`
- Upstream: `django/django`
- Real issue/PR source: `#36984`
- Pinned fixed commit: `57c8c8b107248a3358dd26276ac497c577454011`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair Django admin inline deletion messaging so protected related objects respect delete_confirmation_max_display.

## Why this is relatively complex

Requires understanding admin inline checks, protected delete collection, and rendering-side message limits.

The seed patch reverses production-code portions of a real upstream fix across 2 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the pinned fixed commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/archive/historical-fixtures/django-django/tasks/django-36984-inline-protected-delete-message-regression/agent-prompt.txt`
- SHA-256: `23cb353eddf9ee5d767b0ccc49d1bc8cf83cfbedc89bb02cb5d5ba49271bfa7d`

## Verifier

```bash
sources/evaluations/archive/historical-fixtures/django-django/tasks/django-36984-inline-protected-delete-message-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
PYTHONPATH=. python tests/runtests.py admin_inlines.tests.TestInline.test_delete_protected_message_limits_number_of_objects_displayed admin_inlines.tests.TestInline.test_delete_protected_message_does_not_limit_small_amount_of_objects modeladmin.test_checks.DeleteConfirmationMaxObjectsCheckTests.test_inline_not_integer --verbosity 2
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
