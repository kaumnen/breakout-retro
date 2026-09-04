"""Add page metadata and a game icon to pygbag's generated web build."""

import argparse
import re
import struct
import zlib
from html.parser import HTMLParser
from pathlib import Path


TITLE = "Breakout Retro | Play Online"
DESCRIPTION = (
    "Play Breakout Retro, a browser arcade game with multiball, lasers "
    "and paddle power-ups."
)
SITE_URL = "https://breakout.kaumnen.com/"
RUNTIME_IDS = {"transfer", "crt", "dlg", "pyconsole", "html", "infobox"}

HEAD = f'''<!-- breakout:head -->
    <title>{TITLE}</title>
    <meta name="description" content="{DESCRIPTION}">
    <link rel="canonical" href="{SITE_URL}">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Breakout Retro">
    <meta property="og:title" content="{TITLE}">
    <meta property="og:description" content="{DESCRIPTION}">
    <meta property="og:url" content="{SITE_URL}">
    <meta name="theme-color" content="#0b1020">
    <link rel="icon" type="image/png" href="favicon.png" sizes="96x96">
    <style>
        body {{ background: #0b1020 !important; }}
        #game-info {{
            position: absolute;
            top: 100vh;
            left: 0;
            right: 0;
            box-sizing: border-box;
            padding: 24px;
            background: #0b1020;
            color: #c6d2e8;
            font: 14px/1.6 system-ui, sans-serif;
            text-align: center;
        }}
        #game-info h1 {{ margin: 0 0 8px; color: #f2f6ff; font-size: 20px; }}
        #game-info p {{ margin: 4px auto; max-width: 60em; }}
    </style>
<!-- /breakout:head -->
'''

BODY = f'''<!-- breakout:body -->
    <footer id="game-info">
        <h1>Breakout Retro</h1>
        <p>{DESCRIPTION}</p>
        <p>Move with the mouse, arrow keys, or A and D. Press Space or click to start. Press Escape to pause.</p>
        <noscript>Enable JavaScript to play in your browser.</noscript>
    </footer>
    <script>
        (() => {{
            const loadingInfo = document.getElementById("infobox");
            if (!loadingInfo) return;
            const restoreViewport = () => {{
                if (loadingInfo.style.display !== "none") return;
                // Pygbag scrolls down during startup to hide mobile browser chrome.
                // The loading message is hidden after the game has started.
                window.scrollTo(0, 0);
                observer.disconnect();
            }};
            const observer = new MutationObserver(restoreViewport);
            observer.observe(loadingInfo, {{ attributes: true, attributeFilter: ["style"] }});
            restoreViewport();
        }})();
    </script>
<!-- /breakout:body -->
'''


class PageEdits(HTMLParser):
    """Collect source edits without reserializing pygbag's embedded Python."""

    def __init__(self, source):
        super().__init__(convert_charrefs=False)
        self.source = source
        self.line_offsets = [0]
        self.line_offsets.extend(match.end() for match in re.finditer("\n", source))
        self.edits = []
        self.in_head = False
        self.title_start = None
        self.head_end = None
        self.body_end = None
        self.has_canvas = False

    def source_offset(self):
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        start = self.source_offset()
        raw = self.get_starttag_text()
        end = start + len(raw)
        if tag == "head":
            self.in_head = True
        elif tag == "title" and self.in_head:
            self.title_start = start
        elif self.in_head and tag == "meta":
            name = (attributes.get("name") or "").lower()
            prop = (attributes.get("property") or "").lower()
            if name in {"description", "theme-color"} or prop.startswith("og:"):
                self.edits.append((start, end, ""))
        elif self.in_head and tag == "link":
            relations = (attributes.get("rel") or "").lower().split()
            if "canonical" in relations or "icon" in relations:
                self.edits.append((start, end, ""))

        element_id = attributes.get("id")
        if tag == "canvas" and element_id == "canvas":
            self.has_canvas = True
        if tag == "div" and element_id in RUNTIME_IDS and "data-nosnippet" not in attributes:
            closing = 2 if raw.endswith("/>") else 1
            updated = raw[:-closing] + " data-nosnippet" + raw[-closing:]
            self.edits.append((start, end, updated))

    def handle_endtag(self, tag):
        start = self.source_offset()
        if tag == "title" and self.in_head and self.title_start is not None:
            end = self.source.index(">", start) + 1
            self.edits.append((self.title_start, end, ""))
            self.title_start = None
        elif tag == "head":
            self.in_head = False
            self.head_end = start
        elif tag == "body":
            self.body_end = start


def prepare_html(source):
    # Remove only our own blocks so repeated runs produce identical output.
    for section in ("head", "body"):
        source = re.sub(
            rf"<!-- breakout:{section} -->.*?<!-- /breakout:{section} -->\n?",
            "",
            source,
            flags=re.DOTALL,
        )
    page = PageEdits(source)
    page.feed(source)
    page.close()
    if page.head_end is None or page.body_end is None or not page.has_canvas:
        raise ValueError("Expected a pygbag page with a head, body, and game canvas")
    page.edits.extend(((page.head_end, page.head_end, HEAD), (page.body_end, page.body_end, BODY)))
    for start, end, replacement in sorted(page.edits, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source


def favicon_png():
    """Draw a 96px brick, ball, and paddle icon without image dependencies."""
    size = 96
    rows = []
    for y in range(size):
        row = bytearray([0])  # PNG filter: none.
        for x in range(size):
            color = (11, 16, 32)
            for top, brick_color in ((18, (255, 108, 140)), (35, (157, 127, 255))):
                if top <= y < top + 12 and any(left <= x < left + 20 for left in (14, 38, 62)):
                    color = brick_color
            if (x - 55) ** 2 + (y - 63) ** 2 <= 6 ** 2:
                color = (242, 246, 255)
            if 28 <= x < 68 and 79 <= y < 86:
                color = (74, 223, 230)
            row.extend(color)
        rows.append(row)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b"")


def prepare_web(directory):
    index = directory / "index.html"
    html = prepare_html(index.read_text(encoding="utf-8"))
    icon = favicon_png()
    index.write_text(html, encoding="utf-8")
    (directory / "favicon.png").write_bytes(icon)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=Path("build/web"))
    args = parser.parse_args()
    prepare_web(args.directory)
    print(f"Prepared {args.directory}/index.html and favicon.png")
