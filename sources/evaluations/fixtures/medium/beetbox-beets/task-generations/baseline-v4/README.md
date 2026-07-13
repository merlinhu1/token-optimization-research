# Beets Baseline V4 task family

Active lifecycle-v0 successor for Beets. The prompts differ from Baseline V3 only by the generation label; their command blocks, seed states, exact mechanical edits, and focused model-visible acceptance remain identical. Each generation-local task verifier now derives the copied project root and uses `${WORKFLOW_REPO:-$PROJECT_DIR/repo}`, preserving an explicit override while preventing the V3 wrapper/environment failure without changing model workload complexity.

Provider-free qualification exercises the generated aggregate wrapper with no caller-supplied `WORKFLOW_REPO`. The first GPT-5.6 Sol/`high` Baseline V4 Beets pilot is retained under its immutable r0 identity and passed independent review with every required incident count equal to integer zero. Treatment protocol freezing is now eligible; the occupied pilot must never be rerun.
