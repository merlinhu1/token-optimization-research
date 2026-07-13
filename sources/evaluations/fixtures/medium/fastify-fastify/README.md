# fastify/fastify primary-objective fixture

Fixture ID: `medium-fastify-fastify`

- Status: qualified five-task primary-objective lane
- Evaluation use: primary-objective provider-token comparison
- Upstream: `https://github.com/fastify/fastify`
- Pinned snapshot: `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd`
- Qualification: `qualification-composite-v5.json`
- Sequence: `fastify-maintenance-sequence-v1`
- Current GPT-5.6 Luna xhigh fingerprint: `6a8afd4b63ca`; primary-objective hard baseline `baseline-fastify-20260713-p-6a8afd4b63ca-r0` (5/5 disclosed surfaces, quality 3/5, 60,671,087 tokens). It is not objective-accepted because final-tree review found undefined `kLogController` state.
- Superseded intermediate fingerprints: GPT-5.5 high `109705c35eff`, GPT-5.6 Luna xhigh `a9c642bc016a`

The prior overconstrained verifier snapshot was superseded because it required exact error/log messages, internal symbol shape, request-header object identity, Content-Type cache identity, and exact serialization details not required by the prompts. A later independent source review then exposed under-coverage in the intermediate correction: default 414 handling and explicitly restored logger compatibility behavior were not enforced. The current contract adds those prompt-aligned behavioral gates.

Report operational completion, agent-declared completion, verifier-confirmed behavior, and provider tokens separately. Pair each treatment with a baseline from the same prompt-aligned frozen model condition and protocol fingerprint.

See `docs/research/hard-lane-evidence.md`.
