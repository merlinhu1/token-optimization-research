# orchard-base64-string-decode-regression

## Fixture

- Project: `OrchardCMS/OrchardCore`
- Shared workflow base commit: `91cd8a4bfcaf9cb1388edef6867af2a0b5a0a000`
- Evidence stage target: `reproduction`
- Task class: `controlled-project-regression`
- Primary token-waste surface: `retrieval-context`

## Task summary

Restore pooled Base64 decoding for both string and stream callers.

Complexity upgrade: this task now verifies multiple related symptoms and uses a multi-edit seed patch rather than a one-line localized mutation.

## Seeded start state

Apply `seed-regression.patch` after checking out the shared workflow base commit. The patch creates a controlled broken state in production code while preserving the verifier.

## Agent prompt

- Path: `sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-base64-string-decode-regression/agent-prompt.txt`
- SHA-256: `bb4bb9b8691122ad88acde8015f9598a5b2f333c0ca54369d4c04982e70b51f6`

## Verifier

```bash
sources/evaluations/fixtures/large/orchardcms-orchardcore/tasks/orchard-base64-string-decode-regression/verify.sh
```

Verifier command inside the fixture repo:

```bash
DOTNET_ROOT="${DOTNET_ROOT:-/opt/data/dotnet}"; export DOTNET_ROOT PATH="$DOTNET_ROOT:$PATH" DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="${DOTNET_SYSTEM_GLOBALIZATION_INVARIANT:-1}"; "$DOTNET_ROOT/dotnet" test --no-restore --project test/OrchardCore.Tests/OrchardCore.Tests.csproj --filter-class "*Base64Tests"
```

## Success criteria

- Verifier exits 0 after the seeded regression is repaired.
- Diff is minimal and limited to the described regression unless explicitly justified.
- The solution addresses project behavior rather than hard-coding only the visible failing assertion.
- Provider-billed usage, raw transcript, verifier output, and final diff are saved under `runs/<evaluation-id>/`.

Five-file complexity bar: this seeded start state changes at least five production files, and the verifier includes source-invariant checks for every supplemental file-level regression.
