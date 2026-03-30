# Urinal Game

A two-player combinatorial graph coloring game built with Python and Tkinter.
**Painter** tries to successfully color a graph; **Spoiler** tries to make it impossible. Draw any graph, pick your colors, and see who wins.

---

## How It Works

The game is played on a graph that you draw yourself. On each turn, a player assigns a color to any uncolored vertex. The rules are simple:

- **Painter wins** if every vertex gets colored without any two adjacent vertices sharing a color.
- **Spoiler wins** if any vertex is left with no legal colors remaining.

Both players alternate turns and can color *any* uncolored vertex — not just their "own." This is what makes the game strategically interesting: Spoiler doesn't block colors directly, they manipulate the order and placement of colors to paint the painter into a corner.

---

## Features

- **Draw your own graph** — left-click to place vertices and drag between them to add edges; right-click drag to reposition nodes
- **Configurable colors** — set how many colors are available before the game starts
- **Three play modes** — Human vs Human, Human vs Computer, or Computer vs Computer
- **Choose who goes first** — Painter or Spoiler
- **Two AI difficulties** — Random (fast, chaotic) or Minimax (strategic, depth-configurable)
- **Undo support** — step back through graph edits before starting
- **Legality enforcement** — illegal moves are rejected; the game detects terminal states automatically

---

## Installation

```bash
git clone https://github.com/yourname/urinal-game.git
cd urinal-game
python3 urinal_game.py
```

No pip dependencies. The only requirement outside the standard library is **Tkinter**, which needs a little extra setup on macOS and Linux.

---

### Tkinter Setup

#### Verify first

Before anything else, check whether Tkinter is already available:

```bash
python3 -m tkinter
```

A small grey window should pop up. If it does, you're good — skip the rest of this section.

---

#### macOS

The most common cause of Tkinter issues on macOS is using Homebrew Python, which doesn't bundle it by default.

**Homebrew Python:**
```bash
brew install python-tk
```
If you're on a specific version (e.g. 3.12):
```bash
brew install python-tk@3.12
```

**python.org installer:** Tkinter is bundled, but if it still fails, run the *Install Certificates* script that ships with the installer at `/Applications/Python 3.x/`.

**pyenv:** Tkinter must be present on the system *before* compiling Python. Install the Tcl/Tk dev headers first, then reinstall your Python version:
```bash
brew install tcl-tk
pyenv install 3.12.x   # or whichever version you use
```

---

#### Linux

Tkinter ships separately from Python on all major distros — install it via your package manager.

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install python3-tk
```

**Fedora / RHEL:**
```bash
sudo dnf install python3-tkinter
```

**Arch:**
```bash
sudo pacman -S tk
```

**pyenv on Linux:** Same as macOS — install the dev headers before compiling Python:
```bash
sudo apt install tk-dev   # Debian/Ubuntu
pyenv install 3.12.x
```

If you installed Python via pyenv *before* installing `tk-dev`, you'll need to reinstall the Python version for it to pick up Tkinter.

---

## Usage

1. **Draw a graph** using left-click (place nodes, drag to connect)
2. **Configure** the number of colors, play mode, AI type, and who goes first in the left panel
3. Hit **Start Game** — the app will verify the graph is actually n-colorable before beginning
4. **Click a vertex** to color it (select a color from the palette at the bottom first)
5. When the game ends, hit **Reset** to draw a new graph and play again

---

## Controls

| Action | Input |
|---|---|
| Place vertex | Left click (empty space) |
| Add edge | Left click + drag (node → node) |
| Move vertex | Right click + drag |
| Color a vertex | Select color → left click vertex |
| Undo last edit | Undo button |
| Reset everything | Reset button |

---

## Background

This game is a combinatorial variant of the **graph coloring problem**.
The theoretical question — for a given graph and *k* colors, does Painter have a winning strategy? — is related to a graph's "game chromatic number," which is always at least as large as its ordinary chromatic number and can be strictly larger.
It's an active area of combinatorics research.

---

## Project Structure

```
urinal_game.py      # Everything: graph model, game logic, AI, and GUI
```

