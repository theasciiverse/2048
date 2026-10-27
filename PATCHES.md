# Changes from upstream

This is the Asciiverse packaging of [2048.c](https://github.com/mevdschee/2048.c)
by Maurits van der Schee, a console version of 2048 (Gabriele Cirulli's 2014 game),
under the MIT licence (LICENSE: "Copyright (c) 2024 Maurits van der
Schee"). Upstream is the `upstream` remote; the `asciiverse` branch starts
from its newest release, v1.0.5 (`90343eb`, 2026-10-07), which is also
the head of `main`.

## Debian

Debian packages it as `2048` (1.0.3-1). Its packaging repo
(salsa.debian.org/games-team/2048) is the `debian` remote, fetched
without its tags. Its two patches are packaging only and not applied:
`install.patch` moves the binary to /usr/games and installs an icon, and
`desktop.patch` fixes the path in the desktop file (Asciiverse installs
no desktop entries).

## Code

- **Version.** The v1.0.4 and v1.0.5 tags left `VERSION` at 1.0.3, so
  `--version` reported the wrong release; it says 1.0.5.
- **Centred, also after a resize.** The board was drawn from the top
  left corner. It is placed in the middle of the terminal, each line
  positioned on its own, and placed and drawn again when the terminal is
  resized. Keys are read with `read()` instead of `getchar()`, so the
  wait that `SIGWINCH` interrupts is simply retried (with `getchar()` it
  would have ended the game with "Cannot read keyboard input"); a QUIT?
  or RESTART? prompt showing at the time is shown again. On exit the
  cursor is left below the board.
- **Game over waits.** The game ended the moment no move was left, so a
  launcher that takes the screen back at once, such as av, hid the final
  board and score. It shows "GAME OVER r: again q: quit" and waits.
- **Windows.** Keys come from `_getch()`, with the cursor keys' scan codes
  given the letters their ANSI sequences end in, so the same key handling
  serves both; the console is switched to UTF-8 and to virtual terminal
  processing for the drawing (Windows 10 and later) and restored on
  exit; `usleep()` is `Sleep()`; a new console size is noticed while
  polling for keys, as Windows has no `SIGWINCH`.

## Packaging (new files)

- `asciiverse/build.sh`: the one source file in one compiler call; no
  libraries.
- `asciiverse/package.sh`: one archive per target with the binary,
  LICENSE, README.md and this file.
- `.github/workflows/release.yml`: static Linux in Alpine (x86_64,
  aarch64), macOS (x86_64, arm64) and Windows x86_64 (MinGW), plus
  SHA256SUMS, on a tag; the built-in `2048 test` runs where the binary
  can run.
- `asciiverse/record-preview.py`: records `asciiverse/2048.cast`; a
  driver reads the board from the screen and picks moves with a two-ply
  expectimax search.
- `.gitignore`: the build folders.

## Tested

Linux: native (glibc) and static (Alpine 3.22, musl) builds; `2048 test`
passes; played at 100x30, resized to 60x20 and 80x24 while playing and
at the QUIT? prompt; played to game over (1,870 random moves), r starts
a new game with 0 points, q then y exits with status 0. ASan and UBSan:
five 40-second runs of random keys (arrows, WASD, vi keys, r and q with
their prompts) with random resizes, no reports. Windows: cross-built
with MinGW-w64 and run under Wine: keys (letters and arrows), the score
and quitting work, but Wine's console prints the escape sequences and
UTF-8 literally, so the drawing on a real Windows console is unchecked.
macOS: not built here.

## Ours

- **How to play it, at the top of README.md.** A short note on installing and
  starting it with av, or from a release archive; the original text follows
  unchanged.
