# Fastify Lifecycle V2 fixture

- Upstream: `https://github.com/fastify/fastify.git`
- Snapshot: `94bcbcc6e2ef3b8e8f8e8797fe551ccbe7b942fd`
- Prepared base: `9246fddd50b8031a8b943ef50c5abff8df48be29`
- Sequence: `fastify-lifecycle-sequence-v2`
- Active generation: `lifecycle-v2`
- Qualification: `qualification-lifecycle-v2-20260818.json`
- Tasks: 6 bounded defect repairs, each restoring one named behavior a specific upstream test decides

The controller builds the prepared base before anything is seeded: six upstream test files fail on a clean checkout of the pin in the sandboxed lane, and not for any reason the pin owns. The sandbox resolves `localhost` to `::1` ahead of `127.0.0.1`, so a server bound through a `serverFactory` listens on `::1` while undici's `fetch` connects IPv4-first and is refused; upstream v5.11.3, 34 days past the pin, fails the same seven cases. Left in place they showed every run seven failures the agent did not cause and could not fix, and whether it investigated them was variance charged to the measurement. The removal is committed onto the pinned tree with a fixed identity and date, so the prepared base is a reproducible commit that both the evaluation checkout and this local fixture pin; `initial_snapshot.prepared_removals` in `data/workflow-task-sequences.json` is the single source of the path list and that hash. On the prepared base the clean tree exits zero and every seeded regression still fails underneath, so the suite remains a valid oracle.

The controller then applies all six semantic regressions as one composite start before prompt 1. Agents receive normal engineering objectives and are expected to implement them correctly; evaluator scoring and controller commands are not model-facing. After the final prompt, the controller compiles every affected component, runs one narrow upstream essential-behavior smoke per task, and performs a project-wide JavaScript syntax compile. Broader tests, behavior, style, and source-review quality are diagnostics. The current verifier bytes require a new provider pilot before treatment launch.
