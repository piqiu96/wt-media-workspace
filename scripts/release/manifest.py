"""Validate the product Release Manifest before building from component Tags."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

import yaml


TAG_RE = re.compile(r"^v\d+\.\d+\.\d+(?:-rc\.[1-9]\d*)?$")
TARGETS = {"cloud": "linux-amd64", "desktop": ["windows-x64", "macos-x64", "macos-arm64"]}


def validate_manifest(path: Path, tag: str) -> dict:
    if not TAG_RE.fullmatch(tag):
        raise ValueError(f"invalid product Tag: {tag}")
    if path.name != f"{tag}.yaml":
        raise ValueError("product Tag and Manifest filename differ")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Manifest schema_version must be 1")
    if data.get("product_tag") != tag:
        raise ValueError("product Tag and Manifest product_tag differ")
    channel = "rc" if "-rc." in tag else "stable"
    if data.get("channel") != channel:
        raise ValueError(f"Manifest channel must be {channel} for {tag}")
    environment = data.get("environment")
    if environment not in {"pre", "online"}:
        raise ValueError("Manifest environment must be pre or online")
    if not isinstance(data.get("network_smoke"), bool):
        raise ValueError("Manifest network_smoke must be a boolean")
    origin = data.get("cloud_origin")
    if not isinstance(origin, str):
        raise ValueError("Cloud origin must be an HTTPS URL")
    parsed = urlsplit(origin)
    if (
        parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
        or parsed.path not in ("", "/") or parsed.query or parsed.fragment or origin.endswith("/")
        or parsed.geturl() != origin
    ):
        raise ValueError("Cloud origin must be a credential-free HTTPS origin without path or query")
    try:
        parsed.port
    except ValueError as exc:
        raise ValueError("Cloud origin has an invalid port") from exc
    if parsed.hostname.endswith(".invalid") and data["network_smoke"]:
        raise ValueError("network_smoke cannot be true for an .invalid Cloud origin")
    components = data.get("components")
    if not isinstance(components, dict) or set(components) != {"cloud", "agent", "desktop"}:
        raise ValueError("Manifest components must name cloud, agent, desktop exactly")
    if any(not isinstance(value, str) or not TAG_RE.fullmatch(value) for value in components.values()):
        raise ValueError("each component must use an immutable version Tag")
    if data.get("targets") != TARGETS:
        raise ValueError("Manifest targets must be Linux amd64 and all three Desktop platforms")
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    try:
        data = validate_manifest(args.file, args.tag)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        parser.exit(1, f"release manifest invalid: {exc}\n")
    if args.github_output:
        lines = {
            "channel": data["channel"],
            "environment": data["environment"],
            "cloud_origin": data["cloud_origin"],
            "cloud_tag": data["components"]["cloud"],
            "agent_tag": data["components"]["agent"],
            "desktop_tag": data["components"]["desktop"],
            "network_smoke": str(data["network_smoke"]).lower(),
        }
        with args.github_output.open("a", encoding="utf-8") as output:
            for key, value in lines.items():
                output.write(f"{key}={value}\n")
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
