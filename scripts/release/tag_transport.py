"""Fallback transport for pushing an exact local annotated Tag through GitHub Git Data API."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path


class TagTransportError(Exception):
    """The local Tag cannot be represented exactly by the GitHub API."""


def _api(endpoint: str, payload: dict, repo_root: Path) -> dict:
    result = subprocess.run(
        ["gh", "api", "-X", "POST", endpoint, "--input", "-"],
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        cwd=repo_root,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise TagTransportError(f"GitHub API Tag push failed: {result.stderr.decode(errors='replace').strip()}")
    try:
        response = json.loads(result.stdout)
    except ValueError as exc:
        raise TagTransportError("GitHub API returned an invalid Tag response") from exc
    if not isinstance(response, dict):
        raise TagTransportError("GitHub API returned an invalid Tag response")
    return response


def push_annotated_tag_by_api(repo_name: str, tag: str, repo_root: Path) -> None:
    """Create the same annotated Tag object remotely, then create its ref."""
    if not re.fullmatch(r"wt-media-(?:workspace|cloud|agent|desktop)", repo_name):
        raise TagTransportError(f"invalid release repository: {repo_name}")
    tag_ref = f"refs/tags/{tag}"
    raw = subprocess.run(
        ["git", "cat-file", "-p", tag_ref],
        cwd=repo_root,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    if "\n\n" not in raw:
        raise TagTransportError("local annotated Tag has no message")
    header_text, message = raw.split("\n\n", 1)
    headers = dict(line.split(" ", 1) for line in header_text.splitlines() if " " in line)
    if set(headers) != {"object", "type", "tag", "tagger"} or headers["type"] != "commit" or headers["tag"] != tag:
        raise TagTransportError("local annotated Tag has unsupported headers")
    tagger = re.fullmatch(r"(.+) <([^<>]+)> (\d+) ([+-])(\d{2})(\d{2})", headers["tagger"])
    if tagger is None:
        raise TagTransportError("local annotated Tag has an invalid tagger")
    name, email, epoch, sign, hours, minutes = tagger.groups()
    offset = timedelta(hours=int(hours), minutes=int(minutes))
    if sign == "-":
        offset = -offset
    date = datetime.fromtimestamp(int(epoch), timezone.utc).astimezone(timezone(offset)).isoformat(timespec="seconds")
    local_object = subprocess.run(
        ["git", "rev-parse", tag_ref], cwd=repo_root, capture_output=True, text=True, check=True,
    ).stdout.strip()
    payload = {
        "tag": tag,
        "message": message,
        "object": headers["object"],
        "type": "commit",
        "tagger": {"name": name, "email": email, "date": date},
    }
    prefix = f"repos/piqiu96/{repo_name}/git"
    created = _api(f"{prefix}/tags", payload, repo_root)
    if created.get("sha") != local_object:
        raise TagTransportError("GitHub API Tag object differs from the local annotated Tag")
    _api(f"{prefix}/refs", {"ref": tag_ref, "sha": local_object}, repo_root)
