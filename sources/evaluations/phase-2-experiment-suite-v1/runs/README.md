# Runs Directory

Store one directory per executed baseline or treatment run here.

Required shape:

```text
runs/<evaluation-id>/
  task.md
  profile.md
  environment.json
  baseline-transcript.jsonl or treatment-transcript.jsonl
  provider-usage.json
  verifier-output.txt
  quality-review.md
  artifacts/
```

Do not record a compact row in `data/evaluations.json` until the raw run directory exists.
