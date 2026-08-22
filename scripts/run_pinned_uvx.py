#!/usr/bin/env python3
"""Pin Headroom's Serena uvx selector to the audited wheel."""
import os
import sys

wheel = os.environ.get("PINNED_SERENA_WHEEL")
if not wheel:
    raise SystemExit("PINNED_SERENA_WHEEL is required")
uv = "/opt/data/opt/uv/uv"
os.execv(uv, [uv, "tool", "run", *[wheel if arg == "serena-agent" else arg for arg in sys.argv[1:]]])
