#!/bin/sh
# Packs the build into dist/2048-<target>.tar.gz (.zip for Windows) for
# av: the binary at the top, with LICENSE, README.md and PATCHES.md.
#
#   asciiverse/package.sh x86_64-unknown-linux-musl
set -eu
cd "$(dirname "$0")/.."
target="$1"
case "$target" in *windows*) exe=.exe ;; *) exe= ;; esac
stage=stage/2048
rm -rf "$stage" && mkdir -p "$stage" dist
cp "out/2048$exe" LICENSE README.md PATCHES.md "$stage/"
if [ -n "$exe" ]; then
  (cd "$stage" && zip -qr "../../dist/2048-$target.zip" .)
else
  tar -czf "dist/2048-$target.tar.gz" -C "$stage" .
fi
ls dist
