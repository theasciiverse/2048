#!/bin/sh
# Builds 2048 into out/: one C file, no libraries (it draws with ANSI
# escape sequences itself), so one compiler call serves every target (see
# .github/workflows/release.yml):
#
#   asciiverse/build.sh                                        # Linux
#   LDFLAGS="-static -s" asciiverse/build.sh                   # Alpine, static
#   CFLAGS="-O2 -arch arm64" LDFLAGS="-arch arm64" asciiverse/build.sh  # macOS
#   CC=x86_64-w64-mingw32-gcc LDFLAGS="-static -s" EXE=.exe \
#     asciiverse/build.sh                                      # Windows
set -eu
cd "$(dirname "$0")/.."
CC="${CC:-cc}"
CFLAGS="${CFLAGS:--O2}"
LDFLAGS="${LDFLAGS:-}"
EXE="${EXE:-}"
mkdir -p out
rm -f "out/2048$EXE"
# shellcheck disable=SC2086
nice -n 10 $CC -std=c99 -Wextra $CFLAGS -o "out/2048$EXE" 2048.c $LDFLAGS
echo "built 2048$EXE"
