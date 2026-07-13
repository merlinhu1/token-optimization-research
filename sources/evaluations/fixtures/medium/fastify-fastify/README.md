# fastify/fastify primary-objective fixture

Fixture ID: `medium-fastify-fastify`

- Status: qualified five-task primary-objective lane
- Evaluation use: primary-objective provider-token comparison
- Upstream: `https://github.com/fastify/fastify`
- Pinned snapshot: `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd`
- Qualification: `qualification-composite-v5.json`
- Sequence: `fastify-maintenance-sequence-v1`
- Corrected GPT-5.5 high fingerprint: `109705c35eff`; current hard baseline `baseline-fastify-20260713-p-109705c35eff-r0` (4/5 verified, 45,449,446 tokens)
- Corrected GPT-5.6 Luna xhigh fingerprint: `a9c642bc016a`; current accepted baseline `baseline-fastify-20260713-p-a9c642bc016a-r0` (5/5 verified, 64,598,189 tokens)

The prior strengthened verifier snapshot was superseded because it required exact error/log messages, internal symbol shape, request-header object identity, Content-Type cache identity, and exact serialization details not required by the prompts. Post-hoc replay of the GPT-5.5 high implementation passes all five corrected behavioral surfaces.

Report operational completion, agent-declared completion, verifier-confirmed behavior, and provider tokens separately. Pair each treatment with a baseline from the same prompt-aligned frozen model condition and protocol fingerprint.

See `docs/research/hard-lane-evidence.md`.
