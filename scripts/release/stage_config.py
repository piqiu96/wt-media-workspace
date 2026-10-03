"""Stage a public Cloud origin in client release build inputs."""

from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path
from urllib.parse import urlsplit


SETTING = re.compile(r'^(?P<prefix>\s*)(?P<key>[a-z_]+)\s*=\s*"[^"]*"(?P<rest>\s*(?:#.*)?)$')
SECTION = re.compile(r"^\s*\[([^]]+)\]\s*$")


def _replace(path: Path, section: str, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    current = ""
    count = 0
    for index, line in enumerate(lines):
        match = SECTION.match(line.strip())
        if match:
            current = match.group(1)
            continue
        setting = SETTING.match(line.rstrip("\r\n"))
        if current == section and setting and setting.group("key") == key:
            newline = "\n" if line.endswith("\n") else ""
            lines[index] = f'{setting.group("prefix")}{key} = "{value}"{setting.group("rest")}{newline}'
            count += 1
    if count != 1:
        raise ValueError(f"{path}: expected one {section}.{key}, found {count}")
    path.write_text("".join(lines), encoding="utf-8")


def stage_config(desktop: Path, agent: Path, origin: str) -> None:
    parsed = urlsplit(origin)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.path or parsed.query or parsed.fragment or origin.endswith("/")
            or parsed.geturl() != origin):
        raise ValueError("Cloud origin must be a credential-free HTTPS origin")
    try:
        parsed.port
    except ValueError as exc:
        raise ValueError("Cloud origin has an invalid port") from exc
    # Validate every expected source key before changing either file.
    desktop_data = tomllib.loads(desktop.read_text(encoding="utf-8"))
    agent_data = tomllib.loads(agent.read_text(encoding="utf-8"))
    for data, path in ((desktop_data, desktop), (agent_data, agent)):
        if "base_url" not in data.get("cloud", {}):
            raise ValueError(f"{path}: missing cloud.base_url")
    csp = desktop_data.get("browser", {}).get("csp_connect_src")
    if not isinstance(csp, str):
        raise ValueError(f"{desktop}: missing browser.csp_connect_src")
    old_origin = desktop_data["cloud"]["base_url"]
    if old_origin not in csp.split():
        raise ValueError(f"{desktop}: CSP omits original Cloud origin")
    _replace(desktop, "cloud", "base_url", origin)
    _replace(desktop, "browser", "csp_connect_src", " ".join(origin if item == old_origin else item for item in csp.split()))
    _replace(agent, "cloud", "base_url", origin)
    staged_desktop = tomllib.loads(desktop.read_text(encoding="utf-8"))
    staged_agent = tomllib.loads(agent.read_text(encoding="utf-8"))
    if staged_desktop["cloud"]["base_url"] != origin or staged_agent["cloud"]["base_url"] != origin:
        raise ValueError("staged Cloud origins differ")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--desktop-toml", type=Path, required=True)
    parser.add_argument("--agent-toml", type=Path, required=True)
    parser.add_argument("--cloud-origin", required=True)
    args = parser.parse_args()
    try:
        stage_config(args.desktop_toml, args.agent_toml, args.cloud_origin)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        parser.exit(1, f"release config invalid: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
