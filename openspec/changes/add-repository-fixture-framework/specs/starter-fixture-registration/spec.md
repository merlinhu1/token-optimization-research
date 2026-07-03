## ADDED Requirements

### Requirement: Starter fixture selection

The implementation SHALL register a small starter set of repository fixture candidates for the first evaluation pass.

#### Scenario: Starter set has bounded size

- **WHEN** starter fixtures are registered
- **THEN** the registry contains between three and five starter fixture candidates for the initial pass
- **AND** each starter candidate has exactly one primary token-waste surface

#### Scenario: Starter set covers distinct task classes

- **WHEN** the starter fixture set is reviewed
- **THEN** it includes candidates for noisy terminal/build repair, large-codebase navigation, repeated-task memory rediscovery, and broad-owner/context evaluation
- **AND** Apple/Xcode build repair is included only if a realistic local fixture and verifier are available or explicitly marked blocked

### Requirement: Candidate records are not overpromoted

Starter fixture records SHALL begin at the lowest truthful readiness state unless concrete verifier, reset, and fixture-commit evidence already exists.

#### Scenario: Candidate without complete readiness remains candidate

- **WHEN** a starter fixture lacks a concrete verifier command, reset command, setup command, or frozen commit
- **THEN** its status is `candidate-fixture`
- **AND** the missing readiness item is recorded as a blocker or caveat

#### Scenario: Qualified fixture has concrete readiness evidence

- **WHEN** a starter fixture is marked `qualified-fixture`
- **THEN** it has a concrete fixture commit or snapshot policy, setup command, reset command, verifier command, task prompt path or prompt policy, and artifact path policy

### Requirement: Starter records identify evaluation use

Each starter fixture record SHALL identify what kind of future evaluation it enables.

#### Scenario: Starter fixture names future evaluation lane

- **WHEN** a starter fixture record is inspected
- **THEN** it lists the intended future evaluation lane such as terminal-only bakeoff, retrieval bakeoff, memory rediscovery ablation, broad-owner single-owner test, or Apple specialized terminal test
- **AND** it lists the later Phase 2 profile IDs that may use the fixture without making those profiles active treatments yet

### Requirement: Starter fixture docs link to progressive evaluation workflow

The starter fixture registration SHALL connect fixture records to the existing progressive evaluation workflow.

#### Scenario: Future evaluation can reference fixture ID

- **WHEN** a future evaluation change is created
- **THEN** its proposal or protocol can reference a fixture ID from `data/repository-fixtures.json`
- **AND** the fixture record provides enough setup, reset, verifier, and artifact-location context to freeze a protocol without rereading all Phase 1 reports

### Requirement: Starter fixture registration preserves negative and blocked states

The starter fixture registration SHALL preserve unsuitable or blocked fixture candidates instead of silently dropping them when they are relevant to a task class.

#### Scenario: Blocked candidate remains reviewable

- **WHEN** a candidate fixture is not currently runnable
- **THEN** the registry can keep it as `candidate-fixture` with blockers
- **AND** the registry does not present the blocked candidate as treatment-ready
