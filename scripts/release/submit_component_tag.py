#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Preflight or push an immutable component Tag for an explicit source commit."""

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

from scripts.release.tag_transport import TagTransportError, push_annotated_tag_by_api  # noqa: E402

COMPONENTS = {"cloud", "agent", "desktop"}
TAG_RE = re.compile(r"v\d+\.\d+\.\d+(?:-rc\.[1-9]\d*)?")
SHA_RE = re.compile(r"[0-9a-f]{40}")


class ComponentTagError(Exception):
    """Component Tag input or remote state is unsafe to publish."""


def _command(args: list[str], cwd: Path, *, allow_failure: bool = False, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if allow_failure:
            return subprocess.CompletedProcess(args, 124, "", f"timed out after {timeout}s")
        raise ComponentTagError(f"{args[0]} command timed out after {timeout}s") from exc
    if result.returncode != 0 and not allow_failure:
        raise ComponentTagError(f"{args[0]} command failed ({result.returncode}): {result.stderr.strip()}")
    return result


def _git(repo_root: Path, *args: str, allow_failure: bool = False, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    return _command(["git", "-c", "http.version=HTTP/1.1", *args], repo_root, allow_failure=allow_failure, timeout=timeout)


def _remote_tag(component: str, tag: str, repo_root: Path) -> str | None:
    result = _command(
        ["gh", "api", f"repos/piqiu96/wt-media-{component}/git/ref/tags/{tag}", "--jq", ".object.sha"],
        repo_root,
        allow_failure=True,
    )
    if result.returncode == 0 and SHA_RE.fullmatch(result.stdout.strip()):
        return result.stdout.strip()
    if "HTTP 404" in result.stderr:
        return None
    raise ComponentTagError(f"cannot inspect remote component Tag: {result.stderr.strip()}")


def submit_component_tag(component: str, tag: str, commit: str, repo_root: Path, *, push: bool) -> str:
    if component not in COMPONENTS or not TAG_RE.fullmatch(tag) or not SHA_RE.fullmatch(commit):
        raise ComponentTagError("component, version Tag, or full commit SHA is invalid")
    repo_root = repo_root.resolve()
    local_commit = _git(repo_root, "cat-file", "-t", commit, allow_failure=True)
    if local_commit.returncode != 0 or local_commit.stdout.strip() != "commit":
        raise ComponentTagError(f"source commit {commit} is absent locally")
    remote_commit = _command(
        ["gh", "api", f"repos/piqiu96/wt-media-{component}/git/commits/{commit}", "--silent"],
        repo_root,
        allow_failure=True,
    )
    if remote_commit.returncode != 0:
        raise ComponentTagError(f"source commit {commit} is not present on GitHub; push its branch first")

    local_tag_exists = _git(repo_root, "show-ref", "--verify", "--quiet", f"refs/tags/{tag}", allow_failure=True).returncode == 0
    if local_tag_exists:
        if _git(repo_root, "cat-file", "-t", f"refs/tags/{tag}").stdout.strip() != "tag":
            raise ComponentTagError(f"local {tag} is not an annotated Tag")
        if _git(repo_root, "rev-parse", f"refs/tags/{tag}^{{}}").stdout.strip() != commit:
            raise ComponentTagError(f"local {tag} points to a different commit")
    remote_tag = _remote_tag(component, tag, repo_root)
    if remote_tag is not None:
        if local_tag_exists and remote_tag == _git(repo_root, "rev-parse", f"refs/tags/{tag}").stdout.strip():
            return f"component {component} Tag {tag} is already published at {commit}"
        raise ComponentTagError(f"component Tag {tag} already exists on GitHub with a different Tag object")

    if not push:
        return f"validated {component} {tag} at {commit}; use --push to publish the component Tag"

    if not local_tag_exists:
        _git(repo_root, "tag", "-a", tag, commit, "-m", f"WT Media {component} {tag}")
    local_tag_object = _git(repo_root, "rev-parse", f"refs/tags/{tag}").stdout.strip()
    push_result = _git(repo_root, "push", "origin", f"refs/tags/{tag}", allow_failure=True, timeout=45)
    remote_tag = _remote_tag(component, tag, repo_root)
    if remote_tag is None and push_result.returncode != 0:
        try:
            push_annotated_tag_by_api(f"wt-media-{component}", tag, repo_root)
        except TagTransportError as exc:
            if _remote_tag(component, tag, repo_root) != local_tag_object:
                raise ComponentTagError(f"component Tag push failed: {exc}") from exc
        remote_tag = _remote_tag(component, tag, repo_root)
    if remote_tag != local_tag_object:
        raise ComponentTagError(f"component Tag push failed or remote read-back differs: {push_result.stderr.strip()}")
    return f"pushed {component} {tag} at {commit}"


def component_repo(component: str) -> Path:
    if component not in COMPONENTS:
        raise ComponentTagError(f"unknown component: {component}")
    mapping = yaml.safe_load((ROOT / "config" / "repository-map.yaml").read_text(encoding="utf-8"))
    return (ROOT / mapping["repositories"][component]["path"]).resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("component", choices=sorted(COMPONENTS))
    parser.add_argument("tag", help="new immutable component Tag")
    parser.add_argument("commit", help="full 40-character source commit SHA")
    parser.add_argument("--push", action="store_true", help="create and push the annotated component Tag")
    args = parser.parse_args()
    try:
        print(submit_component_tag(args.component, args.tag, args.commit, component_repo(args.component), push=args.push))
    except (ComponentTagError, OSError, KeyError, yaml.YAMLError) as exc:
        print(f"component Tag submission failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
