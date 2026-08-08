#!/usr/bin/env python3
"""Create a Codex local marketplace from a source-pinned plugin checkout."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--marketplace-root", type=Path, required=True)
    parser.add_argument("--marketplace-name", required=True)
    parser.add_argument("--plugin-name", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    actual_commit = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual_commit != args.expected_commit:
        raise SystemExit(
            f"source commit mismatch for {source}: expected {args.expected_commit}, got {actual_commit}"
        )
    plugin_manifest = source / ".codex-plugin" / "plugin.json"
    manifest = json.loads(plugin_manifest.read_text())
    if manifest.get("name") != args.plugin_name:
        raise SystemExit(
            f"plugin manifest name mismatch: expected {args.plugin_name}, got {manifest.get('name')!r}"
        )

    root = args.marketplace_root.resolve()
    if root.exists():
        shutil.rmtree(root)
    plugin_dest = root / "plugins" / args.plugin_name
    shutil.copytree(source, plugin_dest, ignore=shutil.ignore_patterns(".git"))
    marketplace_manifest = root / ".agents" / "plugins" / "marketplace.json"
    marketplace_manifest.parent.mkdir(parents=True, exist_ok=True)
    marketplace_manifest.write_text(
        json.dumps(
            {
                "name": args.marketplace_name,
                "plugins": [
                    {
                        "name": args.plugin_name,
                        "source": {
                            "source": "local",
                            "path": f"./plugins/{args.plugin_name}",
                        },
                        "policy": {
                            "installation": "AVAILABLE",
                            "authentication": "ON_INSTALL",
                        },
                    }
                ],
            },
            indent=2,
        )
        + "\n"
    )
    receipt = {
        "schema_version": 1,
        "provider_calls": 0,
        "source": str(source),
        "source_commit": actual_commit,
        "plugin_name": args.plugin_name,
        "plugin_version": manifest.get("version"),
        "marketplace_name": args.marketplace_name,
        "marketplace_root": str(root),
        "passed": True,
    }
    (root / "source-pin-receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
