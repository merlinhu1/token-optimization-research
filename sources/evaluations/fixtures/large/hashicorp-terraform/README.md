# hashicorp/terraform production workflow fixture

Fixture ID: `large-hashicorp-terraform`

- Status: active production comparison fixture
- Upstream: `https://github.com/hashicorp/terraform`
- Pinned snapshot: `e02391ad384c9c38f1d7f40b853c0d2297348094`
- Runtime: Go
- Active sequence: `terraform-maintenance-sequence-v2`
- Qualification: `qualification-composite-v6.json`

The active workflow has three sequential tasks: tracing-context propagation, computed-block provider capabilities, and strict/const-only variable parsing. All seed regressions coexist in one concealed composite broken start, prompts are disclosed one at a time, and cumulative verification runs after the final prompt.

The local `repo/`, dependency caches, and run scratch trees are generated and must not be committed.
