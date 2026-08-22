#!/usr/bin/env python3
"""Rebuild the pinned treatment-release corpus from upstream, verified against its hashes.

``BATCH_RELEASES`` in ``run_codex_fixture_evaluation.py`` names, for every treatment tool, the
release artifact and official install guide a batch is pinned to, each with a sha256 and the
upstream commit the guide was read at. Until now nothing produced that tree: it was assembled by
hand, so a machine without it could not run a treatment and a corrupted copy could not be
detected. This fetches every artifact and guide from upstream and refuses any byte that does not
match the pinned digest, which makes the corpus reproducible rather than merely recorded.

Sources are tried in turn -- GitHub release asset, PyPI, npm -- and the digest decides which was
right, so no per-tool source table has to be maintained alongside the pins.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_codex_fixture_evaluation as fixture  # type: ignore

REPOS = {
    "headroom": "chopratejas/headroom",
    "tokenjuice": "vincentkoc/tokenjuice",
    "rtk": "rtk-ai/rtk",
    "snip": "edouard-claude/snip",
    "graphify": "safishamsi/graphify",
    "leanctx": "yvgude/lean-ctx",
    "cartog": "jrollin/cartog",
    "codescope": "onur-gokyildiz-bhi/codescope",
    "swarmvault": "swarmclawai/swarmvault",
    "serena": "oraios/serena",
    "sigmap": "manojmallick/sigmap",
    "token-savior": "Mibayy/token-savior",
    "ponytail": "DietrichGebert/ponytail",
    "caveman": "JuliusBrussee/caveman",
    "codegraph": "colbymchenry/codegraph",
    "jcodemunch": "jgravelle/jcodemunch-mcp",
    "repowise": "repowise-dev/repowise",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def get(url: str, timeout: int = 180) -> bytes | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return None


def release_tag(directory: str, version: str) -> list[str]:
    return [f"v{version}", version, directory]


def candidate_artifact_urls(name: str, directory: str, artifact: str) -> list[str]:
    """Every plausible upstream location; the pinned digest picks the correct one."""
    filename = Path(artifact).name
    version = directory.rsplit("-", 1)[-1]
    repo = REPOS[name]
    urls = [
        f"https://github.com/{repo}/releases/download/{tag}/{filename}"
        for tag in release_tag(directory, version)
    ]
    # Some pins are GitHub's generated source tarball rather than an uploaded asset.
    urls += [
        f"https://github.com/{repo}/archive/refs/tags/{tag}.tar.gz"
        for tag in release_tag(directory, version)
    ]
    stem = filename.split("-")[0].replace("_", "-")
    if filename.endswith(".whl"):
        package = filename.split("-")[0].replace("_", "-")
        urls.append(f"https://pypi.org/pypi/{package}/{version}/json")
    if filename.endswith(".tgz"):
        package = filename[: -len(f"-{version}.tgz")]
        urls.append(f"https://registry.npmjs.org/{package}/-/{filename}")
        # A scoped package is pinned under a flattened filename, and npm serves its tarball
        # under the bare name: swarmvaultai-cli-3.20.0.tgz is @swarmvaultai/cli's cli-3.20.0.tgz.
        if "-" in package:
            scope, _, bare = package.partition("-")
            urls.append(
                f"https://registry.npmjs.org/@{scope}%2f{bare}/-/{bare}-{version}.tgz"
            )
    return urls


def resolve_pypi(url: str, filename: str) -> bytes | None:
    payload = get(url)
    if not payload:
        return None
    try:
        document = json.loads(payload)
    except json.JSONDecodeError:
        return None
    for item in document.get("urls", []):
        if item.get("filename") == filename:
            return get(item["url"])
    return None


def fetch_artifact(name: str, directory: str, artifact: str, digest: str) -> bytes:
    filename = Path(artifact).name
    for url in candidate_artifact_urls(name, directory, artifact):
        payload = resolve_pypi(url, filename) if url.startswith("https://pypi.org") else get(url)
        if payload and sha256(payload) == digest:
            return payload
    raise LookupError(f"{name}: no upstream source produced the pinned artifact digest {digest}")


def materialize_runtime(artifact_path: Path, runtime: Path) -> None:
    """Unpack an archive artifact into runtime/, which is what the tool configs mount.

    Wheels are installed into a lane venv at run time rather than unpacked, so they have no
    runtime tree and are skipped. Extraction uses the data filter so a crafted archive cannot
    write outside its own directory.
    """
    if runtime.exists() or artifact_path.suffix == ".whl":
        return
    if not tarfile.is_tarfile(artifact_path):
        return
    runtime.mkdir(parents=True, exist_ok=True)
    with tarfile.open(artifact_path) as archive:
        archive.extractall(runtime, filter="data")
    install_npm_bin_shims(runtime)


def install_npm_bin_shims(runtime: Path) -> None:
    """Create the launchers npm would have installed for a packed tarball.

    An npm pack extracts to ``package/`` and carries its executables only as ``bin`` entries in
    package.json; nothing on disk is runnable. Lanes put ``runtime`` itself on PATH, so without
    these shims a profile whose install step shells out to its own CLI fails to resolve it.
    """
    manifest = runtime / "package" / "package.json"
    if not manifest.is_file():
        return
    try:
        bins = json.loads(manifest.read_text()).get("bin") or {}
    except json.JSONDecodeError:
        return
    if isinstance(bins, str):
        bins = {manifest.parent.name: bins}
    for name, relative in bins.items():
        target = runtime / "package" / relative
        if not target.is_file():
            continue
        shim = runtime / name
        shim.write_text(f'#!/bin/sh\nexec node "{target}" "$@"\n')
        shim.chmod(0o755)


def fetch_source(name: str, commit: str, destination: Path) -> None:
    """Check the source out at the exact commit the guide sha was read from."""
    repo = f"https://github.com/{REPOS[name]}"
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(destination)], check=True)
    subprocess.run(["git", "-C", str(destination), "remote", "add", "origin", repo], check=True)
    subprocess.run(
        ["git", "-C", str(destination), "fetch", "-q", "--depth", "1", "origin", commit],
        check=True,
    )
    subprocess.run(["git", "-C", str(destination), "checkout", "-q", "--detach", "FETCH_HEAD"], check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", help="fetch just these tools; repeat to select several")
    parser.add_argument("--verify-only", action="store_true", help="check what is present without downloading")
    args = parser.parse_args(argv)

    selected = {k: v for k, v in fixture.BATCH_RELEASES.items() if not args.only or k in args.only}
    failures: list[str] = []
    for name, (directory, artifact, artifact_sha, guide, guide_sha, commit) in sorted(selected.items()):
        root = fixture.BATCH_RELEASE_ROOT / directory
        artifact_path, guide_path = root / artifact, root / guide
        if args.verify_only:
            for path, expected in ((artifact_path, artifact_sha), (guide_path, guide_sha)):
                state = "missing" if not path.is_file() else (
                    "ok" if sha256(path.read_bytes()) == expected else "DIGEST MISMATCH"
                )
                if state != "ok":
                    failures.append(f"{name}: {path.relative_to(fixture.BATCH_RELEASE_ROOT)} {state}")
                print(f"  {state:<15} {name:<14} {path.relative_to(fixture.BATCH_RELEASE_ROOT)}")
            continue

        if not (artifact_path.is_file() and sha256(artifact_path.read_bytes()) == artifact_sha):
            try:
                payload = fetch_artifact(name, directory, artifact, artifact_sha)
            except LookupError as exc:
                # One unreachable tool must not stop the rest of the corpus rebuilding.
                failures.append(str(exc))
                continue
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_bytes(payload)
            print(f"  fetched artifact {name:<14} {artifact_path.name}")

        materialize_runtime(artifact_path, root / "runtime")
        try:
            fetch_source(name, commit, root / "source")
        except subprocess.CalledProcessError as exc:
            failures.append(f"{name}: source checkout at {commit[:12]} failed ({exc})")
            continue
        if not guide_path.is_file():
            failures.append(f"{name}: official guide absent at {guide}")
        elif sha256(guide_path.read_bytes()) != guide_sha:
            failures.append(f"{name}: official guide digest changed at {guide}; the pinned commit no longer matches")
        else:
            print(f"  verified guide   {name:<14} {guide}")

    if failures:
        print("\n".join(f"  FAIL {item}" for item in failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
