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
import os
import shutil
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


NODE_BIN = Path("/opt/data/opt/node-v24.18.0-linux-x64/bin")


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
    if (runtime / "package" / "package.json").is_file():
        install_npm_package(artifact_path, runtime)


def install_npm_package(artifact_path: Path, runtime: Path) -> None:
    """Install an npm tarball the way npm would, into runtime/node_modules.

    Unpacking the tarball by hand is not enough. A published pack contains only the package's
    own files: no dependencies, and no launchers, since npm synthesizes node_modules/.bin from
    the manifest's bin entries at install time. A hand-rolled shim over an unpacked package
    therefore resolves as an executable and then dies on its first require() of a dependency
    that was never fetched. The tool configs already expect npm's layout -- every npm-sourced
    profile invokes runtime/node_modules/.bin/<name> -- so npm is what has to produce it.
    """
    shutil.rmtree(runtime / "package", ignore_errors=True)
    npm = NODE_BIN / "npm"
    if not npm.is_file():
        raise RuntimeError(f"npm is required to install {artifact_path.name} but is missing at {npm}")
    result = subprocess.run(
        [str(npm), "install", "--prefix", str(runtime), "--no-audit", "--no-fund", str(artifact_path)],
        capture_output=True,
        text=True,
        env={**os.environ, "PATH": f"{NODE_BIN}:{os.environ.get('PATH', '')}"},
    )
    if result.returncode != 0:
        raise RuntimeError(f"npm install failed for {artifact_path.name}: {result.stderr.strip()[-500:]}")


def ensure_gitlink_placeholders(destination: Path) -> list[str]:
    """Recreate the empty directories an uninitialized submodule is supposed to leave behind.

    These checkouts are shallow, single-commit, non-recursive fetches, so a submodule recorded
    as a gitlink is never populated -- and for LeanCTX one of them points at an AUR packaging
    repo over ssh that this environment cannot reach anyway. Git represents that state as an
    empty placeholder directory. When the placeholder goes missing, `git status` reports the
    gitlink as deleted, and the treatment-source integrity gate in the workflow controller
    refuses the run with "dirty treatment source artifact" for a checkout whose tracked file
    content is byte-for-byte correct.

    That is a false positive, and it blocked a paid LeanCTX launch until the directory was
    recreated by hand. Repairing it here keeps the fix at the cause: a pinned checkout is
    supposed to be reproducible, so this makes it match what a plain checkout produces instead
    of loosening the gate that noticed the difference. Returns the paths it repaired.
    """
    listing = subprocess.run(
        ["git", "-C", str(destination), "ls-files", "-s"],
        check=True, text=True, capture_output=True,
    ).stdout
    repaired: list[str] = []
    for line in listing.splitlines():
        meta, _, path = line.partition("\t")
        if not path or not meta.startswith("160000 "):
            continue
        placeholder = destination / path
        if not placeholder.exists():
            placeholder.mkdir(parents=True, exist_ok=True)
            repaired.append(path)
    return repaired


def fetch_source(name: str, commit: str, destination: Path) -> None:
    """Check the source out at the exact commit the guide sha was read from."""
    repo = f"https://github.com/{REPOS[name]}"
    if destination.exists():
        ensure_gitlink_placeholders(destination)
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(destination)], check=True)
    subprocess.run(["git", "-C", str(destination), "remote", "add", "origin", repo], check=True)
    subprocess.run(
        ["git", "-C", str(destination), "fetch", "-q", "--depth", "1", "origin", commit],
        check=True,
    )
    subprocess.run(["git", "-C", str(destination), "checkout", "-q", "--detach", "FETCH_HEAD"], check=True)
    ensure_gitlink_placeholders(destination)


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
            # The workflow controller refuses to launch against a dirty pinned checkout, so a
            # digest-only report can pass while a run is still blocked. Surface it here without
            # mutating anything; `--only <tool>` without --verify-only repairs placeholders.
            source = root / "source"
            if (source / ".git").exists():
                status = subprocess.run(
                    ["git", "-C", str(source), "status", "--porcelain", "--untracked-files=all"],
                    check=False, text=True, capture_output=True,
                ).stdout.strip()
                state = "ok" if not status else "DIRTY CHECKOUT"
                if status:
                    failures.append(f"{name}: source checkout dirty\n{status}")
                print(f"  {state:<15} {name:<14} {source.relative_to(fixture.BATCH_RELEASE_ROOT)}")
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
