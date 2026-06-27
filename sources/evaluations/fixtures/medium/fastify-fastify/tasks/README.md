# Fastify primary task set

All tasks target `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd` and use behavioral acceptance only.

1. `fastify-log-controller-regression` — centralized logging behavior, 15 production/type files.
2. `fastify-max-param-length-regression` — 414 routing and framework-error behavior, 6 production/type files.
3. `fastify-request-media-type-regression` — parsed request media-type behavior, 5 production/type files.
4. `fastify-content-type-semantics-regression` — structured Content-Type parsing and reply behavior, 5 production files.
5. `fastify-request-lifecycle-regression` — request lifecycle work elimination and reply completion behavior, 5 production files.

Each task directory contains a controller-only seed, verifier, and provenance note plus one sanitized model-facing prompt. The runner copies controller assets outside the target repository and discloses prompts one task at a time.
