---
name: citation-light-prior-art-mapper
description: Use when writing practical AI/CS software research reports that need prior-art context without becoming citation-heavy literature reviews.
---
# Citation-Light Prior-Art Mapper

## Purpose

This repository evaluates cutting-edge practical software. It should cite or link selectively, but primary evidence comes from running and inspecting software.

## When to Use

Use when writing report background, related-work, method-lineage, benchmark-provenance, or tool-comparison sections.

## Rules

1. Group prior art by mechanism or surface, not by one paragraph per repository.
2. Use citations/links for:
   - benchmark provenance;
   - method lineage;
   - external evaluation standards;
   - tools that anchor a category.
3. Do not cite every README or GitHub repo in the report body.
4. Keep raw provenance in dossiers, data files, and `sources/` artifacts.
5. Prefer direct software evidence for claims about behavior:
   - inspected source code;
   - benchmark harnesses;
   - provider-billed token usage;
   - verifier outputs;
   - software-quality review;
   - negative findings.
6. Avoid generic literature-review claims unless they affect evaluation design.

## Related-Work Paragraph Pattern

1. Name the mechanism group.
2. State what the group generally attempts.
3. State the evaluation-relevant limitation or risk.
4. State how this repository tests that mechanism practically.

## Common Pitfalls

- Turning a practical benchmark report into a survey paper.
- Using citations as a substitute for source inspection or measurement.
- Dumping raw provenance paths in report body text.
- Hiding strongest practical baselines because they are inconvenient.
