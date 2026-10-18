#!/usr/bin/env python3
"""Records asciiverse/2048.cast, the catalog preview, at 100x30
(hub/RECORDING.md): a game played by a driver that reads the board from
the screen and picks each move with a two-ply expectimax search (every
move, then every place a new 2 or 4 can appear), scoring boards by empty
cells, smooth rows and columns and the biggest tile in a corner. After
about 50 seconds it quits with q and y.

2048 runs from out/ (asciiverse/build.sh) by name, so the cast's header
holds no local path.

Needs asciinema 3.x and pyte. Usage, from the repo root:
  uv run --with pyte python3 asciiverse/record-preview.py
Any extra argument is used as the cast's path instead (for test runs);
with --dry-run it plays without recording."""
import fcntl, os, pty, select, struct, sys, termios, time
import pyte

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
args = [a for a in sys.argv[1:] if a != "--dry-run"]
dry = "--dry-run" in sys.argv
cast = args[0] if args else f"{root}/asciiverse/2048.cast"
COLS, ROWS, PLAY = 100, 30, float(os.environ.get("PLAY", "50"))
KEYS = {"up": b"\x1b[A", "down": b"\x1b[B", "right": b"\x1b[C", "left": b"\x1b[D"}

env = dict(os.environ, TERM="xterm-256color", COLORTERM="truecolor", LANG="C.UTF-8",
           PATH=f"{root}/out:{os.environ['PATH']}")
for v in ("VTE_VERSION", "TERM_PROGRAM", "TERM_PROGRAM_VERSION", "TMUX"):
    env.pop(v, None)

pid, fd = pty.fork()
if pid == 0:
    if dry:
        os.execvpe("2048", ["2048"], env)
    os.execvpe("asciinema", ["asciinema", "rec", "--overwrite", "-q", "--idle-time-limit", "2",
        "--window-size", f"{COLS}x{ROWS}", "--capture-env", "TERM,COLORTERM,LANG",
        "--title", "2048", "--command", "2048", cast], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
screen = pyte.Screen(COLS, ROWS)
stream = pyte.ByteStream(screen)
start = time.time()


def pump(seconds):
    end = time.time() + seconds
    while True:
        left = end - time.time()
        r, _, _ = select.select([fd], [], [], max(0.0, min(0.02, left)))
        if r:
            try:
                stream.feed(os.read(fd, 65536))
            except OSError:
                return False
        if left <= 0:
            return True


def key(k, wait=0.3):
    os.write(fd, k)
    pump(wait)


def read_board():
    """The 4x4 board as rows of numbers (0 for empty), from the screen: the
    score line gives the board's corner, each tile is seven columns wide
    and its number sits on the middle of its three lines."""
    for y, line in enumerate(screen.display):
        x = line.find("2048.c")
        if x >= 0:
            break
    else:
        return None
    board = []
    for r in range(4):
        row = []
        for c in range(4):
            cell = screen.display[y + 3 + 3 * r][x + 7 * c:x + 7 * c + 7].strip()
            row.append(int(cell) if cell.isdigit() else 0)
        board.append(row)
    return board


def slide(row):
    tiles = [t for t in row if t]
    out, i = [], 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
            out.append(tiles[i] * 2)
            i += 2
        else:
            out.append(tiles[i])
            i += 1
    return out + [0] * (4 - len(out))


def move(board, d):
    if d == "left":
        return [slide(r) for r in board]
    if d == "right":
        return [slide(r[::-1])[::-1] for r in board]
    cols = [list(c) for c in zip(*board)]
    cols = [slide(c) if d == "up" else slide(c[::-1])[::-1] for c in cols]
    return [list(r) for r in zip(*cols)]


def score(board):
    empty = sum(row.count(0) for row in board)
    rough = 0
    for line in board + [list(c) for c in zip(*board)]:
        for a, b in zip(line, line[1:]):
            if a and b:
                rough += abs(a.bit_length() - b.bit_length())
    big = max(max(r) for r in board)
    corner = big in (board[0][0], board[0][3], board[3][0], board[3][3])
    return empty * 3.0 - rough * 0.5 + (big.bit_length() if corner else 0) * 2.0


def best(board):
    choice, value = None, None
    for d in KEYS:
        after = move(board, d)
        if after == board:
            continue
        spots = [(r, c) for r in range(4) for c in range(4) if after[r][c] == 0]
        total = 0.0
        for r, c in spots:
            for tile, p in ((2, 0.9), (4, 0.1)):
                b = [row[:] for row in after]
                b[r][c] = tile
                total += p * max((score(move(b, e)) for e in KEYS if move(b, e) != b),
                                 default=-100.0)
        v = total / max(1, len(spots))
        if value is None or v > value:
            choice, value = d, v
    return choice


pump(1.5)
while time.time() - start < PLAY:
    if "GAME OVER" in "\n".join(screen.display):
        break
    board = read_board()
    d = best(board) if board else None
    if d is None:
        break
    key(KEYS[d], 0.35)
final = read_board()
pump(1.5)
key(b"q", 1.2)
key(b"y", 0.5)
end = time.time() + 5
while time.time() < end:
    if not pump(0.1):
        break
    done, _ = os.waitpid(pid, os.WNOHANG)
    if done:
        break
else:
    os.kill(pid, 9)
try:
    os.waitpid(pid, 0)
except ChildProcessError:
    pass
print(f"{cast}: {time.time() - start:.0f} s, biggest tile {max(max(r) for r in final) if final else '?'}",
      file=sys.stderr)
