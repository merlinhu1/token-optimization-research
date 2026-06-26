# Profile matrix

| Profile ID | Components enabled | Owned surfaces | Used for | Main failure mode | Required metric |
|---|---|---|---|---|---|
| `baseline-codex-no-mcp` | Codex CLI no-MCP substrate; native shell/edit/file operations allowed | none | all fixtures | broad reads and repeated logs | provider-billed usage, verifier, quality |
| `terminal-rtk` | RTK only | terminal/tool-output compaction | terminal fixtures | diagnostic loss or hook overhead | artifact tokens, diagnostic preservation |
| `terminal-lowfat` | Lowfat only | terminal/tool-output compaction | terminal fixtures | command plugin brittleness | artifact tokens, diagnostic preservation |
| `terminal-snip` | Snip only | terminal/tool-output compaction | terminal fixtures | hook/proxy raw-output loss | artifact tokens, raw recovery |
| `terminal-tokenjuice` | TokenJuice only | terminal/tool-output compaction | terminal fixtures | host-hook coupling | artifact tokens, reset success |
| `terminal-headroom` | Headroom terminal mode only | terminal/tool-output compaction | terminal fixtures | broad owner accidentally enabled | artifact tokens, enabled-surface audit |
| `terminal-xcsift` | xcsift only | Apple build output parsing | recorded xcodebuild fixture | misses Swift diagnostic fact | diagnostic fact preservation |
| `retrieval-codegraph` | CodeGraph only | retrieval/context | retrieval fixtures | stale or irrelevant target | target returned within budget |
| `retrieval-cartog` | Cartog only | retrieval/context | retrieval fixtures | graph misses edit target | target returned within budget |
| `retrieval-graphify` | Graphify only | retrieval/context | retrieval fixtures | graph construction overhead | target returned plus index cost |
| `retrieval-serena` | Serena only | retrieval/context/editing | retrieval fixtures | LSP/index setup failure | target returned and verifier pass |
| `retrieval-sigmap` | SigMap only | signature-map retrieval | retrieval fixtures | signature too shallow | target returned within budget |
| `retrieval-leanctx` | LeanCTX retrieval only | retrieval/context | retrieval fixtures | broad owner leakage | target returned plus surface audit |
| `memory-cavemem` | Cavemem only | memory/reinjection | memory fixture | stale convention injection | rediscovery reduction, verifier |
| `memory-claude-mem` | Claude Mem only | memory/reinjection | memory fixture | overbroad memory scope | rediscovery reduction, verifier |
| `memory-mex` | MEX only | memory/reinjection | memory fixture | drift or weak reset | rediscovery reduction, reset |
| `memory-total-agent-memory` | Total Agent Memory only | memory/reinjection | memory fixture | stale global memory | rediscovery reduction, reset |
| `lower-intervention-codegraph` | RTK + CodeGraph | terminal + retrieval | stack ablation | contribution ambiguity | ablation deltas |
| `lower-intervention-cartog` | RTK + Cartog | terminal + retrieval | stack ablation | contribution ambiguity | ablation deltas |
| `serena-cavemem-lightweight` | Snip + Serena + Cavemem | terminal + retrieval + memory | stack ablation | stale memory or LSP overhead | provider usage, verifier |
| `sigmap-governance-artifact` | Lowfat + SigMap + MEX + Ponytail | terminal + retrieval + memory + artifact policy | stack ablation | too many control surfaces | ablation deltas, quality |
| `broad-context-owner` | LeanCTX alone, or LeanCTX + Ponytail in separate ablation | broad context owner | broad-owner fixture | hidden overlap with narrow tools | surface audit, verifier |
| `integrated-mcp-owner` | Token Savior MCP profile | integrated MCP owner | broad/tool-heavy fixtures | tool-call overhead | provider usage, trace recovery |
| `codescope-owner` | Codescope alone | broad code-intelligence owner | broad-owner fixture | heavy setup/index cost | setup time, verifier |
| `swarmvault-owner` | SwarmVault alone | wiki/graph owner | broad-owner fixture | stale wiki/context | verifier, evidence trace |
| `broad-compression-owner` | Headroom or Claw Compactor alone | broad compression/proxy | broad-owner fixture | schema/code fidelity loss | verifier, raw recovery |
| `mcp-offload` | pctx + jcodemunch MCP + Caveman | execution offload + retrieval + behavior style | tool-trace fixture | final answer loses evidence IDs | verifier, trace-size reduction |
| `tokless-profile` | Tokless-generated selected profile | installer/orchestrator only | installer fixture | hidden extra owners | generated-config diff, cleanup |
| `maestro-orchestrator` | Maestro Flow alone | orchestration/context budget | installer/workflow fixture | workflow overhead | cleanup, latency, verifier |
| `grace-artifact-project` | Grace Marketplace on GRACE fixture | artifact/governance | installer fixture | generated artifact mismatch | config audit, verifier |
| `replacement-clawcodex` | ClawCodex runtime | replacement runtime | replacement fixture | baseline non-parity | verifier, cost, latency |
| `replacement-caveman-code` | Caveman Code runtime | replacement runtime | replacement fixture | baseline non-parity | verifier, cost, latency |
