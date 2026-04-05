#!/usr/bin/env python3
"""Embed assets/icons/*.svg into README row SVGs as data: URIs (Camo-safe)."""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"

TARGETS = [
    "hero-domain-tiles.svg",
    "tech-arsenal-languages.svg",
    "tech-arsenal-backend.svg",
    "tech-arsenal-databases.svg",
    "tech-arsenal-devops-row1.svg",
    "tech-arsenal-devops-row2.svg",
    "tech-arsenal-testing.svg",
]

PATTERN = re.compile(r'href="icons/([^"]+)"\s+xlink:href="icons/[^"]+"')


def to_data_uri(raw: bytes) -> str:
    b64 = base64.standard_b64encode(raw).decode("ascii")
    return f"data:image/svg+xml;base64,{b64}"


def embed_one(svg_path: Path) -> bool:
    text = svg_path.read_text(encoding="utf-8")

    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        icon_path = ICONS / name
        if not icon_path.is_file():
            raise FileNotFoundError(f"Missing icon: {icon_path}")
        uri = to_data_uri(icon_path.read_bytes())
        return f'href="{uri}"'

    new_text, n = PATTERN.subn(repl, text)
    if n == 0:
        return False
    # Drop unused xlink namespace if no xlink:href remains
    if "xlink:href" not in new_text and "xmlns:xlink" in new_text:
        new_text = new_text.replace(
            ' xmlns:xlink="http://www.w3.org/1999/xlink"', "", 1
        )
    svg_path.write_text(new_text, encoding="utf-8")
    print(f"{svg_path.relative_to(ROOT)}: embedded {n} icon(s)")
    return True


def main() -> int:
    if not ICONS.is_dir():
        print("No assets/icons directory", file=sys.stderr)
        return 1
    for name in TARGETS:
        embed_one(ASSETS / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
