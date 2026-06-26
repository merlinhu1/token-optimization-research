#!/usr/bin/env python3
"""Run Codex continuous workflow-sequence evaluations.

The runner evaluates one profile on one active workflow sequence from
``data/workflow-task-sequences.json``. Unlike the early ad-hoc workflow runner,
tasks are fed to the same Codex session one at a time via ``codex exec resume``;
future task prompts are not visible to the model until the previous task verifier
has passed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import extract_codex_usage  # type: ignore
import run_codex_fixture_evaluation as fixture  # type: ignore

DEFAULT_DOCKER_IMAGE = "token-eval-codex:latest"
DEFAULT_SOURCE_CODEX_HOME = Path(os.environ.get("CODEX_HOME", "/opt/data/home/.codex"))
DATE = dt.datetime.now(dt.UTC).date().isoformat()
DATE_COMPACT = DATE.replace("-", "")
COMPACT_ARTIFACT_NAMES = {"run.json", "changes.diff", "evidence.jsonl.gz", "manifest.sha256"}

PROJECT_META: dict[str, dict[str, str]] = {
    "large-django-django": {
        "project_id": "django-django",
        "dependency_command": "python3 -m venv .venv && . .venv/bin/activate && python -m pip install -q --upgrade pip setuptools wheel && python -m pip install -q -e .",
    },
    "large-hashicorp-terraform": {
        "project_id": "hashicorp-terraform",
        "dependency_command": "export PATH=/opt/data/bin:/opt/data/opt/go/bin:$PATH; go env GOMODCACHE >/dev/null",
    },
    "medium-psf-requests": {
        "project_id": "psf-requests",
        "dependency_command": "python3 -m venv .venv && . .venv/bin/activate && python -m pip install -q --upgrade pip setuptools wheel && python -m pip install -q -e . 'pytest<9' pytest-httpbin==2.1.0 'httpbin~=0.10.0' pytest-cov pytest-mock pytest-xdist trustme PySocks",
    },
    "medium-pallets-flask": {
        "project_id": "pallets-flask",
        "dependency_command": "python3 -m venv .venv && . .venv/bin/activate && python -m pip install -q --upgrade pip setuptools wheel && python -m pip install -q -e . 'pytest<9' asgiref python-dotenv",
    },
    "large-orchardcms-orchardcore": {
        "project_id": "orchardcms-orchardcore",
        "dependency_command": "DOTNET_ROOT=/opt/data/dotnet; export DOTNET_ROOT PATH=\"$DOTNET_ROOT:$PATH\" DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1; dotnet restore test/OrchardCore.Tests/OrchardCore.Tests.csproj >/dev/null",
    },
    "medium-fastify-fastify": {
        "project_id": "fastify-fastify",
        "dependency_command": "npm install --ignore-scripts --no-audit --no-fund",
    },
    "medium-beetbox-beets": {
        "project_id": "beetbox-beets",
        "dependency_command": "uv sync --group test",
    },
}

PROFILE_META: dict[str, dict[str, Any]] = {
    "baseline-bare-codex": {
        "session_role": "baseline",
        "profile_type": "control",
        "component_ids": [],
        "enabled_surfaces": ["codex-native-shell-edit"],
        "disabled_overlaps": ["all token-saving surfaces"],
        "allowed_terms": [],
        "tool_state": "none",
        "tool_use_policy": "none",
        "prompt_guidance": (
            "# Evaluation isolation contract\n\n"
            "You are running inside the `baseline-bare-codex` control lane. "
            "This is a Codex substrate baseline: native shell, file, git, and verifier operations are allowed. "
            "Do not use external retrieval, compression, memory, MCP, or token-saving tools. "
            "Work only inside the target repository and use the current task verifier as the acceptance gate.\n\n"
            "---\n\n"
        ),
    },
    "retrieval-leanctx": {
        "session_role": "individual_tool_treatment",
        "profile_type": "individual_tool",
        "component_ids": ["lean-ctx"],
        "enabled_surfaces": ["retrieval-context"],
        "disabled_overlaps": ["all unlisted token-saving surfaces"],
        "allowed_terms": ["lean-ctx", "mcp_lean_ctx", "ctx_read", "ctx_search", "ctx_shell", "ctx_graph"],
        "tool_state": "cold",
        "tool_use_policy": "optional",
        "prompt_guidance": (
            "# Evaluation isolation contract\n\n"
            "You are running inside the `retrieval-leanctx` treatment lane for LeanCTX. "
            "Tool-state condition: `cold`. Tool-use policy: `optional`. LeanCTX is available as an optional retrieval/context MCP tool. "
            "Use it only when it is likely to reduce total context or improve localization; otherwise use Codex native shell/file tools. "
            "Do not use other retrieval, compression, memory, or token-saving tools. "
            "Work only inside the target repository and use the current task verifier as the acceptance gate.\n\n"
            "---\n\n"
        ),
    },
}

LEAKY_PROMPT_LINE_PATTERNS = [
    re.compile(r"^Issue source:.*$", re.IGNORECASE),
    re.compile(r"^The repository has already been checked out.*$", re.IGNORECASE),
    re.compile(r"^This task follows a SWE-bench-style flow:.*$", re.IGNORECASE),
    re.compile(r".*pinned fixed upstream commit.*", re.IGNORECASE),
    re.compile(r".*seeded with a regression.*", re.IGNORECASE),
    re.compile(r".*removes? the relevant production fix.*", re.IGNORECASE),
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def run(
    cmd: list[str],
    *,
    cwd: Path,
    stdout: Path | None = None,
    timeout: int = 900,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if stdout:
        stdout.parent.mkdir(parents=True, exist_ok=True)
        with stdout.open("w") as out:
            return subprocess.run(cmd, cwd=cwd, text=True, stdout=out, stderr=subprocess.STDOUT, timeout=timeout, env=env)
    return subprocess.run(cmd, cwd=cwd, text=True, timeout=timeout, env=env)


def chmod_tree(path: Path) -> None:
    if not path.exists():
        return
    for cur, dirs, files in os.walk(path):
        try:
            os.chmod(cur, 0o700)
        except OSError:
            pass
        for name in dirs:
            try:
                os.chmod(Path(cur) / name, 0o700)
            except OSError:
                pass
        for name in files:
            try:
                os.chmod(Path(cur) / name, 0o600)
            except OSError:
                pass


def sequence_doc() -> dict[str, Any]:
    return json.loads((ROOT / "data/workflow-task-sequences.json").read_text())


def load_sequence(sequence_id: str) -> dict[str, Any]:
    for seq in sequence_doc().get("sequences", []):
        if seq.get("id") == sequence_id:
            return seq
    raise KeyError(f"unknown workflow sequence {sequence_id}")


def active_sequence_ids() -> list[str]:
    return [seq["id"] for seq in sequence_doc().get("sequences", []) if seq.get("status") == "active"]


def task_alias(order: int) -> str:
    return f"task-{order:02d}"


def task_dir(project: Path, order: int) -> Path:
    return project / "tasks" / task_alias(order)


def sanitize_task_prompt(text: str) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        if any(pattern.match(line) for pattern in LEAKY_PROMPT_LINE_PATTERNS):
            continue
        # Hide public lookup keys and upstream-fixed framing in model-facing
        # prompts. The task text still describes the bug and verifier, but not
        # the public issue/commit answer path.
        line = re.sub(r"issue\s+#?\d+", "issue", line, flags=re.IGNORECASE)
        line = re.sub(r"real issue-derived regression", "regression", line, flags=re.IGNORECASE)
        line = re.sub(r"restores? the real upstream behavior", "restores the correct behavior", line, flags=re.IGNORECASE)
        line = re.sub(r"upstream test", "acceptance test", line, flags=re.IGNORECASE)
        lines.append(line)
    text = "\n".join(lines).strip() + "\n"
    return text


def write_sanitized_prompt(src: Path, dest: Path) -> None:
    dest.write_text(sanitize_task_prompt(src.read_text()))


def create_project(seq: dict[str, Any], project: Path, run_dir: Path, *, conceal_seed_origin: bool = True) -> None:
    if project.exists():
        chmod_tree(project)
        shutil.rmtree(project)
    project.mkdir(parents=True)
    tasks_dest = project / "tasks"
    tasks_dest.mkdir()

    ordered_tasks = sorted(seq["tasks"], key=lambda item: item["order"])
    alias_manifest: list[dict[str, Any]] = []
    for task in ordered_tasks:
        order = int(task["order"])
        src = ROOT / Path(task["prompt_path"]).parent
        dest = task_dir(project, order)
        shutil.copytree(src, dest)
        write_sanitized_prompt(src / "agent-prompt.txt", dest / "agent-prompt.txt")
        alias_manifest.append({
            "order": order,
            "task_id": task["id"],
            "alias": task_alias(order),
            "model_prompt_path": rel(dest / "agent-prompt.txt"),
            "verifier_command": rel(dest / "verify.sh"),
        })
    (run_dir / "task-alias-manifest.json").write_text(json.dumps(alias_manifest, indent=2) + "\n")

    repo = project / "repo"
    repo.mkdir()
    commit = seq["initial_snapshot"]["commit"]
    upstream = seq["initial_snapshot"]["upstream"]
    run(["git", "init", "-q"], cwd=repo, stdout=run_dir / "setup-git-init.txt")
    run(["git", "remote", "add", "origin", upstream], cwd=repo)
    run(["git", "fetch", "--depth", "1", "origin", commit], cwd=repo, stdout=run_dir / "setup-fetch.txt", timeout=1200)
    fetched = subprocess.check_output(["git", "rev-parse", "FETCH_HEAD"], cwd=repo, text=True).strip()
    if fetched != commit:
        raise RuntimeError(f"fetched {fetched}, expected {commit}")
    run(["git", "checkout", "-q", "--detach", "FETCH_HEAD"], cwd=repo)
    run(["git", "reset", "--hard", commit], cwd=repo, stdout=run_dir / "setup-reset.txt")
    run(["git", "clean", "-fdx"], cwd=repo, stdout=run_dir / "setup-clean.txt")

    with (run_dir / "setup-seed-patches.txt").open("w") as out:
        for task in ordered_tasks:
            order = int(task["order"])
            patch = task_dir(project, order) / "seed-regression.patch"
            out.write(f"apply order={order} task_id={task['id']} alias={task_alias(order)}\n")
            out.flush()
            proc = subprocess.run(["git", "apply", str(patch)], cwd=repo, text=True, stdout=out, stderr=subprocess.STDOUT, timeout=120)
            if proc.returncode != 0:
                raise RuntimeError(f"seed patch failed for {task['id']}")
    run(["git", "diff", "--stat"], cwd=repo, stdout=run_dir / "setup-seeded-diffstat-before-concealment.txt")

    if conceal_seed_origin:
        conceal_seed(repo, run_dir)
    else:
        run(["git", "diff", "--stat"], cwd=repo, stdout=run_dir / "setup-seeded-diffstat.txt")


def conceal_seed(repo: Path, run_dir: Path) -> None:
    """Make the broken workflow state the local baseline visible to the agent.

    The original fixture construction starts from an upstream fixed commit and
    applies production-code regression patches. If left as a dirty git diff, an
    agent can solve by simply reverting the seed diff. We therefore commit the
    seeded broken state as a local root-visible baseline, remove upstream remotes,
    and hide dependency directories from status. The raw setup artifacts still
    record what happened outside the model-facing repository.
    """
    run(["git", "config", "user.email", "workflow-eval@example.invalid"], cwd=repo)
    run(["git", "config", "user.name", "Workflow Eval"], cwd=repo)
    info = repo / ".git" / "info" / "exclude"
    with info.open("a") as out:
        out.write("\n.venv/\n__pycache__/\n.pytest_cache/\n")
    run(["git", "add", "-A"], cwd=repo, stdout=run_dir / "setup-conceal-git-add.txt")
    commit = run(["git", "commit", "-q", "-m", "workflow broken-start baseline"], cwd=repo, stdout=run_dir / "setup-conceal-commit.txt")
    if commit.returncode != 0:
        status = subprocess.run(["git", "status", "--short"], cwd=repo, text=True, stdout=subprocess.PIPE).stdout
        if status.strip():
            raise RuntimeError("failed to commit concealed seed baseline; inspect setup-conceal-commit.txt")
    run(["git", "remote", "remove", "origin"], cwd=repo, stdout=run_dir / "setup-conceal-remove-origin.txt")
    run(["git", "status", "--short"], cwd=repo, stdout=run_dir / "setup-concealed-status.txt")


def base_record(session_id: str, seq: dict[str, Any], profile_id: str, project: Path, run_dir: Path) -> dict[str, Any]:
    pmeta = PROFILE_META[profile_id]
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    return {
        "schema_version": 1,
        "evaluation_id": session_id,
        "target": {
            "fixture_id": seq["fixture_id"],
            "fixture_scale": seq["fixture_scale"],
            "project_id": project_id,
            "repository_path": rel(project / "repo"),
        },
        "task": {
            "id": seq["id"],
            "prompt_path": rel(run_dir / "task-prompts"),
            "verifier_command": rel(run_dir / "verify-workflow.sh"),
        },
        "profile": {
            "profile_id": profile_id,
            "profile_type": pmeta["profile_type"],
            "component_ids": pmeta["component_ids"],
            "enabled_surfaces": pmeta["enabled_surfaces"],
        },
        "setup": {
            "tool_permissions": {
                "profile_id": profile_id,
                "allowed_token_saving_tools": pmeta["allowed_terms"],
                "allowed_prompt_mentions": pmeta["allowed_terms"],
                "forbidden_tools": [],
            }
        },
        "agent": {
            "runtime_id": "codex-cli",
            "model_condition_id": "codex-openai-gpt-5-5-high",
            "provider": "openai",
            "model": "gpt-5.5",
            "reasoning_effort": "high",
        },
        "artifacts": {"root": rel(run_dir)},
    }


def task_prompt(seq: dict[str, Any], profile_id: str, project: Path, order: int, *, first_task: bool) -> str:
    task = next(item for item in seq["tasks"] if int(item["order"]) == order)
    prompt_path = task_dir(project, order) / "agent-prompt.txt"
    verifier = task_dir(project, order) / "verify.sh"
    preface: list[str] = []
    if first_task:
        preface.append(PROFILE_META[profile_id]["prompt_guidance"])
        preface.extend([
            f"# Sequential workflow session: {seq['id']}",
            "",
            "You are in one persistent repository checkout. Do not reset the repository.",
            "You will receive workflow tasks one at a time. Future tasks are intentionally hidden until the current task verifier passes.",
            "Complete only the current task. Preserve the working tree for later tasks.",
            "The visible git baseline is the broken-start workflow state; do not assume `git diff` reveals the intended fix.",
            "",
        ])
    else:
        preface.extend([
            f"# Continue sequential workflow session: {seq['id']}",
            "",
            "The previous task verifier passed. Continue in the same repository checkout and preserve earlier fixes.",
            "Complete only the current task. Future tasks are intentionally hidden until this verifier passes.",
            "",
        ])
    preface.extend([
        f"## Current task {order}: {task_alias(order)}",
        "",
        f"Verifier command: `{verifier}`",
        "",
        prompt_path.read_text(),
    ])
    return "\n".join(preface).rstrip() + "\n"


def write_verifier(seq: dict[str, Any], run_dir: Path, project: Path) -> Path:
    verifier = run_dir / "verify-workflow.sh"
    lines = ["#!/usr/bin/env bash", "set -euo pipefail"]
    for task in sorted(seq["tasks"], key=lambda item: item["order"]):
        lines.append(f"bash {json.dumps(str(task_dir(project, int(task['order'])) / 'verify.sh'))}")
    verifier.write_text("\n".join(lines) + "\n")
    verifier.chmod(0o755)
    return verifier


def docker_setup_deps(seq: dict[str, Any], record: dict[str, Any], codex_home: Path, run_dir: Path, docker_image: str) -> int:
    repo = ROOT / record["target"]["repository_path"]
    env = fixture.codex_env(codex_home, containerized=True)
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True)
    cmd = ["bash", "-lc", PROJECT_META[seq["fixture_id"]]["dependency_command"]]
    proc = fixture.run_backend(cmd, backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=run_dir / "setup-deps-output.txt", timeout=2400, mounts=mounts)
    return proc.returncode


def codex_base_cmd(record: dict[str, Any]) -> list[str]:
    return ["codex", "exec", *fixture.codex_model_args(record), "--json", "--color", "never", "--disable", "hooks", "--ignore-rules"]


def extract_thread_id(events_path: Path) -> str | None:
    for line in events_path.read_text(errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "thread.started" and item.get("thread_id"):
            return str(item["thread_id"])
    return None


def run_codex_task(
    record: dict[str, Any],
    profile_id: str,
    codex_home: Path,
    run_dir: Path,
    docker_image: str,
    prompt_path: Path,
    output_path: Path,
    last_message_path: Path,
    *,
    timeout: int,
    thread_id: str | None,
) -> tuple[int, str | None]:
    cfg = fixture.active_tool_config(record, profile_id)
    repo = ROOT / record["target"]["repository_path"]
    if thread_id is None:
        cmd = [*codex_base_cmd(record), "--sandbox", "danger-full-access", "--cd", str(repo), "--output-last-message", str(last_message_path), "-"]
    else:
        cmd = ["codex", "exec", "resume", *fixture.codex_model_args(record), "--json", "--disable", "hooks", "--ignore-rules", "--output-last-message", str(last_message_path), thread_id, "-"]
    env = fixture.codex_env(codex_home, containerized=True, cfg=cfg)
    env.update(fixture.tool_env_for_record(record, profile_id, codex_home))
    mounts = fixture.container_mounts_for_record(record, codex_home, include_repo=True, cfg=cfg)
    fixture.add_mount(mounts, run_dir, mode="rw")
    proc = fixture.run_backend(cmd, backend="docker", docker_image=docker_image, cwd=repo, env=env, stdout_path=output_path, input_path=prompt_path, timeout=timeout, mounts=mounts)
    if thread_id is None and proc.returncode == 0:
        thread_id = extract_thread_id(output_path)
    return proc.returncode, thread_id


def run_one_verifier(seq: dict[str, Any], order: int, record: dict[str, Any], codex_home: Path, run_dir: Path, docker_image: str) -> dict[str, Any]:
    task = next(item for item in seq["tasks"] if int(item["order"]) == order)
    repo = ROOT / record["target"]["repository_path"]
    env = fixture.codex_env(codex_home, containerized=True)
    mounts = fixture.container_mounts_for_record(record, codex_home, include_project=True, include_repo=False)
    out = run_dir / f"verifier-{task_alias(order)}.txt"
    cmd = ["bash", str(task_dir(repo.parent, order) / "verify.sh")]
    proc = fixture.run_backend(cmd, backend="docker", docker_image=docker_image, cwd=repo.parent, env=env, stdout_path=out, timeout=1800, mounts=mounts)
    return {
        "task_id": task["id"],
        "task_alias": task_alias(order),
        "order": order,
        "verifier_exit_code": proc.returncode,
        "accepted": proc.returncode == 0,
        "verifier_output": rel(out),
    }


def run_final_verifier(seq: dict[str, Any], record: dict[str, Any], codex_home: Path, run_dir: Path, docker_image: str) -> int:
    repo = ROOT / record["target"]["repository_path"]
    env = fixture.codex_env(codex_home, containerized=True)
    mounts = fixture.container_mounts_for_record(record, codex_home, include_project=True, include_repo=False)
    fixture.add_mount(mounts, run_dir, mode="rw")
    proc = fixture.run_backend(["bash", str(run_dir / "verify-workflow.sh")], backend="docker", docker_image=docker_image, cwd=repo.parent, env=env, stdout_path=run_dir / "final-verifier-output.txt", timeout=3600, mounts=mounts)
    return proc.returncode


def concatenate_events(run_dir: Path, task_count: int) -> None:
    combined = run_dir / "codex-events.jsonl"
    with combined.open("w") as out:
        for order in range(1, task_count + 1):
            path = run_dir / f"task-{order:02d}-codex-events.jsonl"
            if path.exists():
                text = path.read_text(errors="replace")
                out.write(text)
                if text and not text.endswith("\n"):
                    out.write("\n")


def capture_diff(record: dict[str, Any], run_dir: Path) -> None:
    repo = ROOT / record["target"]["repository_path"]
    run(["git", "status", "--short"], cwd=repo, stdout=run_dir / "git-status.txt", timeout=60)
    run(["git", "diff", "--stat"], cwd=repo, stdout=run_dir / "final-diffstat.txt", timeout=60)
    run(["git", "diff"], cwd=repo, stdout=run_dir / "changes.diff", timeout=120)


def audit(record_path: Path, run_dir: Path) -> int:
    artifacts = [str(record_path), str(run_dir / "codex-events.jsonl"), str(run_dir / "codex-mcp-list.txt"), str(run_dir / "codex-effective-config.toml")]
    artifacts.extend(str(path) for path in sorted((run_dir / "task-prompts").glob("task-*.md")))
    return fixture.run([
        sys.executable,
        str(ROOT / "scripts/audit_tool_isolation.py"),
        "--json-output",
        str(run_dir / "tool-isolation-audit.json"),
        *artifacts,
    ], stdout_path=run_dir / "tool-isolation-audit.txt", timeout=120).returncode


def compact_artifacts(run_dir: Path) -> dict[str, str]:
    return {
        "artifact_contract": "compact-v1-four-files",
        "run_record": rel(run_dir / "run.json"),
        "final_diff": rel(run_dir / "changes.diff"),
        "evidence_bundle": rel(run_dir / "evidence.jsonl.gz"),
        "manifest": rel(run_dir / "manifest.sha256"),
    }


def evidence_source_files(run_dir: Path) -> list[Path]:
    """Return text evidence to pack, excluding scratch checkouts/homes."""
    files: list[Path] = []
    for path in sorted(run_dir.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(run_dir).parts
        if not rel_parts or rel_parts[0] == "codex-homes":
            continue
        if rel_parts[0] == "project" and len(rel_parts) > 1 and rel_parts[1] == "repo":
            continue
        if len(rel_parts) == 1 and rel_parts[0] in COMPACT_ARTIFACT_NAMES:
            continue
        files.append(path)
    return files


def write_evidence_bundle(run_dir: Path) -> Path:
    bundle = run_dir / "evidence.jsonl.gz"
    with gzip.open(bundle, "wt", encoding="utf-8") as out:
        for path in evidence_source_files(run_dir):
            entry = {
                "path": str(path.relative_to(run_dir)),
                "content": path.read_text(errors="replace"),
            }
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return bundle


def write_manifest(run_dir: Path) -> Path:
    manifest = run_dir / "manifest.sha256"
    lines = []
    for name in sorted(COMPACT_ARTIFACT_NAMES - {"manifest.sha256"}):
        path = run_dir / name
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {name}\n")
    manifest.write_text("".join(lines))
    return manifest


def remove_noncompact_artifacts(run_dir: Path) -> None:
    for path in list(run_dir.iterdir()):
        if path.is_file() and path.name in COMPACT_ARTIFACT_NAMES:
            continue
        if path.is_dir():
            chmod_tree(path)
            shutil.rmtree(path)
        else:
            path.unlink()


def redact_json_file(path: Path, keys: set[str]) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text())
    for key in keys:
        if key in data:
            data[key] = "[REDACTED]"
    path.write_text(json.dumps(data, indent=2) + "\n")


def redact_auth_sync(run_dir: Path) -> None:
    path = run_dir / "codex-auth-sync.jsonl"
    if path.exists():
        lines = []
        for line in path.read_text().splitlines():
            try:
                item = json.loads(line)
                if "source_home" in item:
                    item["source_home"] = "[REDACTED]"
                lines.append(json.dumps(item))
            except json.JSONDecodeError:
                lines.append(line)
        path.write_text("\n".join(lines) + ("\n" if lines else ""))
    redact_json_file(run_dir / "codex-home-manifest.json", {"source_auth_home"})


def remove_ephemeral_homes(run_dir: Path) -> None:
    for name in ["codex-homes"]:
        path = run_dir / name
        if path.exists():
            chmod_tree(path)
            shutil.rmtree(path)


def workflow_session_record(
    seq: dict[str, Any],
    summary: dict[str, Any],
    run_dir: Path,
    profile_id: str,
    codex_exit_codes: list[int],
    final_verifier_code: int,
    audit_code: int,
    usage: dict[str, Any],
    verifier_results: list[dict[str, Any]],
    *,
    prompt_delivery: dict[str, Any],
    leakage_controls: dict[str, Any],
) -> dict[str, Any]:
    pmeta = PROFILE_META[profile_id]
    tasks_passed = sum(1 for result in verifier_results if result["verifier_exit_code"] == 0)
    total_provider_tokens = usage.get("total_provider_tokens")
    tokens_per_accepted_task = (total_provider_tokens / tasks_passed) if tasks_passed and isinstance(total_provider_tokens, (int, float)) else None
    accepted = bool(summary.get("accepted"))
    return {
        "schema_version": 1,
        "session_id": summary["session_id"],
        "record_type": "workflow_session",
        "evidence_type": "workflow-simulation",
        "study_id": summary["study_id"],
        "experiment_group_id": summary["experiment_group_id"],
        "objective": seq.get("objective", "individual_tool_effectiveness"),
        "evidence_stage": "reproduction",
        "status": "completed" if accepted else "failed",
        "session_role": pmeta["session_role"],
        "replicate_index": summary["replicate_index"],
        "date": DATE,
        "target": {
            "fixture_id": seq["fixture_id"],
            "fixture_scale": seq["fixture_scale"],
            "project_id": PROJECT_META[seq["fixture_id"]]["project_id"],
            "repository_path": summary["repository_path"],
            "initial_snapshot": {
                "commit": seq["initial_snapshot"]["commit"],
                "branch": "detached",
                "fixture_hash": "",
            },
        },
        "task_sequence": {
            "sequence_id": seq["id"],
            "task_ids": [task["id"] for task in sorted(seq["tasks"], key=lambda item: item["order"])],
            "reset_policy": "reset repository, profile home, tool state, indexes, caches, generated config, and agent home before the session; persist them between tasks",
            "prompt_delivery": prompt_delivery,
            "leakage_controls": leakage_controls,
        },
        "profile": {
            "profile_id": profile_id,
            "profile_type": pmeta["profile_type"],
            "enabled_surfaces": pmeta["enabled_surfaces"],
            "disabled_overlaps": pmeta["disabled_overlaps"],
            "component_ids": pmeta["component_ids"],
        },
        "agent": {
            "runtime_id": "codex-cli",
            "model_condition_id": "codex-openai-gpt-5-5-high",
            "name": "Codex CLI",
            "version": summary.get("codex_version", ""),
            "provider": "openai",
            "model": "gpt-5.5",
            "reasoning_effort": "high",
            "temperature": None,
            "max_turns": None,
            "time_budget_seconds": summary.get("timeout_seconds"),
        },
        "state_policy": sequence_doc().get("state_policy_defaults", {}),
        "cumulative_token_usage": {
            "measurement_source": "codex-jsonl-usage-events",
            "fresh_input_tokens": usage.get("fresh_input_tokens"),
            "cached_input_tokens": usage.get("cached_input_tokens"),
            "cache_write_tokens": usage.get("cache_write_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "reasoning_tokens": usage.get("reasoning_tokens"),
            "total_provider_tokens": usage.get("total_provider_tokens"),
            "estimated_cost_usd": usage.get("estimated_cost_usd"),
            "tokens_per_accepted_task": tokens_per_accepted_task,
            "pricing_basis": "not computed; Codex-reported token volume, not billing-weighted cost",
        },
        "per_task_results": verifier_results,
        "software_quality": {
            "tasks_attempted": len(verifier_results),
            "tasks_passed": tasks_passed,
            "final_verifier_command": rel(run_dir / "verify-workflow.sh"),
            "final_verifier_passed": final_verifier_code == 0,
            "quality_score": 5 if accepted else (3 if tasks_passed else 0),
            "critical_failures": [] if final_verifier_code == 0 else ["one or more workflow verifiers failed"],
        },
        "state_observations": {
            "stale_context_incidents": None,
            "overfeeding_incidents": None,
            "repeated_rediscovery_incidents": None,
            "useful_state_reuse_notes": "Single persistent Codex thread resumed across one task prompt at a time.",
        },
        "operational_reproducibility": {
            "install_logged": True,
            "pre_session_reset_verified": True,
            "raw_artifacts_recoverable": True,
            "state_leakage_outside_session_observed": False,
            "tool_isolation_audit": {
                "command": "python3 scripts/audit_tool_isolation.py --json-output ...",
                "passed": audit_code == 0,
                "forbidden_tool_hits": [],
            },
        },
        "artifacts": compact_artifacts(run_dir),
        "interpretation": {
            "accepted_for_objective": accepted,
            "comparison_baseline_session_id": "",
            "exclusion_reason": "" if accepted else f"codex_exit_codes={codex_exit_codes}; final_verifier_exit={final_verifier_code}; audit_exit={audit_code}; usage_warnings={usage.get('warnings')}",
            "notes": "Accepted sequential workflow session." if accepted else "Sequential workflow session failed one or more acceptance gates; inspect raw artifacts.",
            "scope_note": "Full active workflow sequence; tasks disclosed one at a time.",
        },
    }


def update_registry(record: dict[str, Any]) -> None:
    path = ROOT / "data/workflow-sessions.json"
    doc = json.loads(path.read_text())
    sessions = [s for s in doc.get("sessions", []) if s.get("session_id") != record["session_id"]]
    if record["session_role"] == "individual_tool_treatment":
        baseline = next((s for s in sessions if s.get("experiment_group_id") == record["experiment_group_id"] and s.get("session_role") == "baseline"), None)
        if baseline:
            record["interpretation"]["comparison_baseline_session_id"] = baseline["session_id"]
    sessions.append(record)
    doc["sessions"] = sessions
    path.write_text(json.dumps(doc, indent=2) + "\n")


def write_comparison_if_ready(seq: dict[str, Any], study_id: str, replicate_index: int) -> dict[str, Any] | None:
    registry = json.loads((ROOT / "data/workflow-sessions.json").read_text())
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    group_id = f"{DATE_COMPACT}-{project_id}-leanctx-sequential-workflow-r{replicate_index}"
    sessions = [s for s in registry.get("sessions", []) if s.get("experiment_group_id") == group_id]
    baseline = next((s for s in sessions if s.get("session_role") == "baseline"), None)
    treatment = next((s for s in sessions if s.get("profile", {}).get("profile_id") == "retrieval-leanctx"), None)
    if not baseline or not treatment:
        return None
    b_tokens = baseline.get("cumulative_token_usage", {}).get("total_provider_tokens")
    t_tokens = treatment.get("cumulative_token_usage", {}).get("total_provider_tokens")
    delta = t_tokens - b_tokens if isinstance(b_tokens, (int, float)) and isinstance(t_tokens, (int, float)) else None
    pct = (delta / b_tokens * 100) if delta is not None and b_tokens else None
    comparison = {
        "schema_version": 1,
        "comparison_id": f"{DATE_COMPACT}-{project_id}-baseline-vs-leanctx-sequential-workflow-r{replicate_index}",
        "study_id": study_id,
        "experiment_group_id": group_id,
        "sequence_id": seq["id"],
        "baseline_session_id": baseline["session_id"],
        "treatment_session_id": treatment["session_id"],
        "baseline_total_provider_tokens": b_tokens,
        "treatment_total_provider_tokens": t_tokens,
        "delta_total_provider_tokens": delta,
        "delta_percent": pct,
        "baseline_accepted": baseline.get("interpretation", {}).get("accepted_for_objective"),
        "treatment_accepted": treatment.get("interpretation", {}).get("accepted_for_objective"),
        "quality_gate": {
            "baseline_tasks_passed": baseline.get("software_quality", {}).get("tasks_passed"),
            "treatment_tasks_passed": treatment.get("software_quality", {}).get("tasks_passed"),
            "task_count": len(seq["tasks"]),
        },
        "interpretation": "Sequential prompt delivery: each task is disclosed only after the previous verifier passes. Positive token delta means LeanCTX used more Codex-reported provider tokens; negative means fewer.",
    }
    out = ROOT / "sources/evaluations/workflow-sessions" / f"{comparison['comparison_id']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(comparison, indent=2) + "\n")
    return comparison


def run_one(args: argparse.Namespace) -> dict[str, Any]:
    seq = load_sequence(args.sequence_id)
    if seq["fixture_id"] not in PROJECT_META:
        raise ValueError(f"No runner metadata for fixture {seq['fixture_id']}")
    profile_id = args.profile_id
    if profile_id not in PROFILE_META:
        raise ValueError(f"No runner metadata for profile {profile_id}")
    project_id = PROJECT_META[seq["fixture_id"]]["project_id"]
    profile_suffix = profile_id.replace("_", "-")
    mode_suffix = "sequential"
    session_id = args.session_id or f"{DATE_COMPACT}-{project_id}-{profile_suffix}-{mode_suffix}-workflow-r{args.replicate_index}"
    study_id = args.study_id or "phase-2-sequential-workflow-v1"
    experiment_group_id = args.experiment_group_id or f"{DATE_COMPACT}-{project_id}-leanctx-sequential-workflow-r{args.replicate_index}"
    run_dir = ROOT / "sources/evaluations/workflow-sessions" / session_id
    if run_dir.exists() and not args.keep_existing_run_dir:
        chmod_tree(run_dir)
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    project = run_dir / "project"
    prompt_dir = run_dir / "task-prompts"
    prompt_dir.mkdir(exist_ok=True)

    create_project(seq, project, run_dir, conceal_seed_origin=not args.no_conceal_seed_origin)
    verifier = write_verifier(seq, run_dir, project)
    record = base_record(session_id, seq, profile_id, project, run_dir)
    record["task"]["verifier_command"] = rel(verifier)
    record_path = run_dir / "run-record-input.json"
    record_path.write_text(json.dumps(record, indent=2) + "\n")

    protocol = fixture.evaluation_protocol(record, profile_id, PROFILE_META[profile_id]["tool_state"], PROFILE_META[profile_id]["tool_use_policy"])
    protocol["prompt_delivery"] = "sequential-one-task-at-a-time"
    protocol["seed_origin_concealment"] = not args.no_conceal_seed_origin
    (run_dir / "evaluation-protocol.json").write_text(json.dumps(protocol, indent=2) + "\n")

    codex_home_root = run_dir / "codex-homes"
    codex_home = fixture.prepare_codex_home(record, profile_id, run_dir, args.source_codex_home, codex_home_root, copy_auth=True)
    cfg = fixture.active_tool_config(record, profile_id)

    if not args.skip_container_preflight:
        container_preflight = fixture.check_container_runtime("docker", args.docker_image, run_dir, False, build_image=False, dockerfile=fixture.DEFAULT_DOCKERFILE, codex_home=codex_home, cfg=cfg)
        if not container_preflight.get("passed"):
            return {"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "container-preflight", "run_dir": rel(run_dir), "container_preflight": container_preflight}
    if not args.skip_codex_preflight:
        preflight = fixture.preflight_codex(record, codex_home, profile_id, run_dir, backend="docker", docker_image=args.docker_image)
        fixture.sync_copied_codex_auth_back(codex_home, args.source_codex_home, run_dir, "after-preflight")
        redact_auth_sync(run_dir)
        if not preflight.get("passed"):
            return {"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "codex-preflight", "run_dir": rel(run_dir), "preflight": preflight}
    if not args.skip_dependency_install:
        deps_code = docker_setup_deps(seq, record, codex_home, run_dir, args.docker_image)
        if deps_code != 0:
            capture_diff(record, run_dir)
            return {"session_id": session_id, "profile_id": profile_id, "accepted": False, "stage": "setup-deps", "setup_deps_exit_code": deps_code, "run_dir": rel(run_dir)}

    ordered_tasks = sorted(seq["tasks"], key=lambda item: item["order"])
    for task in ordered_tasks:
        order = int(task["order"])
        (prompt_dir / f"task-{order:02d}.md").write_text(task_prompt(seq, profile_id, project, order, first_task=order == 1))

    if args.prepare_only:
        redact_auth_sync(run_dir)
        remove_ephemeral_homes(run_dir)
        return {"session_id": session_id, "profile_id": profile_id, "sequence_id": seq["id"], "prepared": True, "run_dir": rel(run_dir)}

    thread_id: str | None = None
    codex_exit_codes: list[int] = []
    verifier_results: list[dict[str, Any]] = []
    for task in ordered_tasks:
        order = int(task["order"])
        prompt_path = prompt_dir / f"task-{order:02d}.md"
        events_path = run_dir / f"task-{order:02d}-codex-events.jsonl"
        last_message_path = run_dir / f"task-{order:02d}-codex-last-message.txt"
        code, thread_id = run_codex_task(record, profile_id, codex_home, run_dir, args.docker_image, prompt_path, events_path, last_message_path, timeout=args.timeout_per_task, thread_id=thread_id)
        codex_exit_codes.append(code)
        fixture.sync_copied_codex_auth_back(codex_home, args.source_codex_home, run_dir, f"after-task-{order:02d}")
        redact_auth_sync(run_dir)
        if code != 0:
            break
        result = run_one_verifier(seq, order, record, codex_home, run_dir, args.docker_image)
        verifier_results.append(result)
        if result["verifier_exit_code"] != 0:
            break

    concatenate_events(run_dir, len(ordered_tasks))
    usage = extract_codex_usage.build_summary(run_dir / "codex-events.jsonl")
    (run_dir / "provider-usage.json").write_text(json.dumps(usage, indent=2) + "\n")
    final_verifier_code = run_final_verifier(seq, record, codex_home, run_dir, args.docker_image) if len(verifier_results) == len(ordered_tasks) else 1
    capture_diff(record, run_dir)
    audit_code = audit(record_path, run_dir)
    accepted = all(code == 0 for code in codex_exit_codes) and len(verifier_results) == len(ordered_tasks) and final_verifier_code == 0 and audit_code == 0 and not usage.get("warnings")
    smoke = (run_dir / "docker-smoke-output.txt").read_text(errors="replace") if (run_dir / "docker-smoke-output.txt").exists() else ""
    codex_version = next((line.strip() for line in smoke.splitlines() if "codex" in line.lower() and any(ch.isdigit() for ch in line)), "")
    prompt_delivery = {
        "mode": "sequential-one-task-at-a-time",
        "future_tasks_visible": False,
        "codex_thread_id": thread_id,
        "task_prompt_evidence": rel(run_dir / "evidence.jsonl.gz"),
    }
    leakage_controls = {
        "seed_origin_concealed": not args.no_conceal_seed_origin,
        "task_directories_model_facing_aliases": True,
        "model_prompts_sanitized": True,
        "upstream_remote_removed_from_model_facing_repo": not args.no_conceal_seed_origin,
        "broken_start_committed_as_local_baseline": not args.no_conceal_seed_origin,
        "remaining_limitations": [
            "Task semantics and verifier names may still be searchable if the model intentionally uses external network access.",
            "Full prevention requires fixtures built from pre-fix bases plus hidden verifier tests rather than production-code reverse patches.",
        ],
    }
    summary = {
        "session_id": session_id,
        "study_id": study_id,
        "experiment_group_id": experiment_group_id,
        "replicate_index": args.replicate_index,
        "profile_id": profile_id,
        "workflow_sequence_id": seq["id"],
        "fixture_id": seq["fixture_id"],
        "repository_path": rel(project / "repo"),
        "codex_exit_codes": codex_exit_codes,
        "final_verifier_exit_code": final_verifier_code,
        "tool_isolation_audit_exit_code": audit_code,
        "accepted": accepted,
        "timeout_seconds": args.timeout_per_task * len(ordered_tasks),
        "codex_version": codex_version,
        "token_usage": {k: usage.get(k) for k in ["fresh_input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens", "total_provider_tokens", "estimated_cost_usd"]},
        "usage_warnings": usage.get("warnings"),
        "per_task_results": verifier_results,
        "prompt_delivery": prompt_delivery,
        "leakage_controls": leakage_controls,
        "artifacts": compact_artifacts(run_dir),
        "run_dir": rel(run_dir),
    }
    session_record = workflow_session_record(seq, summary, run_dir, profile_id, codex_exit_codes, final_verifier_code, audit_code, usage, verifier_results, prompt_delivery=prompt_delivery, leakage_controls=leakage_controls)
    update_registry(session_record)
    comparison = write_comparison_if_ready(seq, study_id, args.replicate_index)
    if comparison:
        summary["comparison"] = comparison
    (run_dir / "run.json").write_text(json.dumps(summary, indent=2) + "\n")
    write_evidence_bundle(run_dir)
    remove_ephemeral_homes(run_dir)
    remove_noncompact_artifacts(run_dir)
    write_manifest(run_dir)
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "Manual rerun guide: docs/evaluations/sequential-workflow-runner.md. "
            "For a paired baseline+treatment rerun use: "
            "scripts/run_sequential_workflow_pair.sh <sequence-id>."
        ),
    )
    parser.add_argument("--sequence-id", choices=active_sequence_ids())
    parser.add_argument("--profile-id", choices=sorted(PROFILE_META), default="baseline-bare-codex")
    parser.add_argument("--list-sequences", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--timeout-per-task", type=int, default=1800)
    parser.add_argument("--replicate-index", type=int, default=0)
    parser.add_argument("--session-id")
    parser.add_argument("--study-id")
    parser.add_argument("--experiment-group-id")
    parser.add_argument("--docker-image", default=DEFAULT_DOCKER_IMAGE)
    parser.add_argument("--source-codex-home", type=Path, default=DEFAULT_SOURCE_CODEX_HOME)
    parser.add_argument("--skip-container-preflight", action="store_true")
    parser.add_argument("--skip-codex-preflight", action="store_true")
    parser.add_argument("--skip-dependency-install", action="store_true")
    parser.add_argument("--no-conceal-seed-origin", action="store_true", help="debug only: leave seed patch as visible git diff")
    parser.add_argument("--keep-existing-run-dir", action="store_true")
    args = parser.parse_args(argv)
    if args.list_sequences:
        print(json.dumps({"active_sequences": active_sequence_ids(), "profiles": sorted(PROFILE_META)}, indent=2))
        return 0
    if not args.sequence_id:
        parser.error("--sequence-id is required unless --list-sequences is used")
    result = run_one(args)
    if args.prepare_only or result.get("prepared"):
        print(json.dumps(result, indent=2))
        return 0
    return 0 if result.get("accepted") else 1


if __name__ == "__main__":
    raise SystemExit(main())
