"""End-to-end checks for the switch collection.

Run with:

    python3 -m unittest discover -s tests -v

The suite starts a local static server, drives every page in headless Chromium at
desktop and mobile sizes, and asserts that the switches actually work: no console
errors, no horizontal overflow, correct conversions, persistence and previews.
"""

from __future__ import annotations

import os
import re
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent

SWITCHES = [
    "mm-in-unit-switch",
    "billing-cycle-switch",
    "theme-appearance-switch",
    "temperature-unit-switch",
]

VIEWPORTS = [
    ("desktop", 1280, 800),
    ("mobile", 390, 844),
    ("small", 320, 640),
]

CHROMIUM_CANDIDATES = [
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
]


def chromium_executable():
    explicit = os.environ.get("CHROMIUM_PATH")
    if explicit:
        return explicit
    for candidate in CHROMIUM_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class SwitchCollectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = partial(QuietHandler, directory=str(ROOT))
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.port = cls.server.server_address[1]
        cls.base = f"http://127.0.0.1:{cls.port}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            executable_path=chromium_executable(),
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 800})
        self.page = self.context.new_page()
        self.console_errors = []
        self.page_errors = []
        self.page.on("console", self._on_console)
        self.page.on("pageerror", self._on_page_error)

    def tearDown(self):
        self.context.close()

    def _on_console(self, message):
        if message.type == "error":
            self.console_errors.append(message.text)

    def _on_page_error(self, error):
        self.page_errors.append(str(error))

    def open(self, path: str, wait: int = 500):
        response = self.page.goto(f"{self.base}/{path}", wait_until="load")
        self.assertIsNotNone(response, f"no response for {path}")
        self.assertEqual(response.status, 200, f"{path} returned {response.status}")
        self.page.wait_for_timeout(wait)
        return response

    def assert_clean(self, label: str):
        self.assertEqual(self.console_errors, [], f"console errors on {label}")
        self.assertEqual(self.page_errors, [], f"page errors on {label}")
        overflow = self.page.evaluate(
            "() => document.documentElement.scrollWidth - document.documentElement.clientWidth"
        )
        self.assertLessEqual(overflow, 1, f"horizontal overflow on {label}: {overflow}px")

    # --- Structure -------------------------------------------------------

    def test_every_switch_folder_has_example_and_guide(self):
        for slug in SWITCHES:
            with self.subTest(slug=slug):
                folder = ROOT / slug
                self.assertTrue(folder.is_dir(), f"{slug} folder is missing")
                example = folder / "example.html"
                guide = folder / "how-to-add.md"
                self.assertTrue(example.is_file(), f"{example} is missing")
                self.assertTrue(guide.is_file(), f"{guide} is missing")
                self.assertGreater(example.stat().st_size, 4000, f"{example} looks empty")
                self.assertGreater(guide.stat().st_size, 2000, f"{guide} looks empty")
                example_text = example.read_text()
                self.assertIn("<!doctype html>", example_text.lower())
                self.assertIn("viewport", example_text)
                self.assertNotIn("<script src=", example_text, "examples must not load external scripts")
                self.assertNotIn("cdn.", example_text, "examples must not load a CDN")

    def test_examples_render_cleanly_on_desktop_and_mobile(self):
        pages = ["index.html"] + [f"{slug}/example.html" for slug in SWITCHES]
        for path in pages:
            for name, width, height in VIEWPORTS:
                with self.subTest(page=path, viewport=name):
                    self.page.set_viewport_size({"width": width, "height": height})
                    self.console_errors.clear()
                    self.page_errors.clear()
                    self.open(path)
                    self.assert_clean(f"{path} at {name}")
                    self.assertGreater(len(self.page.title()), 3)
                    body_text = self.page.locator("body").inner_text().strip()
                    self.assertGreater(len(body_text), 80, f"page looks blank: {path}")

    def test_index_embeds_every_example_and_credits_studio(self):
        self.open("index.html", wait=1200)
        html = self.page.content()
        iframes = self.page.locator("iframe")
        self.assertEqual(iframes.count(), len(SWITCHES))
        for slug in SWITCHES:
            with self.subTest(slug=slug):
                self.assertIn(f'src="{slug}/example.html', html)
                link = self.page.locator(f'a[href="{slug}/example.html"]')
                self.assertGreaterEqual(link.count(), 1, f"no live-demo link for {slug}")
                guide = self.page.locator(f'a[href="{slug}/how-to-add.md"]')
                self.assertGreaterEqual(guide.count(), 1, f"no how-to-add link for {slug}")
        self.assertIn("https://minescout.net/studio", html)
        self.assert_clean("index.html")

    def test_index_iframes_load_without_errors(self):
        self.open("index.html", wait=500)
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        self.page.wait_for_timeout(1500)
        frame_urls = [frame.url for frame in self.page.frames if frame.url.startswith("http")]
        for slug in SWITCHES:
            with self.subTest(slug=slug):
                self.assertTrue(
                    any(f"/{slug}/example.html" in url for url in frame_urls),
                    f"iframe for {slug} did not load: {frame_urls}",
                )
        self.assert_clean("index.html with iframes")

    # --- mm | in ---------------------------------------------------------

    def test_mm_switch_converts_and_persists(self):
        self.open("mm-in-unit-switch/example.html")
        values = self.page.locator(".num")
        self.assertEqual(values.nth(0).inner_text(), "256")

        self.page.locator(".unit-switch__option[data-unit='in']").click()
        self.page.wait_for_timeout(450)

        self.assertEqual(values.nth(0).inner_text(), "10.08")
        self.assertEqual(values.nth(3).inner_text(), "0.02")
        self.assertEqual(self.page.locator(".unit").first.inner_text(), "in")
        self.assertEqual(
            self.page.locator(".unit-switch__option[data-unit='in']").get_attribute("aria-pressed"),
            "true",
        )
        self.assertEqual(
            self.page.locator(".unit-switch__option[data-unit='mm']").get_attribute("aria-pressed"),
            "false",
        )
        self.assertEqual(self.page.locator("#custom-unit").inner_text(), "in")
        self.assertIn("mm", self.page.locator("#custom-out").inner_text())

        stored = self.page.evaluate("localStorage.getItem('mm-in-unit-switch')")
        self.assertEqual(stored, "in")

        self.page.reload(wait_until="load")
        self.page.wait_for_timeout(300)
        self.assertEqual(self.page.locator(".num").nth(0).inner_text(), "10.08")

        self.page.locator(".unit-switch__option[data-unit='mm']").click()
        self.page.wait_for_timeout(400)
        self.assertEqual(self.page.locator(".num").nth(0).inner_text(), "256")
        self.assert_clean("mm-in-unit-switch")

    def test_mm_switch_keyboard_and_custom_input(self):
        self.open("mm-in-unit-switch/example.html")
        self.page.locator(".unit-switch__option[data-unit='mm']").focus()
        self.page.keyboard.press("ArrowRight")
        self.page.wait_for_timeout(350)
        self.assertEqual(self.page.locator(".num").nth(0).inner_text(), "10.08")

        self.page.locator("#custom-length").fill("2")
        self.page.wait_for_timeout(200)
        self.assertIn("50.8", self.page.locator("#custom-out").inner_text())
        self.assertIn("mm", self.page.locator("#custom-out").inner_text())
        self.assert_clean("mm-in-unit-switch keyboard")

    # --- Billing ---------------------------------------------------------

    def test_billing_switch_updates_prices(self):
        self.open("billing-cycle-switch/example.html")
        amounts = self.page.locator(".amount")
        self.assertEqual([amounts.nth(i).inner_text() for i in range(3)], ["9", "29", "79"])

        self.page.locator(".cycle-switch__option[data-cycle='yearly']").click()
        self.page.wait_for_timeout(450)

        self.assertEqual([amounts.nth(i).inner_text() for i in range(3)], ["7.20", "23.20", "63.20"])
        notes = self.page.locator(".billing-note")
        self.assertTrue(notes.nth(0).is_visible())
        self.assertIn("$86.40", notes.nth(0).inner_text())
        self.assertIn("$758.40", notes.nth(2).inner_text())
        self.assertIn("Billed yearly", self.page.locator("#summary-text").inner_text())
        self.assertEqual(
            self.page.locator(".cycle-switch").get_attribute("data-cycle"), "yearly"
        )

        self.page.locator(".cycle-switch__option[data-cycle='monthly']").click()
        self.page.wait_for_timeout(400)
        self.assertEqual([amounts.nth(i).inner_text() for i in range(3)], ["9", "29", "79"])
        self.assertFalse(notes.nth(0).is_visible())
        self.assert_clean("billing-cycle-switch")

    # --- Theme -----------------------------------------------------------

    def test_theme_switch_applies_and_persists(self):
        self.open("theme-appearance-switch/example.html")
        self.page.evaluate("localStorage.clear()")
        self.page.reload(wait_until="load")
        self.page.wait_for_timeout(300)

        self.page.locator(".theme-switch__option[data-choice='dark']").click()
        self.page.wait_for_timeout(400)

        self.assertEqual(self.page.evaluate("document.documentElement.dataset.theme"), "dark")
        self.assertEqual(self.page.evaluate("document.documentElement.dataset.choice"), "dark")
        self.assertEqual(self.page.evaluate("localStorage.getItem('theme-appearance-switch')"), "dark")
        self.assertEqual(
            self.page.locator(".theme-switch__option[data-choice='dark']").get_attribute("aria-pressed"),
            "true",
        )
        dark_surface = self.page.evaluate(
            "getComputedStyle(document.querySelector('[data-preview]')).backgroundColor"
        )
        self.assertEqual(dark_surface, "rgb(28, 25, 23)")

        self.page.reload(wait_until="load")
        self.page.wait_for_timeout(300)
        self.assertEqual(self.page.evaluate("document.documentElement.dataset.theme"), "dark")

        self.page.locator(".theme-switch__option[data-choice='system']").click()
        self.page.wait_for_timeout(400)
        self.assertEqual(self.page.evaluate("document.documentElement.dataset.choice"), "system")
        self.assertIn(
            self.page.evaluate("document.documentElement.dataset.theme"), ("light", "dark")
        )
        self.assert_clean("theme-appearance-switch")

    # --- Temperature -----------------------------------------------------

    def test_temperature_switch_converts_readout_and_samples(self):
        self.open("temperature-unit-switch/example.html")
        self.assertEqual(self.page.locator("#readout-value").inner_text(), "180")
        self.assertEqual(self.page.locator("#readout-unit").inner_text(), "°C")

        self.page.locator(".temp-switch__option[data-unit='f']").click()
        self.page.wait_for_timeout(450)
        self.assertEqual(self.page.locator("#readout-value").inner_text(), "356")
        self.assertEqual(self.page.locator("#readout-unit").inner_text(), "°F")
        self.assertIn("180", self.page.locator("#readout-alt").inner_text())
        self.assertIn("-4", self.page.locator("#scale-min").inner_text())
        self.assertIn("482", self.page.locator("#scale-max").inner_text())

        self.page.locator(".sample[data-c='21']").click()
        self.page.wait_for_timeout(350)
        self.assertEqual(self.page.locator("#readout-value").inner_text(), "69.8")
        self.assertEqual(self.page.evaluate("document.getElementById('slider').value"), "21")

        self.page.locator(".temp-switch__option[data-unit='c']").click()
        self.page.wait_for_timeout(350)
        self.assertEqual(self.page.locator("#readout-value").inner_text(), "21")
        self.assertEqual(self.page.locator("#readout-unit").inner_text(), "°C")
        self.assert_clean("temperature-unit-switch")

    def test_temperature_slider_updates_readout(self):
        self.open("temperature-unit-switch/example.html")
        self.page.evaluate(
            """() => {
                const slider = document.getElementById('slider');
                slider.value = '100';
                slider.dispatchEvent(new Event('input', { bubbles: true }));
            }"""
        )
        self.page.wait_for_timeout(300)
        self.assertEqual(self.page.locator("#readout-value").inner_text(), "100")
        self.assertIn("212", self.page.locator("#readout-alt").inner_text())
        self.assert_clean("temperature-unit-switch slider")

    # --- Previews --------------------------------------------------------

    def test_previews_exist_and_are_animated(self):
        for slug in SWITCHES:
            with self.subTest(slug=slug):
                gif = ROOT / "previews" / f"{slug}.gif"
                self.assertTrue(gif.is_file(), f"missing preview {gif}")
                self.assertGreater(gif.stat().st_size, 20_000, f"{gif} is suspiciously small")
                with Image.open(gif) as image:
                    self.assertEqual(image.format, "GIF")
                    self.assertGreaterEqual(image.n_frames, 8, f"{gif} has too few frames")
                    self.assertGreaterEqual(image.size[0], 600, f"{gif} is too narrow")
                    self.assertGreater(image.size[1], 200)

    def test_how_to_add_snippets_work(self):
        """The copy-paste snippets in each guide must run on their own."""
        markers = {
            "mm-in-unit-switch": "unit-switch",
            "billing-cycle-switch": "cycle-switch",
            "theme-appearance-switch": "theme-switch",
            "temperature-unit-switch": "temp-switch",
        }
        checks = {
            "mm-in-unit-switch": (
                ".unit-switch__option[data-unit='in']",
                lambda page: self.assertEqual(page.locator(".num").first.inner_text(), "10.08"),
            ),
            "billing-cycle-switch": (
                ".cycle-switch__option[data-cycle='yearly']",
                lambda page: self.assertEqual(page.locator(".amount").first.inner_text(), "7.20"),
            ),
            "theme-appearance-switch": (
                ".theme-switch__option[data-choice='dark']",
                lambda page: self.assertEqual(
                    page.evaluate("document.documentElement.dataset.theme"), "dark"
                ),
            ),
            "temperature-unit-switch": (
                ".temp-switch__option[data-unit='f']",
                lambda page: self.assertEqual(page.locator("#readout-value").inner_text(), "356"),
            ),
        }

        for slug, marker in markers.items():
            with self.subTest(slug=slug):
                doc = (ROOT / slug / "how-to-add.md").read_text()
                blocks = re.findall(r"```(\w*)\n(.*?)```", doc, re.S)
                css = "\n".join(body for lang, body in blocks if lang == "css")
                html_blocks = [body for lang, body in blocks if lang == "html"]
                markup = next(body for body in html_blocks if marker in body and "addEventListener" not in body)
                script = max(
                    (body for body in html_blocks if "addEventListener" in body),
                    key=len,
                )

                page = self.context.new_page()
                errors = []
                page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.goto(f"{self.base}/index.html", wait_until="load")
                page.set_content(
                    "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
                    f"<style>{css}</style></head><body>{markup}{script}</body></html>"
                )
                page.wait_for_timeout(300)
                page.locator(checks[slug][0]).click()
                page.wait_for_timeout(400)
                checks[slug][1](page)
                self.assertEqual(errors, [], f"errors from the {slug} guide snippet")
                page.close()

    def test_readme_links_examples_guides_and_previews(self):
        readme = (ROOT / "README.md").read_text()
        for slug in SWITCHES:
            with self.subTest(slug=slug):
                self.assertIn(f"{slug}/example.html", readme)
                self.assertIn(f"{slug}/how-to-add.md", readme)
                self.assertIn(f"previews/{slug}.gif", readme)
                self.assertIn(
                    f"https://theminescout.github.io/switches/{slug}/example.html", readme
                )
        self.assertIn("minescout.net/studio", readme)


if __name__ == "__main__":
    unittest.main(verbosity=2)
