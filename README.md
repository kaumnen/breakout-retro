# Breakout Retro

A Breakout game built with Python, pygame, and pygbag. It runs as a desktop game or in a browser through WebAssembly.

## Run locally

Requires Python 3.13 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python main.py
```

## Run in a browser

```bash
uv run pygbag main.py
```

Open <http://localhost:8000> if the browser does not open automatically.

## Controls

| Action | Input |
| --- | --- |
| Start or restart | Space, Enter, or left click |
| Move paddle | Mouse, arrow keys, or A and D |
| Fire laser or release ball | Space or left click |
| Pause or resume | Escape |
| Restart while paused | R |

## Power-ups

Bricks can drop multiball, wide paddle, small paddle, laser, sticky paddle, extra life, or slow ball effects.

## Tests

```bash
uv run python -m unittest discover -s tests
```

## Web build

```bash
uv run pygbag --build main.py
```

Static files are written to `build/web`.
