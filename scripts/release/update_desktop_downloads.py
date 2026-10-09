#!/usr/bin/env python3
"""Write the public desktop download manifest from one published product Release."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

REPOSITORY = "piqiu96/wt-media-workspace"
STABLE_TAG = re.compile(r"v\d+\.\d+\.\d+")
PLATFORMS = {
    "windows-x64": "windows-x64-setup.exe",
    "macos-x64": "macos-x64.zip",
    "macos-arm64": "macos-arm64.zip",
}


class ReleaseDownloadError(Exception):
    """GitHub data cannot safely be published as desktop download links."""


def build_manifest(tag: str, release: dict) -> dict:
    if not STABLE_TAG.fullmatch(tag):
        raise ReleaseDownloadError("product Tag must be a stable vX.Y.Z release")
    if not isinstance(release, dict) or release.get("tag_name") != tag or release.get("draft") is not False or release.get("prerelease") is not False:
        raise ReleaseDownloadError("Release is absent, draft, prerelease, or belongs to another Tag")
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ReleaseDownloadError("Release assets are invalid")

    downloads = {}
    for platform, suffix in PLATFORMS.items():
        name = f"WT-Media_{tag}_{suffix}"
        matches = [asset for asset in assets if isinstance(asset, dict) and asset.get("name") == name]
        if len(matches) != 1:
            raise ReleaseDownloadError(f"expected exactly one Release asset named {name}")
        url = matches[0].get("browser_download_url")
        parsed = urlsplit(url) if isinstance(url, str) else None
        expected_path = f"/{REPOSITORY}/releases/download/{tag}/{name}"
        if parsed is None or parsed.scheme != "https" or parsed.netloc != "github.com" or parsed.path != expected_path or parsed.query or parsed.fragment:
            raise ReleaseDownloadError(f"invalid download URL for {name}")
        downloads[platform] = {"file_name": name, "url": url}

    return {"schema_version": 1, "version": tag, "downloads": downloads}


def write_manifest(tag: str, release: dict, output: Path) -> None:
    manifest = build_manifest(tag, release)
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


def fetch_release(tag: str) -> dict:
    if not STABLE_TAG.fullmatch(tag):
        raise ReleaseDownloadError("product Tag must be a stable vX.Y.Z release")
    result = subprocess.run(
        ["gh", "api", f"repos/{REPOSITORY}/releases/tags/{tag}"],
        capture_output=True, text=True, check=False, timeout=30,
    )
    if result.returncode != 0:
        raise ReleaseDownloadError(f"GitHub Release lookup failed: {result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ReleaseDownloadError("GitHub returned invalid Release JSON") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag", help="published stable product Tag, for example v0.1.0")
    parser.add_argument("--output", required=True, type=Path, help="Cloud Web desktop-downloads.json target")
    args = parser.parse_args()
    try:
        release = fetch_release(args.tag)
        write_manifest(args.tag, release, args.output)
    except (ReleaseDownloadError, OSError, subprocess.TimeoutExpired) as exc:
        print(f"desktop download manifest update failed: {exc}", file=sys.stderr)
        return 1
    print(f"desktop download manifest updated: {args.output} ({args.tag})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
