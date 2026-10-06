#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Validate and manually push one product Tag to trigger release.yml."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.release.manifest import validate_manifest  # noqa: E402


class ReleaseError(Exception):
    """A release preflight or Tag submission failed."""


def _command(args: list[str], repo_root: Path, *, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=repo_root, capture_output=True, text=True, check=False)
    if result.returncode != 0 and not allow_failure:
        raise ReleaseError(f"{args[0]} command failed ({result.returncode}): {result.stderr.strip()}")
    return result


def _git(repo_root: Path, *args: str, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    return _command(["git", "-c", "http.version=HTTP/1.1", *args], repo_root, allow_failure=allow_failure)


def _github_ref(repo_root: Path, ref: str) -> str | None:
    result = _command(
        ["gh", "api", f"repos/piqiu96/wt-media-workspace/git/ref/{ref}", "--jq", ".object.sha"],
        repo_root,
        allow_failure=True,
    )
    if result.returncode == 0:
        sha = result.stdout.strip()
        if re.fullmatch(r"[0-9a-f]{40}", sha):
            return sha
        raise ReleaseError(f"GitHub returned an invalid object SHA for {ref}")
    if "HTTP 404" in result.stderr:
        return None
    raise ReleaseError(f"could not inspect GitHub ref {ref}: {result.stderr.strip()}")


def submit_tag(tag: str, repo_root: Path, *, push: bool) -> str:
    """Check fixed release inputs, then optionally create and push the product Tag."""
    repo_root = repo_root.resolve()
    manifest = repo_root / "releases" / "manifests" / f"{tag}.yaml"
    data = validate_manifest(manifest, tag)
    tracked_changes = _git(repo_root, "status", "--porcelain", "--untracked-files=no").stdout
    if tracked_changes:
        raise ReleaseError("workspace has uncommitted tracked changes")
    _git(repo_root, "ls-files", "--error-unmatch", "--", str(manifest.relative_to(repo_root)))

    head = _git(repo_root, "rev-parse", "HEAD").stdout.strip()
    branch = _git(repo_root, "symbolic-ref", "--quiet", "--short", "HEAD").stdout.strip()
    remote_branch = _github_ref(repo_root, f"heads/{branch}")
    if remote_branch != head:
        raise ReleaseError(f"push the workspace branch {branch} before submitting the product Tag")

    local_tag_exists = _git(repo_root, "show-ref", "--verify", "--quiet", f"refs/tags/{tag}", allow_failure=True).returncode == 0
    if local_tag_exists:
        local_tag_commit = _git(repo_root, "rev-parse", f"refs/tags/{tag}^{{}}").stdout.strip()
        if local_tag_commit != head:
            raise ReleaseError(f"product Tag {tag} already exists locally at a different commit")
    if _github_ref(repo_root, f"tags/{tag}") is not None:
        raise ReleaseError(f"product Tag {tag} already exists on origin")

    for component, component_tag in data["components"].items():
        result = _command(
            ["gh", "api", f"repos/piqiu96/wt-media-{component}/git/ref/tags/{component_tag}", "--silent"],
            repo_root,
            allow_failure=True,
        )
        if result.returncode != 0:
            raise ReleaseError(f"{component} component Tag {component_tag} is absent or inaccessible on GitHub")

    if not push:
        return f"validated {tag} at {head}; use --push to submit the Tag and trigger release.yml"

    if not local_tag_exists:
        _git(repo_root, "tag", "-a", tag, "-m", f"WT Media {tag}")
    local_tag_object = _git(repo_root, "rev-parse", f"refs/tags/{tag}").stdout.strip()
    push_result = _git(repo_root, "push", "origin", f"refs/tags/{tag}", allow_failure=True)
    remote_tag_object = _github_ref(repo_root, f"tags/{tag}")
    if remote_tag_object != local_tag_object:
        if push_result.returncode != 0:
            raise ReleaseError(f"product Tag push failed: {push_result.stderr.strip()}")
        raise ReleaseError(f"pushed product Tag {tag}, but remote Tag object read-back differs")
    return f"pushed {tag} at {head}; GitHub Tag push triggers release.yml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="new immutable product Tag, for example v0.1.0-rc.14")
    parser.add_argument("--push", action="store_true", help="create and push the Tag after preflight")
    args = parser.parse_args()
    try:
        print(submit_tag(args.tag, ROOT, push=args.push))
    except (ReleaseError, OSError, ValueError, yaml.YAMLError) as exc:
        print(f"product Tag submission failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
