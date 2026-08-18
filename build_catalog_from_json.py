"""
build_catalog_from_json.py

Fetches https://content.esri.com/patch_notification/patches.json, filters to
security-marked patches released in the last 3 years (>= 2023-01-01), and writes
patches_catalog.json (the raw filtered list) plus patches_catalog.csv (the
columns the scraper consumes).

The Esri JSON is the authoritative source of which patches Esri itself flags as
"Critical: security". We then hand-augment with a small set of non-security-flagged
patches that nonetheless list security vulnerabilities in their issue text
(ArcGIS Web Adaptor Stability, ArcGIS Workflow Manager Server patches) so the
report captures them too.
"""

from __future__ import annotations

import csv
import json
import re
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
URL = "https://content.esri.com/patch_notification/patches.json"
OUT_JSON = ROOT / "patches_catalog.json"
OUT_CSV = ROOT / "patches_catalog.csv"

# Patches that Esri did NOT flag Critical=security in the JSON but that list
# explicit security vulnerabilities in their "Issues addressed" section. These
# are appended to the catalog with security_label="partial".
EXTRA_PATCHES = [
    {
        "Name": "ArcGIS Web Adaptor (IIS) Stability Patch",
        "Products": "ArcGIS Enterprise,ArcGIS Web Adaptor",
        "url": "https://support.esri.com/en-us/patches-updates/2025/arcgis-web-adaptor-iis-stability-patch",
        "ReleaseDate": "10/20/2025",
        "security_label": "partial",
    },
    {
        "Name": "ArcGIS Workflow Manager Server 11.3 Patch 3",
        "Products": "ArcGIS Enterprise,ArcGIS Workflow Manager Server",
        "url": "https://support.esri.com/en-us/patches-updates/2026/arcgis-workflow-manager-server-11-3-patch-3",
        "ReleaseDate": "02/25/2026",
        "security_label": "partial",
    },
    {
        "Name": "ArcGIS Workflow Manager Server 11.5 Patch 1",
        "Products": "ArcGIS Enterprise,ArcGIS Workflow Manager Server",
        "url": "https://support.esri.com/en-us/patches-updates/2026/arcgis-workflow-manager-server-11-5-patch-1",
        "ReleaseDate": "07/21/2026",
        "security_label": "partial",
    },
    {
        "Name": "ArcGIS Data Store 11.5 Reliability Patch",
        "Products": "ArcGIS Enterprise,ArcGIS Data Store",
        "url": "https://support.esri.com/en-us/patches-updates/2026/arcgis-data-store-11-5-reliability-patch",
        "ReleaseDate": "02/10/2026",
        "security_label": "partial",
    },
]

MIN_DATE = datetime(2023, 1, 1)


def parse_date(s: str) -> datetime | None:
    for fmt in ("%m/%d/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
MIN_DATE = datetime(2021, 1, 1)


def product_from_name(name: str, products: str) -> str:
    """Pick the most specific product label from the JSON Products field."""
    p = (products or "").split(",")
    priority = [
        "Portal for ArcGIS",
        "ArcGIS Server",
        "ArcGIS Data Store",
        "ArcGIS Web Adaptor",
        "ArcGIS Workflow Manager Server",
        "ArcGIS GeoEvent Server",
        "ArcGIS Notebook Server",
        "ArcGIS GeoEnrichment Server",
        "ArcGIS Data Interoperability for Server",
        "ArcGIS Enterprise",
    ]
    for item in priority:
        if any(item.lower() in x.lower().strip() for x in p):
            return item
    # Fall back to a token from the patch name
    name_lower = name.lower()
    if "portal" in name_lower:
        return "Portal for ArcGIS"
    if "data store" in name_lower:
        return "ArcGIS Data Store"
    if "web adaptor" in name_lower:
        return "ArcGIS Web Adaptor"
    if "workflow manager" in name_lower:
        return "ArcGIS Workflow Manager Server"
    if "notebook" in name_lower:
        return "ArcGIS Notebook Server"
    if "geoevent" in name_lower:
        return "ArcGIS GeoEvent Server"
    if "geoenrichment" in name_lower:
        return "ArcGIS GeoEnrichment Server"
    if "server" in name_lower:
        return "ArcGIS Server"
    return p[0].strip() if p else "ArcGIS Enterprise"


def slug(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()
    return s[:40]


def main() -> int:
    with urllib.request.urlopen(URL, timeout=30) as resp:
        data = json.load(resp)

    # data == {"Product": [ {version, patches:[...]}, ... ]}
    all_patches = []
    for product_block in data.get("Product", []):
        for patch in product_block.get("patches", []):
            all_patches.append(patch)

    print(f"Total patches in Esri JSON: {len(all_patches)}")

    filtered = []
    seen_urls: set[str] = set()
    # Many Esri patches ship one URL per product version with the same patch name
    # (e.g. "ArcGIS Notebook Server Security Patch", "ArcGIS Server Log4j Patch").
    # Consolidate those into a single row per (name, product, year), keeping the
    # latest release's URL so the catalog isn't flooded with near-identical entries.
    latest_per_group: dict[tuple[str, str, int], tuple[dict, datetime]] = {}
    deferred_groups: set[tuple[str, str, int]] = set()
    for p in all_patches:
        critical = (p.get("Critical") or "").lower()
        is_security = critical == "security"
        name = p.get("Name", "")
        if not (is_security or "Security" in name or "Log4j" in name):
            continue
        rd = parse_date(p.get("ReleaseDate", ""))
        if rd is None or rd < MIN_DATE:
            continue
        url = p.get("url", "")
        product = product_from_name(name, p.get("Products", ""))
        group_key = (name.strip().lower(), product, rd.year)
        prev = latest_per_group.get(group_key)
        if prev is None or rd > prev[1]:
            latest_per_group[group_key] = (p, rd)
        deferred_groups.add(group_key)

    # Emit one row per group, using the latest release's URL. Skip groups whose
    # latest URL was already seen under a different group (defensive dedupe).
    for group_key in sorted(deferred_groups, key=lambda k: latest_per_group[k][1]):
        p, rd = latest_per_group[group_key]
        url = p.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        critical = (p.get("Critical") or "").lower()
        is_security = critical == "security"
        filtered.append((p, is_security))

    filtered.sort(key=lambda t: parse_date(t[0].get("ReleaseDate", "")))

    print(f"Security patches since {MIN_DATE.date()}: {len(filtered)} "
          f"(consolidated from {len(deferred_groups)} per-version groups)")

    # Build a unified list, including extras
    rows = []
    for p, is_sec in filtered:
        rd = parse_date(p["ReleaseDate"])
        rows.append(
            {
                "patch_id": slug(p["Name"]),
                "product": product_from_name(p["Name"], p.get("Products", "")),
                "year": rd.year,
                "release_date": rd.strftime("%Y-%m-%d"),
                "title": p["Name"],
                "url": p["url"],
                "replaced_by": "",
                "security_label": "yes" if is_sec else "partial",
                "source": "esri_json",
                "qfe_id": p.get("QFE_ID", ""),
            }
        )

    seen_urls = {r["url"] for r in rows}
    for extra in EXTRA_PATCHES:
        if extra["url"] in seen_urls:
            continue
        seen_urls.add(extra["url"])
        rd = parse_date(extra["ReleaseDate"])
        rows.append(
            {
                "patch_id": slug(extra["Name"]),
                "product": product_from_name(extra["Name"], extra["Products"]),
                "year": rd.year,
                "release_date": rd.strftime("%Y-%m-%d"),
                "title": extra["Name"],
                "url": extra["url"],
                "replaced_by": "",
                "security_label": extra["security_label"],
                "source": "manual_extra",
                "qfe_id": "",
            }
        )

    # Sort by release date then title
    rows.sort(key=lambda r: (r["release_date"], r["title"]))

    # Save raw filtered JSON for transparency
    OUT_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    # Save CSV consumed by the scraper (drop the extra helper columns)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "patch_id",
                "product",
                "year",
                "release_date",
                "title",
                "url",
                "replaced_by",
                "security_label",
            ],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r[k] for k in writer.fieldnames})

    print(f"Wrote {OUT_CSV.name} ({len(rows)} rows) and {OUT_JSON.name}")
    # Quick summary
    by_year: dict[int, int] = {}
    for r in rows:
        by_year[r["year"]] = by_year.get(r["year"], 0) + 1
    print("By year:", by_year)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())