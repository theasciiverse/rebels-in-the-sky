#!/usr/bin/env python3
"""Records asciiverse/rebels-in-the-sky.cast, the catalog preview
(hub/RECORDING.md). The game is laid out for 160x48 and below that cuts off
the buttons a match needs (the crew panel's Challenge), so this records at
160x48 and the manifest crops to 100x30 ("Record big, crop to 100x30").
Runs offline and silent (-l -a) with a fixed seed, in a scratch HOME so no
save of yours is touched. A pilot that reads the screen through pyte shows
the title, creates a crew (names, planet, colours, ship, and affordable
players), challenges a crew open to it, spends the 20 s before tip-off on
the Galaxy tab, then watches the match in the court view. About 55 s.
Needs pyte. Usage, from the repo root after cargo build --release:
    python3 asciiverse/record-preview.py
TIMES=1 prints when each step happens; DUMP=1 also prints the screen."""
import os, pty, re, struct, fcntl, select, shutil, tempfile, termios, time
import pyte

COLS, ROWS = map(int, os.environ.get("SIZE", "160x48").split("x"))
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cast = os.path.join(root, "asciiverse", "rebels-in-the-sky.cast")
home = tempfile.mkdtemp()
env = dict(os.environ, HOME=home, XDG_CONFIG_HOME=os.path.join(home, ".config"),
           TERM="xterm-256color", COLORTERM="truecolor", LANG="C.UTF-8")
DUMP = os.environ.get("DUMP")

screen = pyte.Screen(COLS, ROWS)
stream = pyte.ByteStream(screen)

shutil.copy(os.path.join(root, "target", "release", "rebels"), home)
pid, fd = pty.fork()
if pid == 0:
    os.chdir(home)      # so the recording shows no local paths
    os.execvpe("asciinema", ["asciinema", "rec", "--overwrite", "-q", "-i", "2",
        "--window-size", f"{COLS}x{ROWS}", "--capture-env", "TERM,COLORTERM,LANG",
        "-c", "./rebels -l -a --random-seed 2101", cast], env)
fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))

done = False
def alive():
    global done
    if not done and os.waitpid(pid, os.WNOHANG)[0]: done = True
    return not done

def pump(t):
    end = time.time() + t
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.01)
        if r:
            try: stream.feed(os.read(fd, 65536))
            except OSError: return

def stop_game():
    """Last resort: end the game under asciinema so the recording closes
    instead of running on (and writing to the cast) after we leave."""
    import signal
    kids, todo = [], [pid]
    while todo:
        p = todo.pop()
        try: ch = open(f"/proc/{p}/task/{p}/children").read().split()
        except OSError: ch = []
        kids += ch; todo += [int(c) for c in ch]
    for k in reversed(kids):
        try: os.kill(int(k), signal.SIGTERM)
        except ProcessLookupError: pass

def text():
    return "\n".join(screen.display)

T0 = time.time()
def dump(tag):
    print(f"[{time.time() - T0:5.1f}s] {tag}", flush=True) if os.environ.get("TIMES") else None
    if DUMP:
        print("=====", tag); print("\n".join(l.rstrip() for l in screen.display), flush=True)

def key(k, wait=0.3):
    os.write(fd, k); pump(wait)

def wait_for(s, limit=15.0):
    end = time.time() + limit
    while time.time() < end and alive() and s not in text():
        pump(0.1)
    return s in text()

def typed(s, wait=0.12):
    for c in s: key(c.encode(), wait)

UP, DOWN, ENTER = b"\x1b[A", b"\x1b[B", b"\r"

def balance():
    m = re.search(r"Remaining balance: (-?\d+) sat", text())
    return int(m.group(1)) if m else None

def to_pick():
    m = re.search(r"Select (\d+) players", text())
    return int(m.group(1)) if m else None

def highlighted():
    """Name and price of the player the card on the right shows."""
    m = re.search(r"┌([^─★┐]+?) [★½☆]", screen.display[0])
    if not m: return None, None
    name = m.group(1).strip()
    for line in screen.display:
        r = re.search(re.escape(name) + r"\s+(\d+) sat", line)
        if r: return name, int(r.group(1))
    return name, None

# title
wait_for("New Game"); pump(2.5); dump("title")
key(ENTER)                      # New Game (the default without a save)
wait_for("Team name", 20.0); pump(1.0); dump("creation")
typed("Asciiverse", 0.06); key(ENTER, 0.4)
typed("Terminus", 0.06); key(ENTER, 0.4)
for _ in range(2): key(DOWN, 0.4)
key(ENTER, 0.6)                 # home planet
for _ in range(3): key(ENTER, 0.4)   # colours
key(DOWN, 0.3); key(ENTER, 0.6)      # jersey style
key(ENTER, 0.6)                 # spaceship model
dump("players")
seen = set()
for _ in range(80):
    n, money = to_pick(), balance()
    if not n or money is None: break
    name, price = highlighted()
    # keep enough for the rest: sign whoever costs no more than a fair share
    if name and price and name not in seen and price <= money / n:
        key(ENTER, 0.5); seen.add(name); dump(f"signed {name} {price}")
    key(DOWN, 0.2)
dump("crew")
key(ENTER)                      # confirm the crew
wait_for("Tutorial", 15.0); pump(1.5); dump("game")
key(b"\x7f", 0.8); dump("tutorial closed")    # Backspace: close the tutorial
key(b"\x1b[C", 1.5); dump("crews")              # Right: the Crews tab
# Tab: show only the crews open to a challenge, then challenge one; the
# match opens in the Games tab with its commentary
key(b"\t", 1.2); dump("open to challenge")
for _ in range(20):
    key(b"C", 0.7)
    if "Commentary" in text(): break
    key(DOWN, 0.3)
start = time.time() + 20        # local games start 20 s later (GAME_START_DELAY)
dump("challenged")
if "Challenge accepted" in text():
    pump(1.0); key(b"\x7f", 0.5)   # close the popup (Backspace)
pump(1.5)
for _ in range(2): key(b"\x1b[C", 0.4)        # Tournaments, Galaxy
dump("galaxy")
pump(max(0.0, start - 4 - time.time()))
for _ in range(2): key(b"\x1b[D", 0.4)        # back to Games
pump(max(0.0, start + 1 - time.time()))
key(b"v", 0.5); dump("court")   # the court view
end = time.time() + float(os.environ.get("LOOK_SECONDS", 10))
while time.time() < end and alive():
    pump(2.0); dump("match")
if alive():
    key(b"\x1b", 1.0); dump("esc")
    key(ENTER, 2.0)
for _ in range(30):
    if not alive(): break
    pump(0.2)
if alive():
    stop_game(); pump(1.0)
shutil.rmtree(home, ignore_errors=True)
