# Profile assignment: Python noisy unit-test repair

## Fixture

- Fixture ID: `py-noisy-unit-failure`
- Primary surface: `terminal-output`
- Verifier: `cd sources/evaluations/fixture-corpus/v1/py-noisy-unit-failure/repo && python3 -m unittest discover -s tests -v`

## Profiles to run

| Run role | Profile ID | Components enabled | Disabled overlaps | Required evidence |
|---|---|---|---|---|
| baseline | `baseline-codex-no-mcp` | Codex CLI no-MCP substrate | all MCP and token-saving add-ons | provider usage, transcript, verifier, diff/artifact |
| treatment | `terminal-rtk` | see `../../profile-matrix.md` | all unlisted owners for `terminal-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `terminal-lowfat` | see `../../profile-matrix.md` | all unlisted owners for `terminal-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `terminal-snip` | see `../../profile-matrix.md` | all unlisted owners for `terminal-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `terminal-tokenjuice` | see `../../profile-matrix.md` | all unlisted owners for `terminal-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |
| treatment | `terminal-headroom` | see `../../profile-matrix.md` | all unlisted owners for `terminal-output` | provider usage or artifact tokens, transcript, verifier, reset evidence |

## Run order

1. Baseline native-agent run.
2. Single-surface treatments before any composed stack.
3. Stack or replacement-runtime treatments only after baseline artifacts exist.
4. Repeat or alternate order if provider/session effects are suspected.
