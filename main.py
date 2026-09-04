"""Canonical local and pygbag entry point for Breakout Retro."""

import asyncio
import os
import sys

# Pygbag scans this entry point for third-party imports before loading the game.
# Keep pygame here even though the application imports it again internally.
import pygame


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from breakout.main import main


if __name__ == "__main__":
    asyncio.run(main())
