# django-37183-xml-control-chars-regression

## Fixture

- Fixture ID: `large-django-django`
- Project: `django-django`
- Upstream: `django/django`
- Real issue/PR source: `#37183`
- Pinned fixed commit: `67c407585ccdc01b76d78e33c082f23d46346747`
- Evidence stage target: `reproduction`
- Task class: `real-issue-derived-multi-file-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Repair Django XML/syndication escaping so control characters cannot be written into XML attributes.

## Why this is relatively complex

Requires tracing XML attribute serialization through both core serializer output and feed-generation helpers.

The seed patch reverses production-code portions of a real upstream fix across 2 production files while leaving the upstream verifier tests in place.

## Seeded start state

Apply `seed-regression.patch` after checking out the pinned fixed commit. The patch creates a controlled broken state by reverting production-code portions of the real upstream fix without using a user-owned repository.

## Agent prompt

- Path: `sources/evaluations/archive/historical-fixtures/django-django/tasks/django-37183-xml-control-chars-regression/agent-prompt.txt`
- SHA-256: `ddb5631d47d3a80301de96e42eb8625a2694f75f3c8e6c2b0e071ea9df8a051f`

## Verifier

```bash
sources/evaluations/archive/historical-fixtures/django-django/tasks/django-37183-xml-control-chars-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
PYTHONPATH=. python tests/runtests.py serializers.test_xml.XmlSerializerTestCase.test_control_char_failure_attribute syndication_tests.tests.SyndicationFeedTest.test_no_control_chars_in_attributes --verbosity 2
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the real issue-derived regression unless explicitly justified.
- The solution coordinates all affected production paths rather than hard-coding only the visible failing assertion.
- No forbidden ambient token-saving tools appear in the transcript for baseline runs.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.
