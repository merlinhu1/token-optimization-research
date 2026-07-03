# django-36560-qualified-cache-control-regression

## Fixture

- Fixture ID: `large-django-django`
- Project: `django-django`
- Upstream: `django/django`
- Real issue/PR source: `#36560 / CVE-2026-35193`
- Pinned fixed commit: `b461519bf5973d7fc149560d2f99acdba71a437d`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair cache and conditional-response handling so qualified Cache-Control directives such as public="..." and no-store="..." are parsed by directive name.

## Why this is relatively complex

Requires coordinating header parsing, cache middleware, conditional GET middleware, and helper APIs.

The seed patch reverses production-code portions of a real upstream fix across 4 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the pinned fixed commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/large-projects/django-django/tasks/django-36560-qualified-cache-control-regression/agent-prompt.txt`
- SHA-256: `09cbaed5d48b72605e3c4c40a2dbb210cfa45495a1daa6a005b0161070ede2eb`

## Verifier

```bash
sources/evaluations/large-projects/django-django/tasks/django-36560-qualified-cache-control-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
PYTHONPATH=. python tests/runtests.py cache.tests.CacheUtils.test_patch_cache_control_whitespace_around_equals cache.tests.CacheMiddlewareTest.test_qualified_cache_control_value_not_cached cache.tests.CacheMiddlewareTest.test_authorization_header_exception_qualified_public_directive middleware.tests.ConditionalGetMiddlewareTest.test_no_etag_no_store_qualified utils_tests.test_http.SplitDirectiveNamesTests.test_basic --verbosity 2
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
