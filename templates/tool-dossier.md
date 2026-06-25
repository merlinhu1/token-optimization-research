# Tool dossier template

## Identity

- Repository:
- URL:
- Version/ref inspected:
- Snapshot status: pinned-commit | unpinned-historical-inspection
- Commit inspected:
- Commit URL:
- Source artifact path:
- Date inspected:
- Reviewer:
- Evidence stage: lead | source-logic | benchmark-audit | reproduction

Resolve moving refs such as GitHub `HEAD`, default branch names, tags that can be retargeted, or local working trees to an immutable commit SHA before writing source-logic claims. Use `Snapshot status: unpinned-historical-inspection` only for historical dossiers where the original pass did not record an immutable commit; do not backfill those with current upstream HEAD unless a fresh inspection is performed. Repositories that cannot provide auditable versioning for the inspected source are not valid candidates for recommendations, stack construction, benchmark-audit, or reproduction until refreshed against a pinned source snapshot.

## Summary

Neutral summary of what the tool does and where it intervenes.

## Evidence inventory

| Evidence type | Files/URLs inspected | Notes |
|---|---|---|
| README/docs | | |
| Installer/config/plugin files | | |
| Runtime source | | |
| Tests | | |
| Benchmarks/evaluations | | |
| Issues/discussions/community reports | | |

## Installation and integration behavior

- Supported agents:
- Installation commands:
- Config files written:
- Hooks/plugins/MCP servers installed:
- Disable/uninstall path:
- Failure behavior if dependency is missing:

## Runtime behavior

- Intervention surface:
- Input captured:
- Output emitted:
- State/cache/files written:
- Network/subprocess behavior:
- Raw-output recovery path:
- Security/privacy considerations:

## Token-saving mechanism

- Addressable token surface:
- Reduction method:
- Quality-preservation mechanism:
- Cases where savings may not translate to provider-billed reductions:

## Benchmarks and claims

| Claim | Source | Measurement scope | Reviewed method | Caveats |
|---|---|---|---|---|
| | | | | |

## Compatibility notes

- Compatible surfaces:
- Conflicting surfaces:
- Stack placement:
- Lower-intervention alternative:

## Failure modes and limits

- Known failure modes:
- Quality risks:
- Operational risks:
- Environments not supported:

## Open questions

- [ ]

## Next review tasks

- [ ] Inspect:
- [ ] Run:
- [ ] Compare:
- [ ] Update:
