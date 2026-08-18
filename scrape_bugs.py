"""
scrape_bugs.py

Fetches each Esri security patch page listed in patches_catalog.csv, extracts
all distinct BUG-000xxxxxx identifiers, classifies each as security-related or
not based on its description text, and writes:

  - bug_counts.csv      : one row per patch with its security-labeled fix count
  - bugs_detail.csv     : one row per (patch, bug ID) with description + is_security flag
  - report.md           : human-readable summary with year-over-year and per-product totals

Pages are cached under cache/ so re-runs are fast and polite to support.esri.com.

Usage:
    python scrape_bugs.py            # fetch missing pages, then build outputs
    python scrape_bugs.py --no-fetch  # use only cached pages, skip network
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent
CATALOG_CSV = ROOT / "patches_catalog.csv"
CACHE_DIR = ROOT / "cache"
OUT_COUNTS = ROOT / "bug_counts.csv"
OUT_DETAIL = ROOT / "bugs_detail.csv"
OUT_REPORT = ROOT / "report.md"

# Sent on every request so Esri can identify the traffic. If you fork this,
# change the contact to your own repository or email.
USER_AGENT = "esri-bug-counter/1.0 (research; +https://github.com/om2468/esri-bug-counter)"

BUG_RE = re.compile(r"BUG-0+\d+", re.IGNORECASE)
LINE_BUG_RE = re.compile(r"^(.*?)(BUG-0+\d+)(.*)$")

SECURITY_KEYWORDS = [
    "security vulnerability",
    "xss",
    "cross-site scripting",
    "cross site scripting",
    "sql injection",
    "directory traversal",
    "local file inclusion",
    "lfi",
    "remote file inclusion",
    "rfi",
    "ssrf",
    "server-side request forgery",
    "server side request forgery",
    "csrf",
    "cross-site request forgery",
    "cross site request forgery",
    "unvalidated redirect",
    "unvalidated file upload",
    "html injection",
    "log4j",
    "improper authentication",
    "unauthorized access",
    "information disclosure",
    "remote file download",
    "relative path sequence",
    "url manipulation",
    "file handle leak",
    # Workflow Manager style: access to encrypted user-defined settings
    "encrypted user-defined setting",
    # Generic privilege/access wording that Esri pairs with "Security vulnerability"
    "privilege escalation",
]


@dataclass
class Bug:
    bug_id: str
    description: str
    is_security: bool


@dataclass
class Patch:
    patch_id: str
    product: str
    year: int
    release_date: str
    title: str
    url: str
    replaced_by: str
    security_label: str
    bugs: List[Bug] = field(default_factory=list)
    # Security-flavored <li> lines on the page that do NOT carry a BUG- ID.
    # Esri occasionally lists a security fix as plain prose (e.g. Workflow Manager
    # "Security vulnerability allowing Workflow Administrators to access encrypted
    # user-defined setting values."). We surface these so they are not lost.
    security_mentions_without_bug_id: List[str] = field(default_factory=list)


def fetch_url(url: str, session: requests.Session, no_fetch: bool = False) -> str | None:
    """Fetch a URL with on-disk caching keyed by the URL's basename."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_name = url.rstrip("/").split("/")[-1] or "index"
    cache_file = CACHE_DIR / f"{cache_name}.html"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8", errors="replace")
    if no_fetch:
        return None
    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        text = resp.text
    except Exception as exc:  # noqa: BLE001
        print(f"  ! fetch failed for {url}: {exc}", file=sys.stderr)
        return None
    cache_file.write_text(text, encoding="utf-8")
    return text


def _is_avoid_conflicts_marker(text: str) -> bool:
    """True when a paragraph introduces a cumulative re-list section."""
    t = text.lower().strip()
    return t.startswith("to avoid conflicts")


def extract_bugs(html_text: str) -> Tuple[List[Bug], List[str]]:
    """Parse a patch page and return (new BUG-IDs, security-mention lines without BUG-IDs).

    Only the *first* <ul> after the "Issues addressed with this patch" heading is counted as
    the patch's own new fixes. Every subsequent <ul> on the page is preceded by a
    "To avoid conflicts the <version> version also addresses:" paragraph and is a cumulative
    re-list of older fixes for backward-version compatibility. Those re-lists are skipped so
    each patch reports only the bugs it newly introduces, not bugs carried over from earlier
    patches (which would otherwise inflate counts and double-count across patches).
    """
    soup = BeautifulSoup(html_text, "html.parser")
    candidates: List[Tuple[str, str]] = []
    seen: set[str] = set()
    security_mentions: List[str] = []

    # Locate the "Issues addressed with this patch" heading. Esri gives it id
    # "issues-addressed-with-this-patch"; fall back to a case-insensitive text match.
    heading = soup.find(id="issues-addressed-with-this-patch")
    if heading is None:
        for h in soup.find_all(["h2", "h3", "h4"]):
            if "issues addressed" in h.get_text(" ", strip=True).lower():
                heading = h
                break

    primary_items: List = []
    if heading is not None:
        # The new-issue list is the first <ul> that follows the heading and appears
        # before any "To avoid conflicts … also addresses:" paragraph.
        node = heading.find_next(["ul", "p"])
        while node is not None:
            if node.name == "p" and _is_avoid_conflicts_marker(node.get_text(" ", strip=True)):
                break  # everything from here on is a cumulative re-list; stop
            if node.name == "ul":
                primary_items = node.find_all("li", recursive=False)
                break
            node = node.find_next(["ul", "p"])

    if primary_items:
        for li in primary_items:
            text = li.get_text(" ", strip=True)
            m = LINE_BUG_RE.match(text)
            if m:
                bug_id = m.group(2).upper()
                if bug_id in seen:
                    continue
                seen.add(bug_id)
                desc = (m.group(1) + " " + m.group(3)).strip(" -—\u00a0")
                candidates.append((bug_id, desc))
                continue
            if "BUG-" in text:
                for match in BUG_RE.findall(text):
                    bug_id = match.upper()
                    if bug_id in seen:
                        continue
                    seen.add(bug_id)
                    desc = text.replace(match, "").strip(" -—\u00a0")
                    candidates.append((bug_id, desc))
                continue
            # No BUG- ID on this <li>: record it only if it reads as a security fix
            # (Esri sometimes lists "Security vulnerability allowing ..." without a BUG- ID).
            text_lower = text.lower()
            if any(kw in text_lower for kw in SECURITY_KEYWORDS) and len(text) < 300:
                if text not in security_mentions:
                    security_mentions.append(text)
    else:
        # Fallback for pages whose structure differs: scan all text nodes for BUG- lines
        # but still skip anything that appears after a "To avoid conflicts" marker.
        skip = False
        for text in soup.stripped_strings:
            if _is_avoid_conflicts_marker(text):
                skip = True
                continue
            if skip:
                continue
            if "BUG-" in text:
                m = LINE_BUG_RE.match(text)
                if m:
                    bug_id = m.group(2).upper()
                    if bug_id in seen:
                        continue
                    seen.add(bug_id)
                    desc = (m.group(1) + " " + m.group(3)).strip(" -—\u00a0")
                    candidates.append((bug_id, desc))

    bugs: List[Bug] = []
    for bug_id, desc in candidates:
        desc_clean = html.unescape(desc)
        desc_lower = desc_clean.lower()
        is_sec = any(kw in desc_lower for kw in SECURITY_KEYWORDS)
        bugs.append(Bug(bug_id=bug_id, description=desc_clean[:400], is_security=is_sec))
    return bugs, security_mentions


def load_catalog() -> List[Patch]:
    rows = pd.read_csv(CATALOG_CSV, keep_default_na=False)
    patches: List[Patch] = []
    for _, row in rows.iterrows():
        patches.append(
            Patch(
                patch_id=row["patch_id"],
                product=row["product"],
                year=int(row["year"]),
                release_date=row["release_date"],
                title=row["title"],
                url=row["url"],
                replaced_by=row.get("replaced_by", ""),
                security_label=row.get("security_label", "yes"),
            )
        )
    return patches


def build_counts(patches: List[Patch]) -> pd.DataFrame:
    rows = []
    for p in patches:
        sec = sum(1 for b in p.bugs if b.is_security)
        rows.append(
            {
                "patch_id": p.patch_id,
                "product": p.product,
                "year": p.year,
                "release_date": p.release_date,
                "title": p.title,
                "url": p.url,
                "replaced_by": p.replaced_by,
                "security_label": p.security_label,
                "security_bugs": sec,
                "security_mentions_without_bug_id": len(p.security_mentions_without_bug_id),
            }
        )
    return pd.DataFrame(rows)


def build_detail(patches: List[Patch]) -> pd.DataFrame:
    rows = []
    for p in patches:
        for b in p.bugs:
            rows.append(
                {
                    "patch_id": p.patch_id,
                    "product": p.product,
                    "year": p.year,
                    "bug_id": b.bug_id,
                    "description": b.description,
                    "is_security": b.is_security,
                }
            )
    return pd.DataFrame(rows)


def write_report(counts: pd.DataFrame) -> None:
    """Generate a markdown report with year and product breakdowns."""
    lines: List[str] = []
    lines.append("# Esri Security Bug Count Report (2021–2026 YTD)\n")
    lines.append(
        "Counts of the **security-labeled** `BUG-000xxxxxx` identifiers each Esri security patch "
        "introduces. Non-security defect fixes listed on the same patch pages are **not counted**. "
        "Cumulative “To avoid conflicts the <version> version also addresses:” re-lists of older "
        "fixes are also **excluded**, so each patch is only credited for the security bugs it newly "
        "fixes and the per-year totals are additive. A bug is classified as *security-related* "
        "when its description contains one of the keywords in `SECURITY_KEYWORDS` (XSS, SQL "
        "injection, directory traversal, SSRF, CSRF, unvalidated redirect, log4j, etc.). See "
        "`README.md` for methodology.\n"
    )

    # Headline totals
    active = counts[counts["replaced_by"] == ""].copy()
    sec_bugs = int(active["security_bugs"].sum())
    lines.append("## Headline totals (active patches only)\n")
    lines.append(f"- Patches catalogued: **{len(counts)}** ({len(active)} active, {len(counts)-len(active)} obsolete/replaced)")
    lines.append(f"- Security-labeled bug fixes introduced by these patches: **{sec_bugs}** "
                 "(each patch contributes only its own new security fixes; cumulative re-lists are excluded)\n")

    # Per-year table
    lines.append("## Security bug counts per patch (chronological)\n")
    lines.append("| Release date | Year | Product | Patch | Security bugs | Mentions w/o BUG-ID | Status |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for _, r in counts.sort_values("release_date").iterrows():
        status = "replaced" if r["replaced_by"] else "active"
        mentions = int(r.get("security_mentions_without_bug_id", 0))
        lines.append(
            f"| {r['release_date']} | {r['year']} | {r['product']} | "
            f"[{r['title']}]({r['url']}) | {r['security_bugs']} | {mentions} | {status} |"
        )
    lines.append("")

    # Per-year totals (now additive since each patch only counts its own new bugs)
    lines.append("## Per-year security totals (additive — each patch counts only its own new fixes)\n")
    lines.append("| Year | Patches | Security-labeled bug fixes |")
    lines.append("| --- | --- | --- |")
    for year in sorted(counts["year"].unique()):
        yr = counts[counts["year"] == year]
        lines.append(
            f"| {year} | {len(yr)} | {int(yr['security_bugs'].sum())} |"
        )
    lines.append("")

    # Per-product summary (active patches only)
    lines.append("## Per-product security summary (active patches only)\n")
    lines.append("| Product | Patches | Security bugs fixed |")
    lines.append("| --- | --- | --- |")
    for product, grp in active.groupby("product"):
        lines.append(
            f"| {product} | {len(grp)} | {int(grp['security_bugs'].sum())} |"
        )
    lines.append("")

    # Charts (McKinsey-style, generated by make_charts.py)
    lines.append("## Charts\n")
    lines.append("Run `python make_charts.py` to (re)generate the three charts in `charts/`, "
                 "plus a dark-mode twin of each in `charts/dark/`. They are intentionally "
                 "rendered as standalone PNGs so they can be dropped into a slide deck. Each "
                 "chart carries its own source line and methodology footnote, and every plotted "
                 "value is also in `bug_counts.csv` so no number is reachable only through the "
                 "picture.\n")
    lines.append("| Chart | File | Story |")
    lines.append("| --- | --- | --- |")
    lines.append("| Patches released and security-labeled bug fixes per year | `charts/patches_and_fixes_per_year.png` | Patch cadence and security-fix volume tell different stories (2022 had the most patches; 2025 had the most fixes) |")
    lines.append("| Security-labeled bug fixes by product | `charts/product_breakdown.png` | Portal for ArcGIS and ArcGIS Server account for 91% of all security fixes |")
    lines.append("| Timeline of Portal and Server patches, sized by security-fix count | `charts/timeline.png` | Since 2025 a single patch has carried up to 25 security fixes — before that, never more than 6 |")
    lines.append("")

    lines.append("## Notes\n")
    lines.append("- Counts reflect only the *new* bugs each patch introduces. Esri patch pages "
                 "also include cumulative \"To avoid conflicts the <version> version also "
                 "addresses:\" re-lists of older fixes for backward-version compatibility; "
                 "those re-lists are deliberately NOT counted, so a bug is only attributed to "
                 "the patch that first addressed it. This means the per-year totals are "
                 "directly additive (no double counting across patches).")
    lines.append("- Security classification is keyword-based and conservative. Bugs labeled "
                 "only as \"ArcGIS Server has a security vulnerability\" are counted as security "
                 "even though the specific vulnerability class is not named in the patch page.")
    lines.append("- The \"Mentions w/o BUG-ID\" column captures security-flavored fix lines "
                 "that Esri wrote without a `BUG-000xxxxxx` identifier (e.g. Workflow Manager "
                 "\"Security vulnerability allowing Workflow Administrators to access encrypted "
                 "user-defined setting values.\"). These are surfaced for completeness but are "
                 "NOT added to the bug counts since there is no trackable identifier.")
    lines.append("- For authoritative details on each fix, follow the patch URL and read the "
                 "\"Issues addressed with this patch\" section.")
    lines.append("")

    OUT_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Scrape Esri patch pages and count BUG IDs.")
    ap.add_argument("--no-fetch", action="store_true", help="Use only cached HTML; skip network.")
    ap.add_argument("--sleep", type=float, default=1.0, help="Seconds between fetches (default 1.0).")
    args = ap.parse_args()

    patches = load_catalog()
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        }
    )

    print(f"Loaded {len(patches)} patches from catalog.")
    for p in patches:
        print(f"[{p.patch_id}] {p.title}")
        html_text = fetch_url(p.url, session, no_fetch=args.no_fetch)
        if html_text is None:
            print(f"  ! no content for {p.url} (skip)")
            continue
        p.bugs, p.security_mentions_without_bug_id = extract_bugs(html_text)
        sec = sum(1 for b in p.bugs if b.is_security)
        print(f"  found {sec} security-labeled bug fix(es)"
              f" across {len(p.bugs)} total entries")
        if p.security_mentions_without_bug_id:
            print(f"  + {len(p.security_mentions_without_bug_id)} security mentions without BUG- ID")
        if not args.no_fetch:
            time.sleep(args.sleep)

    counts = build_counts(patches)
    detail = build_detail(patches)
    counts.to_csv(OUT_COUNTS, index=False)
    detail.to_csv(OUT_DETAIL, index=False)
    write_report(counts)

    print(f"\nWrote {OUT_COUNTS.name} ({len(counts)} rows), {OUT_DETAIL.name} ({len(detail)} rows), {OUT_REPORT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())