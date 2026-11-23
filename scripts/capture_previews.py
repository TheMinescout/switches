#!/usr/bin/env python3
"""Capture animated GIF previews of every switch example.

Uses headless Chromium through Playwright, records the page with the Chrome
DevTools screencast (real rendered frames, no polling), crops to the demo card
and writes a looping GIF to previews/.

    python3 scripts/capture_previews.py            # all switches
    python3 scripts/capture_previews.py --only mm-in-unit-switch  # one switch

Requires: playwright, pillow. Chromium is taken from CHROMIUM_PATH when set,
otherwise /usr/bin/chromium when present, otherwise Playwright's own download.
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import shutil
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PREVIEWS = ROOT / "previews"
VIEWPORT = {"width": 1000, "height": 820}
DEVICE_SCALE = 2
FRAME_MAX_WIDTH = 1400
GIF_WIDTH = 680
PAD = 10

SWITCHES = [
    {
        "slug": "mm-in-unit-switch",
        "steps": [
            ("wait", 700),
            ("click", ".unit-switch__option[data-unit='in']", 900),
            ("click", ".unit-switch__option[data-unit='mm']", 700),
        ],
    },
    {
        "slug": "billing-cycle-switch",
        "steps": [
            ("wait", 700),
            ("click", ".cycle-switch__option[data-cycle='yearly']", 1000),
            ("click", ".cycle-switch__option[data-cycle='monthly']", 700),
        ],
    },
    {
        "slug": "theme-appearance-switch",
        "steps": [
            ("wait", 700),
            ("click", ".theme-switch__option[data-choice='dark']", 900),
            ("click", ".theme-switch__option[data-choice='light']", 800),
            ("click", ".theme-switch__option[data-choice='system']", 700),
        ],
    },
    {
        "slug": "temperature-unit-switch",
        "steps": [
            ("wait", 700),
            ("click", ".temp-switch__option[data-unit='f']", 800),
            ("click", ".sample[data-c='21']", 800),
            ("click", ".sample[data-c='180']", 700),
            ("click", ".temp-switch__option[data-unit='c']", 700),
        ],
    },
    {
        "slug": "currency-unit-switch",
        "steps": [
            ("wait", 700),
            ("click", ".currency-switch__option[data-currency='eur']", 900),
            ("click", ".currency-switch__option[data-currency='gbp']", 900),
            ("click", ".currency-switch__option[data-currency='usd']", 700),
        ],
    },
    {
        "slug": "weight-unit-switch",
        "steps": [
            ("wait", 700),
            ("click", ".weight-switch__option[data-unit='oz']", 900),
            ("click", ".weight-switch__option[data-unit='g']", 700),
        ],
    },
    {
        "slug": "notification-cadence-switch",
        "steps": [
            ("wait", 700),
            ("click", ".cadence-switch__option[data-cadence='daily']", 900),
            ("click", ".cadence-switch__option[data-cadence='off']", 900),
            ("click", ".cadence-switch__option[data-cadence='instant']", 700),
        ],
    },
    {
        "slug": "privacy-consent-switch",
        "steps": [
            ("wait", 700),
            ("click", ".consent-switch__option[data-consent='analytics']", 900),
            ("click", ".consent-switch__option[data-consent='essential']", 700),
        ],
    },
    {
        "slug": "availability-status-switch",
        "steps": [
            ("wait", 700),
            ("click", ".status-switch__option[data-status='booked']", 900),
            ("click", ".status-switch__option[data-status='available']", 700),
        ],
    },
    {
        "slug": "view-density-switch",
        "steps": [
            ("wait", 700),
            ("click", ".density-switch__option[data-density='compact']", 900),
            ("click", ".density-switch__option[data-density='comfortable']", 700),
        ],
    },
]


def chromium_path() -> str | None:
    explicit = os.environ.get("CHROMIUM_PATH")
    if explicit:
        return explicit
    for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome"):
        if Path(candidate).exists():
            return candidate
    return None


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):  # keep the capture output clean
        pass


def serve(directory: Path, port: int) -> ThreadingHTTPServer:
    handler = partial(QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def crop_box(page, selector: str) -> tuple[int, int, int, int]:
    page.locator(selector).scroll_into_view_if_needed()
    page.wait_for_timeout(150)
    box = page.locator(selector).bounding_box()
    if box is None:
        raise RuntimeError(f"{selector} has no bounding box")
    left = max(0, int(box["x"] - PAD))
    top = max(0, int(box["y"] - PAD))
    right = min(VIEWPORT["width"], int(box["x"] + box["width"] + PAD))
    bottom = min(VIEWPORT["height"], int(box["y"] + box["height"] + PAD))
    return left, top, right, bottom


def record(page, steps) -> tuple[list[Image.Image], list[float]]:
    frames: list[tuple[float, bytes]] = []
    cdp = page.context.new_cdp_session(page)

    def on_frame(params):
        frames.append((params["metadata"]["timestamp"], params["data"]))
        cdp.send("Page.screencastFrameAck", {"sessionId": params["sessionId"]})

    cdp.on("Page.screencastFrame", on_frame)
    cdp.send(
        "Page.startScreencast",
        {
            "format": "png",
            "everyNthFrame": 1,
            "maxWidth": FRAME_MAX_WIDTH,
            "maxHeight": VIEWPORT["height"] * DEVICE_SCALE,
        },
    )

    for step in steps:
        kind = step[0]
        if kind == "wait":
            page.wait_for_timeout(step[1])
        elif kind == "click":
            page.evaluate(
                """selector => {
                    const el = document.querySelector(selector);
                    if (!el) throw new Error('missing ' + selector);
                    el.click();
                }""",
                step[1],
            )
            page.wait_for_timeout(step[2])
        else:
            raise ValueError(f"unknown step {kind}")

    cdp.send("Page.stopScreencast")

    images: list[Image.Image] = []
    durations: list[float] = []
    for i, (timestamp, data) in enumerate(frames):
        image = Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")
        images.append(image)
        if i + 1 < len(frames):
            delta = frames[i + 1][0] - timestamp
            durations.append(min(0.2, max(0.03, delta)))
        else:
            durations.append(1.2)
    return images, durations


def build_gif(images, durations, box, out_path: Path) -> None:
    frame_w, frame_h = images[0].size
    scale = frame_w / VIEWPORT["width"]
    left, top, right, bottom = (int(v * scale) for v in box)

    # Sample at roughly 20 fps: keep the first frame, then every other frame,
    # carrying over the skipped frame's duration so playback speed is unchanged.
    kept = []
    for i in range(0, len(images), 2):
        kept.append((images[i], sum(durations[i:i + 2])))

    target_h = round((bottom - top) * GIF_WIDTH / (right - left))
    rendered = []
    for image, _ in kept:
        cropped = image.crop((left, top, right, bottom)).resize((GIF_WIDTH, target_h), Image.LANCZOS)
        rendered.append(cropped.convert("P", palette=Image.Palette.ADAPTIVE, colors=96, dither=Image.Dither.NONE))

    out_durations = [round(duration * 1000) for _, duration in kept]
    out_durations = [max(30, min(200, d)) for d in out_durations]
    out_durations[-1] = 1400

    out_path.parent.mkdir(parents=True, exist_ok=True)
    rendered[0].save(
        out_path,
        save_all=True,
        append_images=rendered[1:],
        duration=out_durations,
        loop=0,
        optimize=True,
        disposal=2,
    )


def capture(page, config, port: int) -> None:
    page.goto(f"http://127.0.0.1:{port}/{config['slug']}/example.html", wait_until="load")
    page.wait_for_timeout(500)
    box = crop_box(page, "[data-preview]")
    images, durations = record(page, config["steps"])
    out = PREVIEWS / f"{config['slug']}.gif"
    build_gif(images, durations, box, out)
    size_kb = out.stat().st_size / 1024
    print(f"{out.relative_to(ROOT)}  {len(images)} frames  {size_kb:.0f} KB")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="capture only this switch slug")
    args = parser.parse_args()

    if shutil.which("python3") is None:
        print("python3 is required", file=sys.stderr)
        return 1

    server = serve(ROOT, 0)
    port = server.server_address[1]
    executable = chromium_path()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=executable,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--force-color-profile=srgb"],
            )
            context = browser.new_context(
                viewport=VIEWPORT,
                device_scale_factor=DEVICE_SCALE,
                color_scheme="light",
                reduced_motion="no-preference",
            )
            for config in SWITCHES:
                if args.only and config["slug"] != args.only:
                    continue
                page = context.new_page()
                capture(page, config, port)
                page.close()
            browser.close()
    finally:
        server.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
