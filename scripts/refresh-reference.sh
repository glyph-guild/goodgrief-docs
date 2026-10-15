#!/bin/sh
# Moves src/data/gg-reference.json to a released gg.
#
#   scripts/refresh-reference.sh 0.89.0
#
# Downloads that release's binary for this machine, runs
# `gg reference --json`, and writes the result. Run `npm run build` after,
# which regenerates the CLI and console-key pages and checks every page
# against the new list.
set -eu

v="${1:?usage: scripts/refresh-reference.sh <gg version, such as 0.89.0>}"

case "$(uname -s)-$(uname -m)" in
  Darwin-arm64) rid=osx-arm64 ;;
  Darwin-x86_64) rid=osx-x64 ;;
  Linux-x86_64) rid=linux-x64 ;;
  Linux-aarch64) rid=linux-arm64 ;;
  *) echo "No gg build for $(uname -s) $(uname -m)." >&2; exit 1 ;;
esac

here="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

curl -fsSL "https://github.com/glyph-guild/gg/releases/download/v$v/gg-$rid.tar.gz" | tar xz -C "$work"
"$work/gg" reference --json > "$here/src/data/gg-reference.json"
echo "src/data/gg-reference.json now describes gg $v."
