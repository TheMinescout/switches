#!/usr/bin/env python3
"""Regenerate the switch table and Switch Finder quiz in README.md.

``switches.json`` is the single source of truth. Edit it, then run:

    python3 scripts/sync_readme.py

The script only rewrites the regions between the AUTO-GENERATED markers, so
hand-written prose and per-switch sections stay untouched. Use ``--check`` in CI
or tests to fail when README.md is stale.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
MANIFEST = ROOT / "switches.json"

TABLE = "SWITCH-TABLE"
FINDER = "SWITCH-FINDER"


def load_manifest(path: Path = MANIFEST) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def cell(value: str) -> str:
    """Escape text that would break a Markdown table cell."""
    return value.replace("|", "&vert;").replace("\n", " ").strip()


def category_labels(data: dict) -> dict[str, str]:
    return {item["id"]: item["label"] for item in data["categories"]}


def render_table(data: dict) -> str:
    labels = category_labels(data)
    lines = [
        "<!-- AUTO-GENERATED -->",
        "| # | Switch | Category | What it does |",
        "| - | ------ | -------- | ------------ |",
    ]
    for switch in data["switches"]:
        name = cell(switch["name"])
        summary = cell(switch["summary"])
        category = cell(labels.get(switch["category"], switch["category"]))
        lines.append(
            f"| {switch['number']} | [{name}]({switch['slug']}/example.html) "
            f"| {category} | {summary} |"
        )
    return "\n".join(lines) + "\n"


def render_leaf(switch: dict, site: dict) -> list[str]:
    return [
        f"**{switch['name']}** — {switch['summary']}",
        "",
        f"- [Jump to the animated preview](#{switch['anchor']})",
        f"- [How to add it]({switch['slug']}/how-to-add.md)",
        f"- [Live demo]({site['demo_base']}/{switch['slug']}/example.html)",
        "",
    ]


def render_finder(data: dict) -> str:
    site = data["site"]
    labels = category_labels(data)
    lines: list[str] = [
        "<!-- AUTO-GENERATED -->",
        "> **Don't see the switch you need? "
        f"[Request a new switch]({site['request_url']}).**",
        "",
        "Prefer a flat list? Jump to the [switch library](#switch-library).",
        "",
        "**Step 1 — What do you need to switch?** Open the category that matches.",
        "",
    ]

    for category in data["categories"]:
        members = [s for s in data["switches"] if s["category"] == category["id"]]
        if not members:
            continue
        lines.append("<details>")
        lines.append(f"<summary><strong>{category['label']}</strong></summary>")
        lines.append("")
        lines.append("**Step 2 — How many options?** Choose the shape that matches.")
        lines.append("")

        for count in sorted({s["options"] for s in members}):
            group = [s for s in members if s["options"] == count]
            lines.append("<details>")
            lines.append(f"<summary>{count} options</summary>")
            lines.append("")
            if len(group) == 1:
                lines.extend(render_leaf(group[0], site))
            else:
                lines.append("**Step 3 — Which one fits?** Pick the closest match.")
                lines.append("")
                for switch in group:
                    detail = switch.get("quiz", {}).get("detail", switch["name"])
                    lines.append("<details>")
                    lines.append(f"<summary>{detail}</summary>")
                    lines.append("")
                    lines.extend(render_leaf(switch, site))
                    lines.append("</details>")
                    lines.append("")
            lines.append("</details>")
            lines.append("")

        lines.append("</details>")
        lines.append("")

    lines.append(
        "> **Still not sure? "
        f"[Request a new switch]({site['request_url']}) and describe what it should toggle.**"
    )
    return "\n".join(lines) + "\n"


def replace_block(text: str, name: str, content: str) -> str:
    start = f"<!-- AUTO-GENERATED:{name} START -->"
    end = f"<!-- AUTO-GENERATED:{name} END -->"
    begin = text.find(start)
    finish = text.find(end)
    if begin == -1 or finish == -1 or finish < begin:
        raise SystemExit(f"README.md is missing the {name} AUTO-GENERATED markers")
    return text[: begin + len(start)] + "\n" + content + text[finish:]


def build_readme(text: str, data: dict) -> str:
    text = replace_block(text, TABLE, render_table(data))
    text = replace_block(text, FINDER, render_finder(data))
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero when README.md does not match switches.json",
    )
    args = parser.parse_args(argv)

    data = load_manifest()
    current = README.read_text(encoding="utf-8")
    updated = build_readme(current, data)

    if args.check:
        if current != updated:
            print(
                "README.md is out of sync with switches.json. "
                "Run: python3 scripts/sync_readme.py",
                file=sys.stderr,
            )
            return 1
        print("README.md is in sync with switches.json.")
        return 0

    if current == updated:
        print("README.md is already up to date.")
        return 0

    README.write_text(updated, encoding="utf-8")
    print("Updated README.md from switches.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
