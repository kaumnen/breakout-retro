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
uv run python scripts/build_web.py --serve
```

Open <http://127.0.0.1:8000>.

## Controls

| Action | Input |
| --- | --- |
| Start | Space, Enter, or left click |
| Restart after a game | Space, Enter, or R |
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
uv run python scripts/build_web.py
```

Static files are written to `build/web`.

Cloudflare Pages build command:

```bash
pip install pygame pygbag==0.9.3 && python scripts/build_web.py
```

Set the output directory to `build/web`.
