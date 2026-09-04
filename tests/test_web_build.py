"""Protect pygbag's embedded runtime when preparing the published HTML."""

import ast
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

from scripts.prepare_web import DESCRIPTION, SITE_URL, TITLE, favicon_png, prepare_html, prepare_web


BOOTSTRAP = '''<script type=module id=site src="pythons.js">#<!--
async def custom_site():
    markup = '<title>keep this</title><div id=transfer>'
    await shell.source(main)
asyncio.run(custom_site())
# --></script>'''
PRERUN = '<script>function custom_prerun() { console.log("custom_prerun"); }</script>'
PAGE = f'''<html>{BOOTSTRAP}<head>
<title>breakout</title><meta name=description content="old">
<link href="old.ico" rel="shortcut icon"><link rel=canonical href="https://old.test/">
<meta property="og:title" content="old">
<script>const markup = '<div id="transfer">';</script>
</head><body>
<div id="transfer">Downloading...</div><canvas id=canvas></canvas>
<div id=crt><button>RESET</button></div><div id='infobox'>Loading</div>
<div id=html></div><div id=dlg></div><div id=pyconsole data-nosnippet></div>
{PRERUN}
</body></html>'''


class WebBuildTests(unittest.TestCase):
    def test_entry_point_declares_pygame_for_browser_preloading(self):
        # Pygbag scans main.py for dependencies before importing local modules.
        entry_point = Path(__file__).resolve().parents[1] / "main.py"
        module = ast.parse(entry_point.read_text(encoding="utf-8"))
        imports_pygame = any(
            isinstance(statement, ast.Import)
            and any(alias.name == "pygame" for alias in statement.names)
            for statement in module.body
        )
        self.assertTrue(imports_pygame, "Keep a direct top-level pygame import in main.py")

    def test_metadata_preserves_runtime_and_is_idempotent(self):
        output = prepare_html(PAGE)
        self.assertIn(BOOTSTRAP, output)
        self.assertIn("<script>const markup = '<div id=\"transfer\">';</script>", output)
        self.assertIn(f"<title>{TITLE}</title>", output)
        self.assertIn(f'<meta name="description" content="{DESCRIPTION}">', output)
        self.assertIn(f'<link rel="canonical" href="{SITE_URL}">', output)
        self.assertNotIn('href="old.ico"', output)
        self.assertNotIn('content="old"', output)
        self.assertIn('<div id="transfer" data-nosnippet>', output)
        self.assertIn("<div id=crt data-nosnippet>", output)
        self.assertIn("<div id='infobox' data-nosnippet>", output)
        self.assertIn("<h1>Breakout Retro</h1>", output)
        self.assertIn(PRERUN, output)
        self.assertGreater(output.index("const loadingInfo"), output.index(PRERUN))
        self.assertIn('document.getElementById("infobox")', output)
        self.assertIn("if (!loadingInfo) return", output)
        self.assertIn('if (loadingInfo.style.display !== "none") return', output)
        self.assertIn("new MutationObserver(restoreViewport)", output)
        self.assertIn('attributeFilter: ["style"]', output)
        self.assertIn("window.scrollTo(0, 0)", output)
        self.assertIn("observer.disconnect()", output)
        self.assertEqual(prepare_html(output), output)

    def test_invalid_build_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            index = directory / "index.html"
            original = "<html><body>Not a game build</body></html>"
            index.write_text(original)
            with self.assertRaises(ValueError):
                prepare_web(directory)
            self.assertEqual(index.read_text(), original)
            self.assertFalse((directory / "favicon.png").exists())
            self.assertFalse((directory / "_headers").exists())

    def test_generated_build_revalidates_assets_after_deployment(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            (directory / "index.html").write_text(PAGE, encoding="utf-8")
            prepare_web(directory)
            headers = directory / "_headers"
            self.assertEqual(headers.read_text(encoding="utf-8"), "/*\n  Cache-Control: no-cache\n")
            first_build = {path.name: path.read_bytes() for path in directory.iterdir()}
            prepare_web(directory)
            self.assertEqual(
                {path.name: path.read_bytes() for path in directory.iterdir()},
                first_build,
            )

    def test_favicon_is_a_valid_square_png(self):
        icon = favicon_png()
        self.assertEqual(icon[:8], b"\x89PNG\r\n\x1a\n")
        offset = 8
        image_data = bytearray()
        while offset < len(icon):
            length = struct.unpack(">I", icon[offset:offset + 4])[0]
            kind = icon[offset + 4:offset + 8]
            data = icon[offset + 8:offset + 8 + length]
            crc = struct.unpack(">I", icon[offset + 8 + length:offset + 12 + length])[0]
            self.assertEqual(crc, zlib.crc32(kind + data))
            if kind == b"IHDR":
                self.assertEqual(struct.unpack(">IIBBBBB", data), (96, 96, 8, 2, 0, 0, 0))
            elif kind == b"IDAT":
                image_data.extend(data)
            offset += length + 12
        self.assertEqual(len(zlib.decompress(image_data)), 96 * (1 + 96 * 3))


if __name__ == "__main__":
    unittest.main()
