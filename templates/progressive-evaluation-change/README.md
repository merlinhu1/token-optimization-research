# Progressive evaluation change template

Copy this directory to `docs/evaluations/changes/<change-id>/` before starting a bounded evaluation.

Recommended command:

```bash
change_id=YYYY-MM-DD-lane-target
mkdir -p "docs/evaluations/changes/$change_id"
cp templates/progressive-evaluation-change/{proposal.md,protocol.md,tasks.md,status.json,results.md} "docs/evaluations/changes/$change_id/"
```

Then fill the files in this order:

1. `proposal.md`
2. `protocol.md`
3. `tasks.md`
4. `status.json`
5. `results.md` after evidence exists

Raw transcripts, provider usage, verifier output, and quality reviews belong under `sources/evaluations/<evaluation-id>/`, not in this change directory.
