## ADDED Requirements

### Requirement: Fixture framework documentation

The repository SHALL document a repository fixture framework that explains how repositories become controlled Phase 2 evaluation fixtures before stack experiments run.

#### Scenario: Framework describes fixture purpose

- **WHEN** a researcher opens the fixture framework documentation
- **THEN** the documentation states that fixture qualification separates repository suitability from stack effectiveness
- **AND** the documentation states that fixture readiness does not promote any tool or stack to `benchmark-audit` or `reproduction`

#### Scenario: Framework defines task classes

- **WHEN** a researcher selects a fixture task class
- **THEN** the framework lists supported task classes including noisy terminal/build repair, large-codebase navigation, memory rediscovery, broad-owner/context evaluation, MCP/tool-heavy workflow where applicable, replacement-runtime comparison where applicable, and Apple/Xcode build repair where applicable
- **AND** each task class names its minimum verifier expectation

### Requirement: Fixture lifecycle states

The repository fixture framework SHALL define machine-checkable lifecycle states for repository readiness.

#### Scenario: Lifecycle states are explicit

- **WHEN** a fixture record is created or reviewed
- **THEN** its status is one of `candidate-fixture`, `qualified-fixture`, `baseline-run`, `treatment-ready`, or `retired-fixture`
- **AND** the framework defines the promotion condition for each state

#### Scenario: Fixture lifecycle is separate from evidence stage

- **WHEN** a fixture reaches `qualified-fixture`, `baseline-run`, or `treatment-ready`
- **THEN** the framework states that this status is repository-readiness evidence only
- **AND** the status does not imply `benchmark-audit` or `reproduction` evidence for a tool or stack

### Requirement: Structured fixture registry

The implementation SHALL add a structured fixture registry that can be validated without reading narrative reports.

#### Scenario: Fixture registry exists

- **WHEN** repository validation runs
- **THEN** a `data/repository-fixtures.json` file exists
- **AND** the file contains a schema version and a list of fixture records

#### Scenario: Fixture record has required fields

- **WHEN** a fixture record is validated
- **THEN** the record includes an ID, fixture status, repository identity, fixture source path or URL, frozen commit or snapshot policy, task classes, token-waste surfaces, setup command or setup blocker, reset command or reset blocker, verifier command or verifier blocker, artifact paths, and caveats

### Requirement: Fixture template

The implementation SHALL add a human-readable template for creating new repository fixture records.

#### Scenario: Template supports future fixture creation

- **WHEN** a researcher creates a new fixture candidate
- **THEN** `templates/repository-fixture.md` provides fields for identity, repository source, fixture commit, task classes, token-waste hypothesis, verifier, setup, reset, artifact paths, promotion state, blockers, and caveats

### Requirement: Fixture validation

The implementation SHALL validate fixture records as part of repository health checks.

#### Scenario: Fixture validation rejects invalid lifecycle states

- **WHEN** a fixture record uses an unknown status
- **THEN** validation fails with a diagnostic naming the fixture ID and invalid status

#### Scenario: Fixture validation rejects missing verifier information

- **WHEN** a fixture record lacks both a verifier command and a verifier blocker
- **THEN** validation fails with a diagnostic naming the fixture ID

#### Scenario: Fixture validation rejects duplicate fixture IDs

- **WHEN** two fixture records use the same ID
- **THEN** validation fails with a duplicate-ID diagnostic

### Requirement: No experiment execution in framework change

The framework implementation SHALL avoid running baseline, treatment, or stack-ablation experiments as part of this change.

#### Scenario: Framework change completes without measured results

- **WHEN** the framework change is completed
- **THEN** no stack is promoted because of the fixture framework alone
- **AND** no provider-billed savings claim is added
- **AND** fixture records remain readiness records until future evaluation changes collect evidence
