#!/usr/bin/env python3
"""Generate executable qualification evidence from a clean pinned checkout."""
from __future__ import annotations

import argparse
import atexit
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import validate_repository as validation
from scripts import run_codex_workflow_evaluation as runner


def call(cmd: list[str], cwd: Path, timeout: int = 300, env: dict[str, str] | None = None) -> int:
    try:
        return subprocess.run(cmd, cwd=cwd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=False, timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        return 124


def out(cmd: list[str], cwd: Path, timeout: int = 120) -> str:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True, timeout=timeout).stdout.strip()


def concealed_paths(sequence: dict) -> list[str]:
    return sorted({str(path) for task in sequence["tasks"] for path in task.get("model_concealed_paths", [])})


def expected_task_concealed_paths(task: dict) -> list[str]:
    expected = set()
    expected.update(str(path) for path in task.get("upstream_test_paths", []))
    expected.update(str(path) for path in task.get("compatibility_rebased_test_paths", []))
    return sorted(expected)


def omitted_expected_concealment(task: dict) -> list[str]:
    declared = {str(path) for path in task.get("model_concealed_paths", [])}
    return sorted(set(expected_task_concealed_paths(task)) - declared)


def remove_concealed(checkout: Path, sequence: dict) -> None:
    for path_text in concealed_paths(sequence):
        path = checkout / path_text
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def normalize_remote(url: str) -> str:
    url = url.removesuffix(".git")
    if url.startswith("git@github.com:"):
        return "https://github.com/" + url.split(":", 1)[1]
    return url


def strip_comments(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not line.lstrip().startswith(("#", "//", "/*", "*")))


def noncomment_changed_lines(text: str) -> int:
    total = 0
    for line in text.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        stripped = line[1:].strip()
        if not stripped or stripped.startswith(("//", "/*", "*")):
            continue
        total += 1
    return total


def patch_semantic_footprint(text: str) -> dict[str, int]:
    """Small, language-neutral lower bound on a patch's behavior-bearing delta."""
    changed = [line[1:].strip() for line in text.splitlines()
               if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]
    code = [line for line in changed if line and not line.startswith(("//", "/*", "*", "#"))]
    control = [line for line in code if line.startswith(("if ", "if(", "for ", "for(", "while ", "switch ", "return ", "throw ", "await "))]
    files = sum(1 for line in text.splitlines() if line.startswith("diff --git "))
    return {"files": files, "noncomment_lines": len(code), "control_lines": len(control)}


def qualification_environment(fixture_id: str, checkout: Path) -> dict[str, str]:
    """Build the non-login-shell environment required by a fixture."""
    env = os.environ.copy()
    for key, value in runner.PROJECT_META[fixture_id].get("dependency_environment", {}).items():
        env[key] = value.format(**env)
    env["WORKFLOW_REPO"] = str(checkout)
    return env


def write_qualification_atomically(output: Path, payload: dict) -> None:
    """Replace qualification evidence only after its complete JSON is durable."""
    fd, temporary_name = tempfile.mkstemp(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, output)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequence_id")
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    sequence_doc = json.loads((ROOT / "data/workflow-task-sequences.json").read_text())
    sequence = next(item for item in sequence_doc["sequences"] if item["id"] == args.sequence_id)
    source_checkout = args.checkout.resolve()
    expected_commit = sequence["initial_snapshot"]["commit"]
    expected_upstream = sequence["initial_snapshot"]["upstream"]
    observed_head = out(["git", "rev-parse", "HEAD"], source_checkout)
    observed_tree = out(["git", "rev-parse", f"{expected_commit}^{{tree}}"], source_checkout)
    observed_remotes = out(["git", "remote", "-v"], source_checkout).splitlines()
    remote_urls = {line.split()[1] for line in observed_remotes if line.split()}
    normalized_remotes = {normalize_remote(url) for url in remote_urls}
    if observed_head != expected_commit:
        raise SystemExit(f"checkout HEAD {observed_head} does not match sequence snapshot {expected_commit}")
    if normalize_remote(expected_upstream) not in normalized_remotes:
        raise SystemExit(f"checkout remotes do not include expected upstream {expected_upstream}")
    status = out(["git", "status", "--porcelain", "--untracked-files=all"], source_checkout)
    if status:
        raise SystemExit("prepared checkout must be clean, including untracked files")

    workspace_root = Path(tempfile.mkdtemp(prefix="workflow-qualification-"))
    atexit.register(shutil.rmtree, workspace_root, ignore_errors=True)
    checkout = workspace_root / "repo"
    shutil.copytree(source_checkout, checkout, symlinks=True, ignore=shutil.ignore_patterns(".git"))
    remove_concealed(checkout, sequence)
    subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
    subprocess.run(["git", "config", "user.email", "qualification@example.invalid"], cwd=checkout, check=True)
    subprocess.run(["git", "config", "user.name", "Workflow Qualification"], cwd=checkout, check=True)
    subprocess.run(["git", "add", "-A"], cwd=checkout, check=True)
    subprocess.run(["git", "commit", "-qm", "fixed qualification root"], cwd=checkout, check=True)
    workspace_head = out(["git", "rev-parse", "HEAD"], checkout)
    fixture_meta = runner.PROJECT_META[sequence["fixture_id"]]
    dependency_command = fixture_meta["dependency_command"]
    qualification_env = qualification_environment(sequence["fixture_id"], checkout)
    subprocess.run(["bash", "-c", dependency_command], cwd=checkout, env=qualification_env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=True, timeout=2400)
    ordered = sorted(sequence["tasks"], key=lambda item: item["order"])
    records = []
    boundaries = []
    seeded_fail = fixed_pass = transitions = True

    for index, task in enumerate(ordered):
        task_dir = (ROOT / task["prompt_path"]).parent
        patch = task_dir / "seed-regression.patch"
        verifier = task_dir / "verify.sh"
        files = [path for path in validation.patch_paths(patch) if validation.is_production_path(path)]
        task_concealed = sorted(str(path) for path in task.get("model_concealed_paths", []))
        expected_concealed = expected_task_concealed_paths(task)
        omissions = omitted_expected_concealment(task)
        seed_check = call(["git", "apply", "--check", str(patch)], checkout)
        seed_apply = call(["git", "apply", str(patch)], checkout) if seed_check == 0 else 1
        seeded_exit = call(["bash", str(verifier)], checkout, env=qualification_env) if seed_apply == 0 else 125
        restore_check = call(["git", "apply", "--check", "--reverse", str(patch)], checkout) if seed_apply == 0 else 125
        restore_apply = call(["git", "apply", "--reverse", str(patch)], checkout) if restore_check == 0 else 125
        prior_exits = {
            prior["id"]: call(["bash", str((ROOT / prior["verifier_command"]).resolve())], checkout, env=qualification_env)
            for prior in ordered[:index + 1]
        } if restore_apply == 0 else {}
        pending_checks = {
            pending["id"]: call(["git", "apply", "--check", str((ROOT / pending["prompt_path"]).parent / "seed-regression.patch")], checkout)
            for pending in ordered[index + 1:]
        } if restore_apply == 0 else {}
        seeded_fail &= seeded_exit != 0
        fixed_pass &= restore_apply == 0 and all(code == 0 for code in prior_exits.values())
        transitions &= seed_check == 0 and seed_apply == 0 and restore_check == 0 and restore_apply == 0 and all(code == 0 for code in pending_checks.values())
        boundaries.append({"task_id": task["id"], "seed_apply_check_exit": seed_check, "seed_apply_exit": seed_apply, "seeded_verifier_exit": seeded_exit, "repair_apply_check_exit": restore_check, "repair_apply_exit": restore_apply, "retained_verifier_exits": prior_exits, "pending_seed_apply_check_exits": pending_checks})
        records.append({
            "task_id": task["id"],
            "seed_patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
            "verifier_sha256": hashlib.sha256(verifier.read_bytes()).hexdigest(),
            "production_files": files,
            "production_file_count": len(files),
            "expected_model_concealed_paths": expected_concealed,
            "model_concealed_paths": task_concealed,
            "omitted_expected_model_concealed_paths": omissions,
            "declared_concealment_matches_expected": task_concealed == expected_concealed,
            "model_concealed_absent": all(not (checkout / path).exists() for path in task_concealed),
        })

    replay = sequence.get("alternative_repair_replay", {})
    alternative_repair_transition = False
    alternative_repair_noncanonical = False
    alternative_repair_semantic_delta = False
    alternative_repair_metrics: dict[str, int] = {}
    alternative_repair_source_sha256 = ""
    alternative_repair_patch_sha256 = ""
    if replay:
        repaired_order = int(replay["repaired_task_order"])
        next_order = int(replay["next_task_order"])
        if next_order != repaired_order + 1:
            raise SystemExit("alternative repair must preserve the next ordered seed; wraparound is not allowed")
        repaired_task = next(task for task in ordered if int(task["order"]) == repaired_order)
        next_task = next(task for task in ordered if int(task["order"]) == next_order)
        repaired_dir = (ROOT / repaired_task["prompt_path"]).parent
        next_patch = (ROOT / next_task["prompt_path"]).parent / "seed-regression.patch"
        replay_path = ROOT / replay["changes_diff"]
        source = replay_path.read_text()
        alternative_repair_source_sha256 = hashlib.sha256(replay_path.read_bytes()).hexdigest()
        marker = f"# --- task-{repaired_order:02d}-agent ---"
        section = (source.split(marker, 1)[1].split("# --- task-", 1)[0] if marker in source else source).strip() + "\n"
        alternative_repair_patch_sha256 = hashlib.sha256(section.encode()).hexdigest()
        with tempfile.NamedTemporaryFile("w", suffix=".patch", delete=False) as handle:
            handle.write(section)
            accepted_patch = Path(handle.name)
        try:
            seed = repaired_dir / "seed-regression.patch"
            if call(["git", "apply", str(seed)], checkout) == 0:
                canonical_restore = subprocess.run(["git", "diff", "--binary", "-R", workspace_head, "--"], cwd=checkout, text=True, capture_output=True, check=True).stdout
                repaired = call(["git", "apply", str(accepted_patch)], checkout) == 0
                verifier_passed = repaired and call(["bash", str(repaired_dir / "verify.sh")], checkout, env=qualification_env) == 0
                next_applies = verifier_passed and call(["git", "apply", "--check", str(next_patch)], checkout) == 0
                alternative_repair_transition = repaired and verifier_passed and next_applies
                text_noncanonical = hashlib.sha256(strip_comments(section).encode()).hexdigest() != hashlib.sha256(strip_comments(canonical_restore).encode()).hexdigest()
                alternative_repair_metrics = patch_semantic_footprint(section)
                canonical_metrics = patch_semantic_footprint(canonical_restore)
                # A spelling/operand shuffle is not an independent repair. Require a
                # changed control-flow footprint or a substantial behavior-bearing delta.
                alternative_repair_semantic_delta = alternative_repair_metrics["control_lines"] != canonical_metrics["control_lines"] or alternative_repair_metrics["files"] != canonical_metrics["files"] or abs(alternative_repair_metrics["noncomment_lines"] - canonical_metrics["noncomment_lines"]) >= 5
                alternative_repair_noncanonical = text_noncanonical and alternative_repair_semantic_delta
        finally:
            accepted_patch.unlink(missing_ok=True)
            subprocess.run(["git", "reset", "--hard", workspace_head], cwd=checkout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    cumulative = all(call(["bash", str((ROOT / task["verifier_command"]).resolve())], checkout, env=qualification_env) == 0 for task in ordered)
    unmerged = not out(["git", "diff", "--name-only", "--diff-filter=U"], checkout)
    hidden = all(not (checkout / path).exists() for path in concealed_paths(sequence))
    controller_hidden = (ROOT / ordered[0]["prompt_path"]).parent.parents[1] / "controller-hidden"
    payload = {
        "schema_version": 4,
        "controller_hidden_sha256": validation.task_directory_sha256(controller_hidden) if controller_hidden.is_dir() else None,
        "qualified_on": sequence["qualification_date"],
        "snapshot": expected_commit,
        "observed_source": {"head": observed_head, "tree": observed_tree, "remotes": observed_remotes, "expected_upstream": expected_upstream, "clean": True},
        "tool_versions": {"git": out(["git", "--version"], ROOT), "qualification_dependency_command": dependency_command},
        "ordered_task_ids": [task["id"] for task in ordered],
        "model_concealed_paths": concealed_paths(sequence),
        "tasks": records,
        "cumulative_boundaries": boundaries,
        "seeded_verifier_nonzero": seeded_fail,
        "fixed_verifier_zero": fixed_pass,
        "full_fixed_cumulative_verifier_zero": cumulative,
        "ordered_transition_applicability": transitions,
        "alternative_repair_transition_applicability": alternative_repair_transition,
        "alternative_repair_noncanonical": alternative_repair_noncanonical,
        "alternative_repair_semantic_delta": alternative_repair_semantic_delta,
        "alternative_repair_metrics": alternative_repair_metrics,
        "alternative_repair_source_sha256": alternative_repair_source_sha256,
        "alternative_repair_patch_sha256": alternative_repair_patch_sha256,
        "no_unmerged_paths": unmerged,
        "no_model_visible_acceptance_assets": hidden,
        "all_expected_model_concealment_declared": all(record["declared_concealment_matches_expected"] for record in records),
    }
    output = ROOT / sequence["qualification_path"]
    for record, task in zip(records, ordered):
        task_dir = (ROOT / task["prompt_path"]).parent
        record["agent_prompt_sha256"] = hashlib.sha256((task_dir / "agent-prompt.txt").read_bytes()).hexdigest()
        record["task_directory_sha256"] = validation.task_directory_sha256(task_dir)
    payload["fixture_id"] = sequence["fixture_id"]
    payload["sequence_id"] = sequence["id"]
    payload["alternative_repair_source_sha256"] = alternative_repair_source_sha256
    payload["task_binding"] = {"algorithm": "sha256(path\\0bytes\\0; lexical recursive task directory order)", "task_directories": {record["task_id"]: record["task_directory_sha256"] for record in records}}
    write_qualification_atomically(output, payload)
    required = ("seeded_verifier_nonzero", "fixed_verifier_zero", "full_fixed_cumulative_verifier_zero", "ordered_transition_applicability", "alternative_repair_transition_applicability", "alternative_repair_noncanonical", "no_unmerged_paths", "no_model_visible_acceptance_assets", "all_expected_model_concealment_declared")
    return 0 if all(payload[field] for field in required) else 1


if __name__ == "__main__":
    raise SystemExit(main())
