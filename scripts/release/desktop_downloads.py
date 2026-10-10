#!/usr/bin/env python3
"""Write the public desktop download manifest for a stable product Tag."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

REPOSITORY = "piqiu96/wt-media-workspace"
STABLE_TAG = re.compile(r"v\d+\.\d+\.\d+")
PLATFORMS = {
    "windows-x64": "windows-x64-setup.exe",
    "macos-x64": "macos-x64.zip",
    "macos-arm64": "macos-arm64.zip",
}


class ReleaseDownloadError(Exception):
    """The manifest for this Tag cannot safely be published."""


def build_manifest_from_tag(tag: str) -> dict:
    if not STABLE_TAG.fullmatch(tag):
        raise ReleaseDownloadError("product Tag must be a stable vX.Y.Z release")
    downloads = {}
    for platform, suffix in PLATFORMS.items():
        name = f"WT-Media_{tag}_{suffix}"
        downloads[platform] = {
            "file_name": name,
            "url": f"https://github.com/{REPOSITORY}/releases/download/{tag}/{name}",
        }
    return {"schema_version": 1, "version": tag, "downloads": downloads}


def write_manifest(tag: str, output: Path) -> None:
    manifest = build_manifest_from_tag(tag)
    output = Path(output)
    if not output.parent.is_dir():
        raise ReleaseDownloadError(f"output directory does not exist: {output.parent}")
    encoded = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{output.name}.", suffix=".tmp", dir=output.parent, delete=False) as file:
            temporary = Path(file.name)
            file.write(encoded)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True, help="stable product Tag, for example v0.1.0")
    parser.add_argument("--output", required=True, type=Path, help="Cloud Web desktop-downloads.json target")
    args = parser.parse_args()
    try:
        write_manifest(args.tag, args.output)
    except (ReleaseDownloadError, OSError) as exc:
        print(f"desktop download manifest write failed: {exc}", file=sys.stderr)
        return 1
    print(f"desktop download manifest written: {args.output} ({args.tag})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
