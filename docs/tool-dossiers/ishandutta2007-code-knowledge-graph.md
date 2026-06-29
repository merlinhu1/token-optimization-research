# Tool dossier: ishandutta2007/Code-Knowledge-Graph

## Identity

- Repository: `ishandutta2007/Code-Knowledge-Graph`
- URL: https://github.com/ishandutta2007/Code-Knowledge-Graph
- Local clone inspected: `/tmp/token-leads-20260629/ishandutta2007__Code-Knowledge-Graph`
- Version/ref inspected: local shallow clone commit `1b1986717647`
- Date inspected: 2026-06-29
- Evidence stage: source-logic
- License observed in manifest: ISC

## Summary

Code-Knowledge-Graph is a small TypeScript MVP that scans TypeScript/JavaScript files, stores files and function/class/method symbols in SQLite, creates only file-to-symbol `contains` edges, and exposes two stdio MCP tools for symbol search and node details. Source logic shows useful lightweight indexing, but not a full call/dependency knowledge graph in the inspected commit.

## Evidence inventory

| Evidence type | Source file paths inspected | Notes |
|---|---|---|
| Manifest/entrypoints | `package.json`, `tsconfig.json` | npm scripts for `index`, `query`, `mcp`, `build`; ESM TypeScript with sqlite/glob/MCP deps. |
| CLI entrypoint | `src/index.ts` | Dispatches `index`, `query`, and `mcp`; database path fixed to `.ckg-index.db` in current working directory. |
| Indexer | `src/indexer.ts` | Glob scans `**/*.{ts,js}` excluding `node_modules`, `dist`, `.git`; TypeScript AST extracts functions/classes/methods. |
| SQLite schema | `src/db.ts` | Creates `nodes` and `edges` tables plus indexes on node path/name. |
| MCP server | `src/mcp.ts` | Stdio MCP server exposes `search_nodes` and `get_node_details` backed by SQLite queries. |

## Installation and integration behavior

- `package.json` scripts run `node --loader ts-node/esm src/index.ts` for CLI commands; `npm run index`, `npm run query`, and `npm run mcp` are wrappers.
- Index command writes `.ckg-index.db` in `process.cwd()`, not necessarily the indexed target directory.
- `index` clears all rows in `nodes` and `edges` before rebuilding, then closes the SQLite DB.
- `mcp` opens the same `.ckg-index.db` from current working directory and serves over stdio using `@modelcontextprotocol/sdk`.

## Runtime behavior

- Indexer reads each matched `.ts`/`.js` file fully and stores a `file` node containing full source text.
- It traverses the TypeScript AST and inserts `function`, `class`, and `method` nodes with relative path and start/end lines.
- It inserts `contains` edges from the file node to each symbol node; no call/import/inheritance edges were implemented in inspected source.
- `query` performs a simple `SELECT * FROM nodes WHERE name LIKE ?` and prints a console table.
- MCP `search_nodes` runs a `LIKE` query over node names with optional exact `type` filter; `get_node_details` returns the node row and children joined through `contains` edges.

## Token-saving mechanism

- Primary mechanism: lightweight pre-indexed symbol lookup lets an agent find files/line ranges for matching JS/TS symbols without grepping or reading every file.
- `get_node_details` can return file content or child symbol lists from SQLite; this may reduce discovery tool calls, but file content storage can also return large payloads.
- There is no inspected source logic for semantic search, call graph traversal, incremental indexing, output compression, token accounting, or automatic context budgeting.

## Benchmarks and claims

- README/description claims were not used as decision evidence.
- No benchmark artifact, raw output, or provider-token accounting was inspected; status remains source-logic only.
- No tests were present in the local file listing for this clone.

## Compatibility notes

- Narrow source-symbol indexer: less overlap than broad memory tools, but overlaps any other code graph tool on symbol indexing and MCP search authority.
- Compatibility-safe use would need clear database path/current-working-directory handling to avoid indexing one directory while serving another.
- Because it stores full file content in SQLite, privacy/state boundaries should be treated as local source-cache boundaries.

## Failure modes and limits

- Supports only `.ts` and `.js` files in inspected indexer.
- Database rebuild is destructive (`DELETE FROM nodes`, `DELETE FROM edges`) and not incremental.
- The graph is containment-only; no callers/callees/imports/inheritance/dependency edges.
- `search_nodes` lacks explicit argument validation and uses broad `LIKE` matching; large result sets are returned as pretty JSON without truncation.
- File content is stored only on file nodes, not symbol bodies; `get_node_details` for file nodes may emit full source content.

## Open questions

- Is this intended as a minimal prototype or will call/import graph logic be added?
- Should the database path be tied to target directory rather than current working directory?
- What MCP client configuration is expected beyond running `npm run mcp`?

## Next review tasks

- [ ] Run `npm run build` and a small JS/TS fixture index/query smoke test before any operational use.
- [ ] Add or inspect tests if they exist outside the shallow clone.
- [ ] Review generated DB size and output size behavior on a medium TypeScript repo.
- [ ] Treat as a lead/source-logic candidate only until benchmark-audit or reproduction evidence exists.
