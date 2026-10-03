#!/usr/bin/env bash
set -euo pipefail

MODE="${1:?rc or stable required}"
TAG="${2:?product Tag required}"
ASSETS="${3:?verified assets directory required}"
[[ "$MODE" == rc || "$MODE" == stable ]] || { echo "invalid release mode: $MODE" >&2; exit 1; }
[[ -s "$ASSETS/SHA256SUMS" && -s "$ASSETS/build-info.json" && -s "$ASSETS/$TAG.yaml" ]] || {
  echo "verified release inventory is incomplete" >&2
  exit 1
}
cd "$ASSETS"
sha256sum --check SHA256SUMS
cd - >/dev/null
printf 'WT Media %s\n\nCloud Linux package and Desktop Web remain in this run’s controlled Actions artifacts. See build-info.json for their SHA-256.\n' "$TAG" > "$ASSETS/RELEASE-NOTES.txt"
gh release create "$TAG" "$ASSETS"/*.zip "$ASSETS"/*.exe "$ASSETS"/build-info.json "$ASSETS"/SHA256SUMS "$ASSETS/$TAG.yaml" --verify-tag --draft --title "WT Media $TAG" --notes-file "$ASSETS/RELEASE-NOTES.txt"
if [[ "$MODE" == rc ]]; then
  gh release edit "$TAG" --draft=false --prerelease
fi

# GitHub is part of the release boundary, not merely a file sink. Check the
# names and bytes that a user can actually download after upload and renaming.
expected=$(
  cd "$ASSETS"
  find . -maxdepth 1 -type f ! -name RELEASE-NOTES.txt -printf '%f\n' | LC_ALL=C sort
)
actual=$(gh release view "$TAG" --json assets --jq '[.assets[].name] | sort | .[]')
if [[ "$expected" != "$actual" ]]; then
  printf 'published asset names differ:\nexpected:\n%s\nactual:\n%s\n' "$expected" "$actual" >&2
  exit 1
fi
verify_dir="$(mktemp -d)"
gh release download "$TAG" --dir "$verify_dir" --clobber
(
  cd "$verify_dir"
  sha256sum --check SHA256SUMS
)
