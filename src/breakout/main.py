"""Main entry point for the Breakout game - WebAssembly compatible."""

import asyncio
import pygame

from breakout.game import Game


async def main():
    """Main game loop with WebAssembly compatibility."""
    # Initialize pygame
    pygame.init()
    try:
        pygame.mixer.init()
    except pygame.error:
        # Browsers and headless environments may not expose an audio device.
        pass
    
    try:
        # Create and run the game
        game = Game()
        await game.run()
    except KeyboardInterrupt:
        print("Game interrupted by user")
    finally:
        # Clean up
        pygame.quit()


if __name__ == "__main__":
    # Run the game
    asyncio.run(main())
