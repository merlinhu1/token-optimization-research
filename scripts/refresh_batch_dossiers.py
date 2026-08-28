#!/usr/bin/env python3
"""Re-inspect every batch-pinned tool against the release its lanes actually install.

The dossier corpus was inspected between 2026-06-26 and 2026-07-01 by fetching each
repository's then-current GitHub HEAD. ``BATCH_RELEASES`` later pinned each tool to a
published release, and the lane runners rewrite their paths onto that release, so the
code that runs has not matched the code the dossiers describe since the batch landed.
That gap is what the 2026-08-22 review found five protocol drifts and one blocking
repowise defect inside.

This reads the pinned ``source/`` checkout in the release corpus rather than a fresh
network fetch. Upstream HEAD keeps moving; the checkout does not, so the artifact this
writes describes exactly the bytes a treatment lane installs and stays reproducible
after upstream advances again.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_codex_fixture_evaluation as fixture  # type: ignore

# Dossier file per batch release key. A tool with no dossier is not a treatment
# candidate and has nothing to refresh.
DOSSIERS = {
    "cartog": "jrollin-cartog.md",
    "caveman": "juliusbrussee-caveman.md",
    "codegraph": "colbymchenry-codegraph.md",
    "codescope": "onur-gokyildiz-bhi-codescope.md",
    "graphify": "safishamsi-graphify.md",
    "headroom": "chopratejas-headroom.md",
    "jcodemunch": "jgravelle-jcodemunch-mcp.md",
    "leanctx": "yvgude-lean-ctx.md",
    "ponytail": "dietrichgebert-ponytail.md",
    "repowise": "repowise-dev-repowise.md",
    "rtk": "rtk-ai-rtk.md",
    "serena": "oraios-serena.md",
    "sigmap": "manojmallick-sigmap.md",
    "snip": "edouard-claude-snip.md",
    "token-savior": "mibayy-token-savior.md",
    "tokenjuice": "vincentkoc-tokenjuice.md",
}

# Paths that decide how a tool integrates with a host agent. These are the ones a
# stale dossier can silently misdescribe into a broken install protocol.
INTEGRATION_HINTS = (
    "install", "init", "setup", "hook", "plugin", "skill", "mcp", "client",
    "agent", "codex", "claude", "opencode", "cursor", "config",
)
SOURCE_SUFFIXES = {".py", ".ts", ".js", ".tsx", ".jsx", ".rs", ".go", ".mjs", ".cjs"}
DOC_SUFFIXES = {".md", ".mdx", ".rst", ".txt"}
TEST_HINTS = ("test", "spec", "bench", "fixture")
CONFIG_SUFFIXES = {".toml", ".yaml", ".yml", ".json", ".jsonc", ".sh", ".ps1"}
# Captured output rather than code: matches integration hints on filename alone.
DATA_DIRS = ("/results/", "results/", "__snapshots__", "/fixtures/", "fixtures/",
             "/testdata/", "testdata/", "/golden/", "node_modules/")
SKIP_DIRS = {".git", "node_modules", "dist", "build", "target", "__pycache__", ".venv", "vendor"}


def sha256_prefix(data: bytes, length: int = 16) -> str:
    return hashlib.sha256(data).hexdigest()[:length]


def git(source: Path, *args: str) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(source), *args],
            capture_output=True, text=True, timeout=60, check=False,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def walk(source: Path) -> list[Path]:
    files: list[Path] = []
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(source).parts):
            continue
        files.append(path)
    return sorted(files)


def classify(rel: str) -> set[str]:
    lowered = rel.lower()
    kinds: set[str] = set()
    suffix = Path(rel).suffix
    if suffix in SOURCE_SUFFIXES:
        kinds.add("source")
    if suffix in DOC_SUFFIXES:
        kinds.add("documentation")
    if any(hint in lowered for hint in TEST_HINTS):
        kinds.add("test_or_benchmark")
    if any(hint in lowered for hint in INTEGRATION_HINTS):
        # A recorded benchmark result named after a model, or a test snapshot, matches
        # "claude"/"agent" on its filename alone and tells an install protocol nothing.
        # Integration means code that performs the integration, or a doc that specifies
        # one -- not captured output that happens to mention a host.
        noise = any(part in lowered for part in DATA_DIRS)
        if not noise and (suffix in SOURCE_SUFFIXES or suffix in CONFIG_SUFFIXES
                          or (suffix in DOC_SUFFIXES and "test" not in lowered)):
            kinds.add("integration")
    return kinds


CHANGELOG_CANDIDATES = ("CHANGELOG.md", "CHANGES.md", "docs/CHANGELOG.md", "HISTORY.md")
# Matches every heading shape in the corpus: "## [1.108.290] - 2026-08-21 - title",
# "# v1.7.0 (2026-08-09)", and rtk's "## [0.45.0](compare-url) (2026-08-07)".
RELEASE_HEADING = re.compile(
    r"^#{1,3}\s+.*?v?(\d+\.\d+\.\d+)\D.*?(\d{4}-\d{2}-\d{2})", re.MULTILINE
)
# A release that renamed a flag, moved a config path, or changed what an installer
# writes is one that can invalidate a protocol derived from the older reading.
INSTALL_RELEVANT = re.compile(
    r"\b(install\w*|init\b|setup|hooks?\b|mcp\b|clients?\b|skills?\b|plugins?\b|"
    r"codex|claude|opencode|cursor|config\w*|settings?\b|agents?\.md|registrat\w+|"
    r"deprecat\w+)",
    re.IGNORECASE,
)


def changelog_delta(source: Path, audited_on: str, version: str) -> dict[str, object]:
    """Which upstream releases landed between the dossier's reading and the pinned one.

    Git cannot answer this: the corpus checkouts are built from release tarballs, so
    the commit a dossier audited is not an ancestor of the pinned commit and the range
    is unresolvable. The shipped changelog can, and it is keyed on dates rather than
    commits, which is what the dossiers actually record. Release titles are the
    cheapest signal for whether an install-protocol assumption moved -- the risk a
    stale dossier carries.
    """
    if not audited_on:
        return {"available": False, "reason": "dossier records no inspection date"}
    path = next((source / name for name in CHANGELOG_CANDIDATES if (source / name).is_file()), None)
    if path is None:
        return {"available": False, "reason": "release ships no changelog"}

    text = path.read_text(encoding="utf-8", errors="replace")
    matches = list(RELEASE_HEADING.finditer(text))
    entries = []
    for index, match in enumerate(matches):
        line_end = text.find("\n", match.start())
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[line_end + 1:end]
        entries.append({
            "version": match.group(1),
            "date": match.group(2),
            # The full heading line: several projects put the release's theme after the
            # date, and that title is the part worth reading.
            "heading": text[match.start():line_end].lstrip("# ").strip(),
            # Match the curated title, not the body. Nearly every release body
            # mentions "config" or "client" somewhere; a title that names an install
            # surface is the author telling you the surface moved.
            "touches_integration": bool(
                INSTALL_RELEVANT.search(text[match.start():line_end])
            ),
        })
    since = [entry for entry in entries if entry["date"] > audited_on]
    relevant = [entry for entry in since if entry["touches_integration"]]
    return {
        "available": True,
        "source": str(path.relative_to(source)),
        "audited_on": audited_on,
        "pinned_version": version,
        "releases_since_audit": len(since),
        "install_relevant_releases": len(relevant),
        "newest": since[0] if since else None,
        "oldest_after_audit": since[-1] if since else None,
        # Releases whose title names an install surface. Only some projects write
        # descriptive titles; where they do, this is the author pointing at the
        # releases that can invalidate a protocol. Where they do not it is empty,
        # which means "no signal", not "nothing changed" -- hence recent_headings.
        "install_relevant_headings": [entry["heading"] for entry in relevant[:40]],
        "titles_are_descriptive": any(
            len(entry["heading"]) > 30 for entry in since[:10]
        ),
        "recent_headings": [entry["heading"] for entry in since[:12]],
    }


def inspect(name: str, release_dir: str, artifact: str, guide: str, commit: str) -> dict[str, object]:
    root = fixture.BATCH_RELEASE_ROOT / release_dir
    source = root / "source"
    files = walk(source)
    rels = [str(path.relative_to(source)) for path in files]

    buckets: dict[str, list[str]] = {
        "integration": [], "source": [], "test_or_benchmark": [], "documentation": [],
    }
    for rel in rels:
        for kind in classify(rel):
            buckets[kind].append(rel)

    # Representative implementation files: the integration entry points first, since
    # those are what an install protocol is derived from, then the largest sources.
    integration_sources = [
        rel for rel in buckets["integration"]
        if Path(rel).suffix in SOURCE_SUFFIXES and "test" not in rel.lower()
    ]
    by_size = sorted(
        (rel for rel in buckets["source"] if "test" not in rel.lower()),
        key=lambda rel: (source / rel).stat().st_size,
        reverse=True,
    )
    representative: list[dict[str, object]] = []
    for rel in list(dict.fromkeys(integration_sources[:12] + by_size[:8])):
        data = (source / rel).read_bytes()
        representative.append({
            "path": rel,
            "bytes": len(data),
            "sha256_prefix": sha256_prefix(data),
        })

    guide_path = root / guide
    artifact_path = root / artifact
    return {
        "tool": name,
        "release_directory": release_dir,
        "version": release_dir.rsplit("-", 1)[-1],
        "pinned_commit": commit,
        "checkout_head": git(source, "rev-parse", "HEAD"),
        "checkout_head_matches_pin": git(source, "rev-parse", "HEAD") == commit,
        "commit_date": git(source, "show", "-s", "--format=%cI", "HEAD"),
        "release_artifact": {
            "path": artifact,
            "exists": artifact_path.is_file(),
            "sha256_prefix": sha256_prefix(artifact_path.read_bytes()) if artifact_path.is_file() else None,
        },
        "official_install_guide": {
            "path": guide,
            "exists": guide_path.is_file(),
            "sha256_prefix": sha256_prefix(guide_path.read_bytes()) if guide_path.is_file() else None,
        },
        "file_counts": {
            "total": len(rels),
            **{kind: len(value) for kind, value in buckets.items()},
        },
        # Split rather than one list: an install protocol is written from the code
        # that performs the integration and the docs that specify it, and mixing
        # benchmark harnesses into either is what made the old listing unreadable.
        "integration_code_paths": sorted(
            rel for rel in buckets["integration"]
            if Path(rel).suffix in SOURCE_SUFFIXES
            and not any(hint in rel.lower() for hint in TEST_HINTS)
        )[:40],
        "install_guide_paths": sorted(
            rel for rel in buckets["integration"]
            if Path(rel).suffix in DOC_SUFFIXES
            and not any(hint in rel.lower() for hint in TEST_HINTS)
        )[:20],
        "integration_paths": sorted(buckets["integration"])[:60],
        "test_or_benchmark_paths": sorted(buckets["test_or_benchmark"])[:30],
        "representative_files": representative,
        "dossier": DOSSIERS.get(name),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", help="limit to these batch release keys")
    parser.add_argument("--out", default=None, help="output artifact path")
    parser.add_argument(
        "--dossier-pins", default=None,
        help="JSON map of tool -> {commit, date} as recorded by its dossier",
    )
    args = parser.parse_args(argv)

    pins: dict[str, str] = {}
    if args.dossier_pins:
        pins = json.loads(Path(args.dossier_pins).read_text())

    stamp = date.today().strftime("%Y-%m-%d")
    out = Path(args.out) if args.out else ROOT / f"sources/discovery/{stamp}-batch-pinned-dossier-refresh.json"

    selected = {
        key: value for key, value in fixture.BATCH_RELEASES.items()
        if key in DOSSIERS and (not args.only or key in args.only)
    }
    tools = []
    for name, (release_dir, artifact, _artifact_sha, guide, _guide_sha, commit) in sorted(selected.items()):
        source = fixture.BATCH_RELEASE_ROOT / release_dir / "source"
        if not source.is_dir():
            print(f"  SKIP  {name:<14} no source checkout at {source}")
            continue
        record = inspect(name, release_dir, artifact, guide, commit)
        record["previously_audited_commit"] = pins.get(name, {}).get("commit")
        record["previously_audited_on"] = pins.get(name, {}).get("date")
        record["upstream_changes_since_audit"] = changelog_delta(
            source, pins.get(name, {}).get("date", ""), record["version"]
        )
        tools.append(record)
        head_ok = "ok" if record["checkout_head_matches_pin"] else "HEAD MISMATCH"
        print(f"  {head_ok:<14} {name:<14} {record['version']:<11} {record['file_counts']['total']:>5} files")

    payload = {
        "schema_version": 1,
        "date": stamp,
        "purpose": (
            "Re-inspect every batch-pinned treatment tool against the release its lanes "
            "install, replacing dossier readings taken from GitHub HEAD between "
            "2026-06-26 and 2026-07-01."
        ),
        "basis": (
            "Pinned source/ checkouts in the release corpus, each verified to sit at the "
            "BATCH_RELEASES commit. Not a fresh network fetch: upstream HEAD moves, the "
            "pinned checkout does not."
        ),
        "evidence_stage": "source-logic",
        "tool_count": len(tools),
        "tools": tools,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {out.relative_to(ROOT)} ({len(tools)} tools)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
