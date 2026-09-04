"""Build the browser game and add its public page metadata."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys

from prepare_web import prepare_web


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="Serve the build on 127.0.0.1:8000")
    args = parser.parse_args()

    subprocess.run(
        [sys.executable, "-m", "pygbag", "--build", "--title", "Breakout Retro",
         "--width", "800", "--height", "600", "--ume_block", "0", "main.py"],
        cwd=ROOT,
        check=True,
    )
    output = ROOT / "build" / "web"
    prepare_web(output)
    print(f"Web build ready: {output}")

    if args.serve:
        handler = partial(SimpleHTTPRequestHandler, directory=str(output))
        with ThreadingHTTPServer(("127.0.0.1", 8000), handler) as server:
            # Pygbag treats 'localhost' as a CDN proxy; the numeric address avoids that mode.
            print("Play at http://127.0.0.1:8000. Press Ctrl+C to stop.")
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
