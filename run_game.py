"""Entry point to run the Breakout game."""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from breakout.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
