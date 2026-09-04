"""Canonical local and pygbag entry point for Breakout Retro."""

import asyncio
import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from breakout.main import main


if __name__ == "__main__":
    asyncio.run(main())
