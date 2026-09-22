#!/usr/bin/env python3
"""Read the agent-facing configuration files.

`config/repository-map.yaml` and `config/skills-distribution.yaml` are small,
hand-maintained files with a restricted shape. They are read with the standard
library only, because the validation scripts must run in a bare checkout where
PyYAML is not guaranteed to be installed.

The reader covers exactly the subset these files use: nested mappings of
scalars, block sequences, comments, and quoted or unquoted strings. It raises
`ConfigError` on anything else rather than guessing, because a misread here
would silently change which repositories receive generated skill copies.

The reader lives in its own module rather than inside `sync_skills.py` so that
the verification scripts do not have to import the tool they verify.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class ConfigError(Exception):
    """Raised when a configuration file uses a shape this reader cannot trust."""


def _scalar(text: str, path: Path, lineno: int) -> Any:
    value = text.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith(("\"", "'")):
        if len(value) < 2 or not value.endswith(value[0]):
            raise ConfigError(f"{path}:{lineno}: unterminated quoted string: {value}")
        return value[1:-1]
    if value.startswith(("[", "{")):
        raise ConfigError(
            f"{path}:{lineno}: inline collections are not supported, use a block list"
        )
    if value.endswith((":", "-")):
        raise ConfigError(f"{path}:{lineno}: unexpected value: {value}")
    return value


def _tokenize(path: Path) -> list[tuple[int, int, str]]:
    lines: list[tuple[int, int, str]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        leading = raw[: len(raw) - len(raw.lstrip())]
        if "\t" in leading:
            raise ConfigError(f"{path}:{lineno}: tabs are not allowed in indentation")
        lines.append((lineno, len(leading), raw.strip()))
    return lines


def _parse(
    lines: list[tuple[int, int, str]], position: int, path: Path
) -> tuple[Any, int]:
    """Parse one block starting at `position`; return the value and the next position."""
    if lines[position][2].startswith("- "):
        items: list[Any] = []
        indent = lines[position][1]
        while (
            position < len(lines)
            and lines[position][1] == indent
            and lines[position][2].startswith("- ")
        ):
            lineno, _, text = lines[position]
            items.append(_scalar(text[2:], path, lineno))
            position += 1
        return items, position

    mapping: dict[str, Any] = {}
    indent = lines[position][1]
    while position < len(lines):
        lineno, line_indent, text = lines[position]
        if line_indent < indent or text.startswith("- "):
            break
        if line_indent > indent:
            raise ConfigError(f"{path}:{lineno}: unexpected indentation")
        key, separator, rest = text.partition(":")
        if not separator:
            raise ConfigError(f"{path}:{lineno}: expected 'key: value', got: {text}")
        key = key.strip()
        if key in mapping:
            raise ConfigError(f"{path}:{lineno}: duplicate key: {key}")
        position += 1
        if rest.strip():
            mapping[key] = _scalar(rest, path, lineno)
        elif position < len(lines) and lines[position][1] > indent:
            mapping[key], position = _parse(lines, position, path)
        else:
            mapping[key] = None
    return mapping, position


def read_document(path: Path) -> dict[str, Any]:
    """Read a whole configuration file into plain Python values."""
    if not path.is_file():
        raise ConfigError(f"missing configuration file: {path}")
    lines = _tokenize(path)
    if not lines:
        raise ConfigError(f"{path}: file is empty")
    if lines[0][1] != 0:
        raise ConfigError(f"{path}:{lines[0][0]}: top-level keys must not be indented")
    document, position = _parse(lines, 0, path)
    if not isinstance(document, dict):
        raise ConfigError(f"{path}: top level must be a mapping")
    if position != len(lines):
        raise ConfigError(f"{path}:{lines[position][0]}: unexpected trailing content")
    return document


def read_section(path: Path, section: str) -> dict[str, dict[str, Any]]:
    """Read a section that maps names to settings, such as `targets`."""
    value = read_document(path).get(section)
    if value is None:
        raise ConfigError(f"{path}: missing section: {section}")
    if not isinstance(value, dict):
        raise ConfigError(f"{path}: section '{section}' must be a mapping")
    for name, settings in value.items():
        if not isinstance(settings, dict):
            raise ConfigError(
                f"{path}: entry '{name}' in section '{section}' must be a mapping"
            )
    return value


def read_sequence(path: Path, key: str) -> list[str]:
    """Read a top-level block sequence, such as `tools`."""
    value = read_document(path).get(key)
    if value is None:
        raise ConfigError(f"{path}: missing key: {key}")
    if not isinstance(value, list):
        raise ConfigError(f"{path}: key '{key}' must be a block sequence")
    return [str(item) for item in value]
