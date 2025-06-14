"""Main entry point for the Breakout game - WebAssembly compatible."""

import asyncio
import pygame
import sys
import os

# Add the src directory to the path for web compatibility
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from breakout.game import Game


async def main():
    """Main game loop with WebAssembly compatibility."""
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    try:
        # Create and run the game
        game = Game()
        await game.run()
    except KeyboardInterrupt:
        print("Game interrupted by user")
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        pygame.quit()


if __name__ == "__main__":
    # Run the game
    asyncio.run(main())
