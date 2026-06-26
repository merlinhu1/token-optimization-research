# Profile assignment: Node ESM import repair

## Fixture

- Fixture ID: `node-esm-import-repair`
- Primary surface: `build-output`
- Verifier: `cd sources/evaluations/fixture-corpus/v1/node-esm-import-repair/repo && node --test`

## Profiles to run

| Run role | Profile ID | Components enabled | Disabled overlaps | Required evidence |
|---|---|---|---|---|
| baseline | `baseline-codex-no-mcp` | Codex CLI no-MCP substrate | all MCP and token-saving add-ons | provider usage, transcript, verifier, diff/artifact |
| treatment | `terminal-rtk` | see `../../profile-matrix.md` | all unlisted owners for `build-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `terminal-lowfat` | see `../../profile-matrix.md` | all unlisted owners for `build-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `terminal-snip` | see `../../profile-matrix.md` | all unlisted owners for `build-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `retrieval-leanctx` | see `../../profile-matrix.md` | all unlisted owners for `build-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |

## Run order

1. Baseline native-agent run where applicable.
2. Single-surface treatments before composed stack treatments.
3. Repeat or alternate order if provider/session effects are suspected.
