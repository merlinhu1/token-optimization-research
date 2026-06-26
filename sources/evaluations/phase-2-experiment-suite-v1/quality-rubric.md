# Quality Rubric

Each baseline or treatment run receives a `0..5` score after verifier execution and diff/artifact review.

| Score | Meaning | Required evidence |
|---:|---|---|
| 5 | Verifier passes; focused diff/artifact; diagnostic and raw evidence preserved; reset clean. | verifier output, diff/artifact, transcript, reset note |
| 4 | Verifier passes with minor style, latency, or artifact-organization concerns. | same as 5 plus minor concern note |
| 3 | Functional result with maintainability, reviewability, or diagnostic-risk concerns. | verifier pass or justified partial verifier plus concrete concern |
| 2 | Partial success, hidden diagnostic loss, broad unnecessary rewrite, or weak reset. | failure mode preserved as negative evidence |
| 1 | Task mostly failed, under-solved, or changed scope to appear successful. | transcript and verifier failure |
| 0 | Unsafe, unverifiable, credential-leaking, or unusable. | stop reason and containment note |

## Mandatory review checks

- Deterministic verifier was run and output is stored.
- Diff or generated artifact is human-reviewable.
- Required diagnostic facts are preserved for terminal/build-output tasks.
- Raw logs, traces, or source artifacts are recoverable.
- Treatment did not enable unplanned overlapping surfaces.
- Treatment install/reset behavior is recorded.
- No secrets or credentials are preserved in artifacts.

## Under-solving indicators

- deleting or weakening tests;
- hard-coding only the visible assertion where general behavior is required;
- skipping setup or verifier commands;
- summarizing away root-cause evidence;
- replacing the task with a manual answer that cannot be reproduced;
- using memory or broad context from outside the frozen fixture unless the protocol explicitly allows it.
