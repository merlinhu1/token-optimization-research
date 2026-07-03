# Profile assignment: Recorded xcodebuild diagnostic preservation

## Fixture

- Fixture ID: `recorded-xcodebuild-diagnostic`
- Primary surface: `apple-build-output`
- Verifier: `cd sources/evaluations/fixture-corpus/v1/recorded-xcodebuild-diagnostic/repo && python3 verify_compaction.py`

## Profiles to run

| Run role | Profile ID | Components enabled | Disabled overlaps | Required evidence |
|---|---|---|---|---|
| baseline | `baseline-codex-no-mcp` | Codex CLI no-MCP substrate | all MCP and token-saving add-ons | provider usage, transcript, verifier, diff/artifact |
| treatment | `terminal-xcsift` | see `../../profile-matrix.md` | all unlisted owners for `apple-build-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `terminal-rtk` | see `../../profile-matrix.md` | all unlisted owners for `apple-build-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `terminal-headroom` | see `../../profile-matrix.md` | all unlisted owners for `apple-build-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |

## Run order

1. Baseline native-agent run.
2. Single-surface treatments before any composed stack.
3. Stack or replacement-runtime treatments only after baseline artifacts exist.
4. Repeat or alternate order if provider/session effects are suspected.
