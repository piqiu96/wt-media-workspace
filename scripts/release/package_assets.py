#!/usr/bin/env python3
"""Refuse an incomplete release and produce its public inventory and checksums."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import tomllib
import zipfile
from pathlib import Path


PLATFORMS = {
    "windows-x64": "x86_64-pc-windows-msvc",
    "macos-x64": "x86_64-apple-darwin",
    "macos-arm64": "aarch64-apple-darwin",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exactly_one(paths: list[Path], label: str) -> Path:
    if len(paths) != 1:
        raise ValueError(f"expected one {label}, found {len(paths)}")
    if paths[0].stat().st_size == 0:
        raise ValueError(f"empty {label}: {paths[0]}")
    return paths[0]


def verify_cloud(path: Path, tag: str, source_commit: str) -> None:
    with tarfile.open(path, "r:gz") as archive:
        names = {entry.name for entry in archive}
        root = f"wt-media-cloud_{tag}_linux-amd64/"
        required = (
            "bin/server", "bin/discovery-scheduler", "bin/discovery-worker", "bin/migrate",
            "bin/ffmpeg", "bin/ffprobe", "web/index.cloud.html", "ffmpeg-source.json",
            "release-info.json", "deploy/DEPLOYMENT.md", "deploy/prepare-database.sql.example",
            "deploy/install.sh", "deploy/init-config.sh", "deploy/migrate.sh",
            "deploy/activate.sh", "deploy/verify-package.sh", "deploy/verify-database.sh",
            "deploy/verify-runtime.sh", "deploy/rollback.sh",
            "deploy/systemd/wt-media-cloud-server.service",
            "deploy/systemd/wt-media-cloud-scheduler.service",
            "deploy/systemd/wt-media-cloud-worker.service",
            "deploy/config-template/app.toml", "deploy/config-template/database/primary.toml",
            "deploy/config-template/credentials/agent.toml",
            "deploy/config-template/credentials/douyin.toml",
            "deploy/config-template/credentials/object_storage.toml.example",
        )
        for relative in required:
            if root + relative not in names:
                raise ValueError(f"Cloud package omits {relative}")
        if not any(name.startswith(root + "migrations/") and name.endswith(".sql") for name in names):
            raise ValueError("Cloud package omits SQL migrations")
        if any(
            "config_online" in name or name.startswith(root + "config/")
            or name == root + "deploy/config-template/credentials/object_storage.toml"
            for name in names
        ):
            raise ValueError("Cloud package contains private runtime configuration")

        def read(relative: str) -> bytes:
            stream = archive.extractfile(root + relative)
            if stream is None:
                raise ValueError(f"Cloud package cannot read {relative}")
            return stream.read()

        info = json.loads(read("release-info.json"))
        if info.get("product_tag") != tag or info.get("source_commit") != source_commit:
            raise ValueError("Cloud package Tag or source Commit differs from Release Manifest")
        blank_fields = (
            ("deploy/config-template/app.toml", ("initial_admin", "password")),
            ("deploy/config-template/database/primary.toml", ("password",)),
            ("deploy/config-template/credentials/agent.toml", ("auth_token",)),
            ("deploy/config-template/credentials/douyin.toml", ("api_key",)),
            ("deploy/config-template/credentials/douyin.toml", ("cookie",)),
        )
        for relative, keys in blank_fields:
            value = tomllib.loads(read(relative).decode("utf-8"))
            for key in keys:
                value = value[key]
            if value != "":
                raise ValueError(f"Cloud package has a nonempty credential in {relative}")


def verify_cloud_artifact_checksums(directory: Path, cloud: Path, web: Path) -> None:
    sums_file = directory / "SHA256SUMS"
    if not sums_file.is_file():
        raise ValueError("Cloud artifact omits SHA256SUMS")
    entries = {}
    for line in sums_file.read_text(encoding="utf-8").splitlines():
        parts = line.split("  ", 1)
        if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]) or parts[1] in entries:
            raise ValueError("Cloud artifact has an invalid SHA256SUMS entry")
        entries[parts[1]] = parts[0]
    if set(entries) != {cloud.name, web.name}:
        raise ValueError("Cloud artifact checksum file does not name both packages exactly")
    for package in (cloud, web):
        if sha256(package) != entries[package.name]:
            raise ValueError(f"Cloud artifact SHA-256 mismatch: {package.name}")


def public_asset_name(tag: str, platform: str, suffix: str) -> str:
    """GitHub-safe public name without discarding the product identity."""
    return f"WT-Media_{tag}_{platform}{suffix}"


def normalize_public_asset(
    source: Path, assets: Path, tag: str, platform: str, suffix: str
) -> Path:
    target_name = public_asset_name(tag, platform, suffix)
    target = assets / target_name
    if target.exists():
        raise ValueError(f"duplicate normalized Desktop asset: {target_name}")
    source.rename(target)
    return target


def verify_mac(path: Path, origin: str) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        for suffix in ("/Contents/Resources/config/agent.toml", "/Contents/Resources/resources/desktop.production.toml", "/Contents/Resources/sidecar-manifest.json", "/Contents/Resources/versions.json"):
            matching = [name for name in names if name.endswith(suffix)]
            if len(matching) != 1:
                raise ValueError(f"{path.name} omits or duplicates {suffix}")
            if suffix.endswith(".toml") and origin.encode() not in archive.read(matching[0]):
                raise ValueError(f"{path.name} has wrong Cloud origin in {suffix}")
        if not any(name.endswith(".dmg") for name in names):
            raise ValueError(f"{path.name} has no DMG")


def package(tag: str, origin: str, manifest: Path, assets: Path, cloud_artifact: Path, agent_artifacts: Path, source_commits: dict[str, str]) -> None:
    if not manifest.is_file() or not assets.is_dir() or not agent_artifacts.is_dir():
        raise ValueError("Manifest, Desktop assets, and Agent artifacts are required")
    if set(source_commits) != {"workspace", "cloud", "agent", "desktop"} or any(not re.fullmatch(r"[0-9a-f]{40}", commit) for commit in source_commits.values()):
        raise ValueError("all four source commits must be full Git SHA-1 values")
    cloud = exactly_one(list(cloud_artifact.glob(f"wt-media-cloud_{tag}_linux-amd64.tar.gz")), "Cloud Linux package")
    web = exactly_one(list(cloud_artifact.glob("desktop-web_*.tar.gz")), "Desktop Web package")
    verify_cloud_artifact_checksums(cloud_artifact, cloud, web)
    verify_cloud(cloud, tag, source_commits["cloud"])
    for platform, target in PLATFORMS.items():
        folder = agent_artifacts / f"agent-{platform}"
        record = json.loads((folder / "sidecar-manifest.json").read_text(encoding="utf-8"))
        if record["target"] != target or record["component"] != "wt-media-agent":
            raise ValueError(f"wrong Sidecar target for {platform}")
        binary = folder / record["filename"]
        if not binary.is_file() or sha256(binary) != record["sha256"]:
            raise ValueError(f"Sidecar SHA-256 mismatch for {platform}")
    installers = [path for path in assets.iterdir() if path.is_file()]
    windows_source = exactly_one(
        [path for path in installers if path.suffix.lower() == ".exe"],
        "Windows NSIS installer",
    )
    intel_source = exactly_one(
        [path for path in installers if path.name.endswith("_macos-x64.zip")],
        "macOS Intel package",
    )
    arm_source = exactly_one(
        [path for path in installers if path.name.endswith("_macos-aarch64.zip")],
        "macOS ARM package",
    )
    if set(installers) != {windows_source, intel_source, arm_source}:
        raise ValueError("unexpected Desktop release assets")
    windows = normalize_public_asset(windows_source, assets, tag, "windows-x64-setup", ".exe")
    intel = normalize_public_asset(intel_source, assets, tag, "macos-x64", ".zip")
    arm = normalize_public_asset(arm_source, assets, tag, "macos-arm64", ".zip")
    for path in (intel, arm):
        verify_mac(path, origin)
    (assets / manifest.name).write_bytes(manifest.read_bytes())
    info = {
        "schema_version": 1,
        "product_tag": tag,
        "cloud_origin": origin,
        "source_commits": source_commits,
        "cloud_artifact": {"name": cloud.name, "sha256": sha256(cloud)},
        "desktop_web_artifact": {"name": web.name, "sha256": sha256(web)},
        "agent_artifacts": {platform: json.loads((agent_artifacts / f"agent-{platform}" / "sidecar-manifest.json").read_text(encoding="utf-8")) for platform in PLATFORMS},
        "desktop_assets": {path.name: sha256(path) for path in (windows, intel, arm)},
    }
    (assets / "build-info.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    paths = sorted(path for path in assets.iterdir() if path.is_file() and path.name != "SHA256SUMS")
    (assets / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in paths), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", required=True)
    parser.add_argument("--cloud-origin", required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--cloud-artifact", type=Path, required=True)
    parser.add_argument("--agent-artifacts", type=Path, required=True)
    parser.add_argument("--source-commit", action="append", required=True)
    args = parser.parse_args()
    try:
        source_commits = dict(pair.split("=", 1) for pair in args.source_commit)
        package(args.tag, args.cloud_origin, args.manifest, args.assets, args.cloud_artifact, args.agent_artifacts, source_commits)
    except (OSError, ValueError, KeyError, tarfile.TarError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        parser.exit(1, f"release package invalid: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
