#!/usr/bin/env python3
"""Inject or verify the universal bilingual programme navigation fragment."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

START = "<!-- program-matematika-navigation:start -->"
END = "<!-- program-matematika-navigation:end -->"
BLOCK_RE = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
BODY_RE = re.compile(r"(<body(?:\s[^>]*)?>)", re.IGNORECASE)


def fragment(config: dict) -> str:
    course = html.escape(config["course_id"])
    links = [
        (f"https://kokunoyumeto.github.io/program-matematika-indonesia/id/#course-{course}", f"Program Indonesia — {course}"),
        (f"https://kokunoyumeto.github.io/program-matematika-indonesia/en/#course-{course}", f"English programme — {course}"),
    ]
    for number, original in enumerate(config["authoritative_originals"], 1):
        links.append((original["url"], original.get("label", f"Sumber asli / Original source {number}")))
    items = "\n".join(f'      <li><a href="{html.escape(url, quote=True)}">{html.escape(label)}</a></li>' for url, label in links)
    return f'''{START}
<style id="program-matematika-navigation-style">
  .program-matematika-navigation {{ box-sizing: border-box; margin: 0; padding: .75rem 1rem; width: 100%; background: #111827; color: #f9fafb; border-bottom: 3px solid #38bdf8; font: 600 1rem/1.45 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
  .program-matematika-navigation * {{ box-sizing: border-box; }} .program-matematika-navigation strong {{ display: block; margin: 0 0 .45rem; color: #fff; }}
  .program-matematika-navigation ul {{ display: flex; flex-wrap: wrap; gap: .45rem .75rem; margin: 0; padding: 0; list-style: none; }} .program-matematika-navigation li {{ margin: 0; padding: 0; }}
  .program-matematika-navigation a {{ display: inline-block; padding: .34rem .58rem; border: 1px solid #7dd3fc; border-radius: .35rem; color: #e0f2fe; background: #1f2937; text-decoration: underline; text-underline-offset: .15em; }}
  .program-matematika-navigation a:focus-visible {{ outline: 3px solid #fbbf24; outline-offset: 2px; }}
</style>
<nav class="program-matematika-navigation" aria-label="Navigasi program matematika / Mathematics programme navigation">
  <strong>Kursus {course}: edisi lokal, program lengkap, dan sumber asli / Course {course}: local edition, full programme, and original source</strong>
  <ul>
{items}
  </ul>
</nav>
{END}'''


def html_files(targets: list[Path]) -> list[Path]:
    found = set()
    for target in targets:
        if target.is_file() and target.suffix.lower() == ".html": found.add(target.resolve())
        elif target.is_dir(): found.update(p.resolve() for p in target.rglob("*.html") if p.is_file())
        else: raise FileNotFoundError(target)
    return sorted(found)


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("mode", choices=("inject", "check")); p.add_argument("--config", required=True, type=Path); p.add_argument("targets", nargs="+", type=Path); a = p.parse_args()
    config = json.loads(a.config.read_text(encoding="utf-8")); expected = fragment(config)
    required = [f"https://kokunoyumeto.github.io/program-matematika-indonesia/id/#course-{config['course_id']}", f"https://kokunoyumeto.github.io/program-matematika-indonesia/en/#course-{config['course_id']}", *[r["url"] for r in config["authoritative_originals"]]]
    files = html_files(a.targets)
    if not files: print("No HTML files found", file=sys.stderr); return 1
    if a.mode == "inject":
        for path in files:
            text = path.read_bytes().decode("utf-8-sig")
            if BLOCK_RE.search(text): updated = BLOCK_RE.sub(expected, text, count=1)
            else:
                m = BODY_RE.search(text)
                if not m: print(f"Missing <body>: {path}", file=sys.stderr); return 1
                updated = text[:m.end()] + "\n" + expected + text[m.end():]
            path.write_bytes(updated.encode("utf-8"))
    failed = []
    for path in files:
        data = path.read_bytes().decode("utf-8-sig"); problems = []
        if data.count(START) != 1 or data.count(END) != 1: problems.append("marker-count")
        if expected not in data: problems.append("fragment-mismatch")
        for url in required:
            if f'href="{html.escape(url, quote=True)}"' not in data: problems.append(f"missing-link:{url}")
        if problems: failed.append({"path": str(path), "problems": problems})
    print(json.dumps({"mode": a.mode, "course_id": config["course_id"], "html_count": len(files), "failures": failed}, ensure_ascii=False, sort_keys=True)); return 1 if failed else 0


if __name__ == "__main__": raise SystemExit(main())
