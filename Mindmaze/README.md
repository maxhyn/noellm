# MindMaze — Race against time (Python + Pygame)

Beat the maze before the clock hits zero. Collect PolyU-shaped fruits to add time, and reach the glowing exit as fast as you can.

---

## How to Run

Windows PowerShell (recommended):

```powershell
# 1) Create and activate a virtual environment (optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Launch the game
python .\main.py
```

Notes:
- Requires Python 3.10+.
- On Windows with Python 3.13, this project uses `pygame-ce` (a drop-in replacement for pygame) for compatibility. The import remains `import pygame`.

---

## Controls

- WASD / Arrow Keys: Move through the maze one cell at a time.
- R: Regenerate a fresh maze.
- Esc: Pause/Resume or return to Menu.

---

## Gameplay

- Start with 60 seconds.
- Collect PolyU-shaped fruits to add +20s per fruit.
- Reach the exit before time runs out to win.
- Clean black background with white walls for clear visibility.

---

## Repository Structure

```
mindmaze/
├─ main.py
├─ requirements.txt
├─ README.md
├─ LICENSE
├─ data/
│  ├─ negative_words.txt   # (legacy, unused)
│  └─ tips.txt             # (legacy, unused)
└─ assets/
   └─ (optional future images/sfx)
```

---

## Notes

- The previous reflective features (thought prompts, breathing) were removed to focus on a fast, arcade-style maze run.
- Feel free to tweak constants in `main.py`:
  - `START_TIME_SECONDS`, `FRUIT_COUNT`, `FRUIT_BONUS_SECONDS`
  - Grid size: `GRID_W`, `GRID_H`, and `CELL`
  - Colors: `BG_BASE`, `WALL_COLOR`, etc.
