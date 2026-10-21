"""Read the small CHG metadata contract; keep legacy records readable."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


CHANGE_ID_RE = re.compile(r"^CHG-\d{8}-\d{3}$")
REPO_RE = re.compile(r"^wt-media-(?:workspace|cloud|agent|desktop)$")
LEGACY_REPO_RE = re.compile(r"wt-media-(?:workspace|cloud|agent|desktop)")
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
REQUIRED = ("id", "parent", "status", "depends_on", "affected_repos", "risk")


@dataclass(frozen=True)
class ChangeMetadata:
    change_id: str
    title: str
    parent: str
    status: str
    depends_on: tuple[str, ...]
    affected_repos: tuple[str, ...]
    risk: str
    path: Path
    legacy: bool
    merge_commits: dict[str, str]
    dependency_merge_commits: dict[str, dict[str, str]]
    verify_scenarios: tuple[str, ...]


def _frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None, text
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing CHG frontmatter end") from exc
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"invalid CHG frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        if key in values:
            raise ValueError(f"duplicate CHG metadata key: {key}")
        values[key] = value.strip()
    return values, "\n".join(lines[end + 1 :])


def _json_value(values: dict[str, str], key: str, default: object) -> object:
    if key not in values:
        return default
    try:
        return json.loads(values[key])
    except json.JSONDecodeError as exc:
        raise ValueError(f"{key} must use a JSON-style YAML value: {exc.msg}") from exc


def _string_list(values: dict[str, str], key: str) -> tuple[str, ...]:
    result = _json_value(values, key, [])
    if not isinstance(result, list) or any(not isinstance(item, str) for item in result):
        raise ValueError(f"{key} must be a list of strings")
    if len(result) != len(set(result)):
        raise ValueError(f"{key} contains duplicates")
    return tuple(result)


def _commits(values: dict[str, str], key: str) -> dict[str, str]:
    result = _json_value(values, key, {})
    if not isinstance(result, dict) or any(
        not isinstance(repo, str) or not REPO_RE.fullmatch(repo)
        or not isinstance(sha, str) or not SHA_RE.fullmatch(sha)
        for repo, sha in result.items()
    ):
        raise ValueError(f"{key} must map repository names to commit SHA values")
    return result


def read_change(path: Path) -> ChangeMetadata:
    change_id = path.parent.name
    if not CHANGE_ID_RE.fullmatch(change_id):
        raise ValueError(f"invalid CHG directory id: {change_id}")
    text = path.read_text(encoding="utf-8")
    values, body = _frontmatter(text)
    title_match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else change_id
    title = re.sub(rf"^{re.escape(change_id)}\s*[:：]\s*", "", title).strip() or change_id

    if values is None:
        status_match = re.search(r"^- Status:\s*(\w+)", text, re.MULTILINE)
        parent_match = re.search(r"^- Milestone:\s*`([^`]+)`", text, re.MULTILINE)
        affected_match = re.search(r"^- Affected repositories:\s*(.*)$", text, re.MULTILINE)
        affected: list[str] = []
        if affected_match:
            affected.extend(LEGACY_REPO_RE.findall(affected_match.group(1)))
            for line in text[affected_match.end():].splitlines():
                if not line.startswith("  - "):
                    break
                affected.extend(LEGACY_REPO_RE.findall(line))
        return ChangeMetadata(
            change_id, title, parent_match.group(1) if parent_match else "none",
            status_match.group(1) if status_match else "UNKNOWN", (),
            tuple(dict.fromkeys(affected)), "M", path, True, {}, {}, (),
        )

    missing = [key for key in REQUIRED if not values.get(key)]
    if missing:
        raise ValueError("missing CHG metadata: " + ", ".join(missing))
    if values["id"] != change_id:
        raise ValueError(f"CHG id {values['id']} does not match directory {change_id}")
    if values["status"] not in {"DISCUSSION", "PLANNED", "IMPLEMENTING", "VERIFYING", "DONE", "SUPERSEDED"}:
        raise ValueError(f"invalid CHG status: {values['status']}")
    if values["risk"] not in {"L", "M", "H"}:
        raise ValueError(f"invalid CHG risk: {values['risk']}")
    depends = _string_list(values, "depends_on")
    if any(not CHANGE_ID_RE.fullmatch(item) or item == change_id for item in depends):
        raise ValueError("depends_on contains an invalid or self CHG id")
    affected = _string_list(values, "affected_repos")
    if not affected or any(not REPO_RE.fullmatch(repo) for repo in affected):
        raise ValueError("affected_repos must name at least one known repository")
    if not re.search(r"^## Change\s*$", body, re.MULTILINE) or not re.search(r"^## Done When\s*$", body, re.MULTILINE):
        raise ValueError("new CHG must contain ## Change and ## Done When")
    merges = _commits(values, "merge_commits")
    dependency_merges = _json_value(values, "dependency_merge_commits", {})
    if not isinstance(dependency_merges, dict):
        raise ValueError("dependency_merge_commits must map CHG IDs to repository commits")
    parsed_dependencies: dict[str, dict[str, str]] = {}
    for dependency, commits in dependency_merges.items():
        if dependency not in depends or not isinstance(commits, dict):
            raise ValueError("dependency_merge_commits must refer to depends_on entries")
        parsed_dependencies[dependency] = _commits({"commits": json.dumps(commits)}, "commits")
    verify_scenarios = _string_list(values, "verify_scenarios")
    if any(scenario not in {"fast", "repo", "integration", "e2e", "real"} for scenario in verify_scenarios):
        raise ValueError("verify_scenarios contains an unknown scenario")
    return ChangeMetadata(
        change_id, title, values["parent"], values["status"], depends, affected,
        values["risk"], path, False, merges, parsed_dependencies, verify_scenarios,
    )
