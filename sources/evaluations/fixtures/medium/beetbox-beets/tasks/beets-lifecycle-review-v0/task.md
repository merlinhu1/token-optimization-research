# Beets lifecycle task: review and correct ftintitle metadata hooks

## Classification

Code review followed by correction of acceptance-critical findings.

## Authentic source

The proposed patch is the production diff from Beets PR #6726 revision `1160d31c` against pinned base `8ddae794`. The fixed snapshot uses merged revision `9acb1ecf`. The controller checks behavior and design contracts, not canonical source identity.

## Review boundary

Review the supplied `review-change.patch` affecting only `beetsplug/ftintitle.py` and `beets/autotag/hooks.py`. Correct the checked-out implementation so automatic metadata hooks preserve collaboration data, artist-credit semantics, event behavior, command/import behavior, and the plugin's documented scope.
