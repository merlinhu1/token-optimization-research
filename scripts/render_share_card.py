#!/usr/bin/env python3
"""Render the site's link-preview image, docs/og.png, from the session registry.

The card repeats the site's headline figures, so it is built from update_site_data.build()
rather than typed by hand. It needs a Chromium binary for the screenshot (pass --chrome, set
CHROME, or have a Playwright headless shell installed) and network access to Google Fonts, whose
files are inlined so the screenshot never waits on a font request.

Rerun it whenever update_site_data.py changes the figures.
"""
from __future__ import annotations

import argparse
import base64
import glob
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

try:
    from scripts import update_site_data as site
except ImportError:
    import update_site_data as site

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / site.SHARE_IMAGE
FONT_CSS = "https://fonts.googleapis.com/css2?family=Geist:wght@500;600;700&family=Geist+Mono:wght@500&display=block"
BROWSER_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def find_chrome(explicit: str | None) -> str:
    candidates = [explicit, os.environ.get("CHROME")]
    candidates += sorted(glob.glob(os.path.expanduser(
        "~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell")), reverse=True)
    candidates += [shutil.which(n) for n in ("chromium", "chromium-browser", "google-chrome")]
    for c in candidates:
        if c and Path(c).exists():
            return c
    raise SystemExit("no Chromium found; pass --chrome or set CHROME")


def inline_fonts() -> str:
    """Fetch the Latin subsets of Geist and inline them as data URIs."""
    req = urllib.request.Request(FONT_CSS, headers={"User-Agent": BROWSER_UA})
    css = urllib.request.urlopen(req, timeout=30).read().decode()
    blocks = re.findall(r"/\* latin \*/\s*(@font-face\s*{[^}]*})", css)
    out = []
    for block in blocks:
        url = re.search(r"url\((https://[^)]+)\)", block).group(1)
        data = base64.b64encode(urllib.request.urlopen(url, timeout=30).read()).decode()
        out.append(block.replace(url, f"data:font/woff2;base64,{data}"))
    if not out:
        raise SystemExit("could not read Geist from Google Fonts")
    return "\n".join(out)


def card_html(data: dict, fonts: str) -> str:
    words = site.headline(data)
    widest = max(data["pools"], key=lambda p: p["band_pct"])
    cells = {(c["product"], c["agent"], c["codebase"]): c for c in data["cells"]}
    retest = [cells[(r["product"], r["agent"], r["codebase"])] for r in data["retest"]]
    lost = sum(not c["confirmed"] for c in retest)
    t = data["totals"]

    # Strip of the widest no-optimizer pool: one dot per identical run, by distance from its median.
    lo, hi = min(widest["run_offset_pct"]), max(widest["run_offset_pct"])
    span = max(abs(lo), abs(hi)) * 1.15
    x = lambda v: 20 + (v + span) / (2 * span) * 400
    dots = "".join(f'<circle cx="{x(v):.1f}" cy="26" r="9" fill="#f0b450" stroke="#0f1013" stroke-width="3"/>'
                   for v in widest["run_offset_pct"])
    strip = (f'<svg width="440" height="52" viewBox="0 0 440 52" xmlns="http://www.w3.org/2000/svg">'
             f'<rect x="{x(lo):.1f}" y="17" width="{x(hi) - x(lo):.1f}" height="18" rx="9" fill="rgba(240,180,80,.18)"/>'
             f'<line x1="{x(0):.1f}" x2="{x(0):.1f}" y1="4" y2="48" stroke="rgba(255,255,255,.25)"/>{dots}</svg>')
    agent = {a["id"]: a["name"] for a in data["agents"]}[widest["agent"]]
    project = {c["id"]: c["name"] for c in data["codebases"]}[widest["codebase"]]
    lead = words["lead"].replace(f"Up to {widest['band_pct']:.1f}% cost difference.", "").strip()

    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{fonts}
*{{box-sizing:border-box;margin:0}}
html,body{{width:1200px;height:630px;background:#08090a;overflow:hidden}}
body{{font-family:Geist,sans-serif;color:#f7f8f8;position:relative;padding:64px 72px}}
body::before{{content:"";position:absolute;inset:-200px auto auto -200px;width:900px;height:700px;
  background:radial-gradient(closest-side,rgba(123,136,255,.26),transparent)}}
.wrap{{position:relative;display:grid;grid-template-columns:1fr 470px;gap:56px;height:100%}}
.eyebrow{{font:500 17px/1 'Geist Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#8a8f98}}
.eyebrow b{{color:#7b88ff;font-weight:500}}
h1{{font-weight:650;font-size:86px;line-height:.95;letter-spacing:-.055em;margin-top:34px;
  background:linear-gradient(180deg,#fff 35%,#9aa0ab);-webkit-background-clip:text;color:transparent}}
.lead{{margin-top:34px;font-size:27px;line-height:1.3;color:#c9ccd3;letter-spacing:-.01em;max-width:560px}}
.url{{position:absolute;bottom:0;left:0;font:500 17px/1 'Geist Mono',monospace;color:#5f646c}}
.right{{display:flex;flex-direction:column;justify-content:center;border-left:1px solid rgba(255,255,255,.1);padding-left:48px}}
.big{{font-weight:650;font-size:132px;line-height:.9;letter-spacing:-.05em;color:#f0b450}}
.cap{{margin-top:16px;font-size:21px;line-height:1.35;color:#c9ccd3}}
.cap span{{color:#8a8f98}}
.strip{{margin-top:22px}}
.row{{display:flex;gap:36px;margin-top:30px;padding-top:24px;border-top:1px solid rgba(255,255,255,.1)}}
.row div{{font-size:17px;line-height:1.3;color:#8a8f98;max-width:190px}}
.row b{{display:block;font-weight:650;font-size:40px;letter-spacing:-.04em;color:#f7f8f8;margin-bottom:6px}}
.row b.k{{color:#7b88ff}}
.row b small{{font-size:22px;color:#8a8f98;font-weight:500}}
</style></head><body><div class="wrap">
<div style="position:relative">
  <div class="eyebrow"><b>Independent research</b> / AI coding 2026</div>
  <h1>The Token<br>Savings Illusion</h1>
  <p class="lead">{html.escape(lead)}</p>
  <div class="url">merlinhu1.github.io/token-optimization-research</div>
</div>
<div class="right">
  <div class="big">{widest['band_pct']:.1f}%</div>
  <p class="cap">cost difference between identical runs<br><span>{html.escape(agent)} on {html.escape(project)}, {widest['runs']} runs</span></p>
  <div class="strip">{strip}</div>
  <div class="row">
    <div><b class="k">{t['confirmed']}<small> of {t['cells']}</small></b>optimizer setups held up</div>
    <div><b>{lost}<small> of {len(retest)}</small></b>early wins failed a second run</div>
  </div>
</div>
</div></body></html>"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chrome", help="path to a Chromium or headless-shell binary")
    args = parser.parse_args(argv)

    chrome = find_chrome(args.chrome)
    page = card_html(site.build(), inline_fonts())
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "card.html"
        src.write_text(page)
        shot = Path(tmp) / "card.png"
        subprocess.run([chrome, "--no-sandbox", "--hide-scrollbars", "--force-device-scale-factor=1",
                        f"--window-size={site.SHARE_SIZE[0]},{site.SHARE_SIZE[1]}", "--virtual-time-budget=3000",
                        f"--screenshot={shot}", src.as_uri()], check=True, timeout=120,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.copyfile(shot, OUTPUT)
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
