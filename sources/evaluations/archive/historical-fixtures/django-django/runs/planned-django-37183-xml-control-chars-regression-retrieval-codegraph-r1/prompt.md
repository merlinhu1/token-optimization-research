# Evaluation isolation contract

You are running inside the `retrieval-codegraph` treatment lane for CodeGraph. Tool-state condition: `cold`. Tool-use policy: `optional`. CodeGraph is available as an optional retrieval/context tool. Use it only when graph-backed navigation is likely to reduce total context or improve localization; otherwise use Codex native shell/file tools. Do not use other retrieval, compression, memory, or token-saving tools. Work only inside the target repository and use the verifier as the acceptance gate.

---

You are repairing a real issue-derived regression in django/django.

Issue source: #37183
Task: Repair Django XML/syndication escaping so control characters cannot be written into XML attributes.

The repository has already been checked out at the pinned fixed upstream commit and then seeded with a regression that removes the relevant production fix. Do not look for a toy one-line answer; this is intentionally a multi-file large-project task.

Constraints:
- Work only inside the fixture repository.
- Use the verifier below as the acceptance gate.
- Prefer the smallest maintainable production-code change that restores the real upstream behavior.
- Do not modify tests unless you can justify that the upstream test itself is wrong.
- Preserve project style and existing public APIs.

Complexity note: Requires tracing XML attribute serialization through both core serializer output and feed-generation helpers.

Verifier:
PYTHONPATH=. python tests/runtests.py serializers.test_xml.XmlSerializerTestCase.test_control_char_failure_attribute syndication_tests.tests.SyndicationFeedTest.test_no_control_chars_in_attributes --verbosity 2
