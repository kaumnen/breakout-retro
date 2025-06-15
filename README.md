> [!IMPORTANT]  
> This repository has been vibe-coded! See the linked blog post to learn more. Breakout game available at: https://breakout.kaumnen.com/

# Breakout Retro

A classic Breakout game built with Python 3.13, pygame, and pygbag for web deployment. Experience the nostalgic arcade gameplay with modern power-ups and smooth physics!

## 🎮 Game Features

### Core Gameplay
- **Classic Breakout mechanics** with smooth ball physics
- **Multiple lives system** (start with 3 lives)
- **Progressive scoring** with combo multipliers
- **Responsive paddle control** via mouse or keyboard
- **Collision detection** with realistic ball bouncing
- **Victory and game over states**

### Power-ups System
Destroy bricks to randomly drop power-ups (25% chance per brick). Catch them with your paddle to activate special abilities:

#### 🔴 **Multiball** (Most Common)
- Spawns additional balls for maximum chaos
- Each ball can destroy bricks independently
- Lose a life only when ALL balls fall off screen

#### 🟢 **Large Paddle** 
- Increases paddle size for easier ball catching
- Makes the game more forgiving
- Duration: 10 seconds

#### 🟡 **Small Paddle** (Negative Effect)
- Decreases paddle size for added challenge
- Avoid this one if possible!
- Duration: 10 seconds

#### 🔵 **Laser Paddle**
- Equips your paddle with laser cannons
- Press SPACE to fire lasers that destroy bricks
- Limited ammunition, use wisely!

#### 🟣 **Sticky Paddle**
- Ball sticks to paddle on contact
- Press SPACE to release the ball
- Perfect for precise aiming

#### 🟠 **Extra Life**
- Grants an additional life
- Instant effect, no duration

#### 🔵 **Slow Ball**
- Reduces ball speed for better control
- Easier to track and react to ball movement
- Duration: 10 seconds

## 🎯 Controls

### Menu
- **SPACE** - Start the game

### Gameplay
- **Mouse** - Move paddle left/right
- **Arrow Keys** - Alternative paddle control
- **SPACE** - Fire lasers (with Laser Paddle power-up) or release ball (with Sticky Paddle)
- **ESC** - Pause/unpause game

### Pause Menu
- **ESC** - Resume game
- **R** - Restart game

### Game Over
- **R** - Restart game
- **ESC** - Return to main menu

## 🚀 How to Run

### Prerequisites
- Python 3.13+
- uv package manager

### Local Installation
```bash
# Clone the repository
git clone <repository-url>
cd breakout_retro

# Install dependencies
uv sync

# Run the game locally
uv run python simple_breakout.py
```

### Web Assembly (Browser) Version

The game can be compiled to WebAssembly and run in any modern web browser using pygbag:

```bash
# Build and serve the web version
uv run pygbag main.py
```

This will:
1. Compile the game to WebAssembly
2. Start a local web server (usually on http://localhost:8080)
3. Open your browser to play the game

The web version includes:
- **Full game functionality** with all power-ups
- **Responsive controls** (mouse and keyboard)
- **Cross-platform compatibility** (works on desktop, mobile, tablets)
- **No installation required** - just open in browser

### Alternative Local Run
```bash
# Run the full-featured version
uv run python -m src.breakout.main

# Or run the simple standalone version
uv run python simple_breakout.py
```

## 🏗️ Project Structure

```
breakout_retro/
├── main.py                 # Web entry point (pygbag compatible)
├── simple_breakout.py      # Standalone simple version
├── pygbag.toml            # Web build configuration
├── pyproject.toml         # Project dependencies
├── src/
│   └── breakout/
│       ├── game.py        # Main game logic
│       ├── entities/      # Game objects
│       │   ├── paddle.py  # Player paddle
│       │   ├── ball.py    # Game ball
│       │   ├── brick.py   # Destructible bricks
│       │   ├── powerup.py # Power-up system
│       │   └── laser.py   # Laser projectiles
│       └── utils/
│           ├── constants.py # Game constants
│           └── helpers.py   # Utility functions
└── build/                 # Generated web files (after pygbag build)
```

## 🎨 Game Mechanics

### Scoring System
- **Basic brick destruction**: 10 points per brick
- **Combo multipliers**: Consecutive hits increase score
- **Power-up collection**: Bonus points for catching power-ups
- **Level completion**: Bonus points for clearing all bricks

### Physics
- **Realistic ball bouncing** with angle variation based on paddle hit position
- **Collision detection** using optimized algorithms
- **Smooth movement** with delta-time based updates
- **Boundary constraints** to keep objects on screen

### Difficulty Progression
- **Ball speed increases** as game progresses
- **Brick layouts** become more challenging
- **Power-up frequency** adjusts with difficulty

## 🌐 Web Deployment

The game is fully compatible with modern web browsers through WebAssembly:

### Supported Browsers
- Chrome/Chromium 80+
- Firefox 79+
- Safari 14+
- Edge 80+

### Performance
- **60 FPS** smooth gameplay
- **Low latency** input handling
- **Optimized rendering** for web performance
- **Mobile-friendly** touch controls

### Hosting
After building with pygbag, the `build/web/` directory contains all files needed for web hosting:
- Upload to any static web host (GitHub Pages, Netlify, Vercel, etc.)
- No server-side processing required
- Works offline after initial load

## 🛠️ Development

### Technology Stack
- **Python 3.13** - Latest Python with performance improvements
- **pygame** - Cross-platform game development
- **pygbag** - WebAssembly compilation for web deployment
- **uv** - Fast Python package management

### Adding New Features
The modular architecture makes it easy to extend:
- Add new power-ups in `entities/powerup.py`
- Modify game physics in `entities/ball.py` and `entities/paddle.py`
- Adjust difficulty in `utils/constants.py`
- Create new brick types in `entities/brick.py`

## 🎵 Audio (Future Enhancement)
The game is structured to support audio features:
- Sound effects for brick destruction, power-up collection, paddle hits
- Background music with retro-style soundtrack
- Audio settings and volume control

## 🐛 Troubleshooting

### Common Issues
1. **Import errors**: Make sure you're in the project directory and dependencies are installed
2. **Web version not loading**: Check browser console for WebAssembly support
3. **Performance issues**: Try closing other browser tabs or applications

### Web-Specific Issues
- **Slow loading**: First load downloads WebAssembly runtime (normal)
- **Controls not working**: Click on the game area to focus
- **Audio not working**: Some browsers require user interaction before playing audio

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional power-ups and game mechanics
- Visual effects and animations
- Sound effects and music
- Mobile touch controls optimization
- Performance optimizations

---

**Enjoy playing Breakout Retro!** 🎮✨
