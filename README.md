# Esri Security Bug Counter

Counts the **security-related** bug fixes in Esri ArcGIS Enterprise patches from 2021 to 2026 YTD. Only bugs whose description is security-labeled (XSS, SQL injection, directory traversal, SSRF, CSRF, unvalidated redirect, log4j, etc.) are counted; non-security defect fixes listed on the same patch pages are ignored.

Esri does not publish a single centralized database of fixed bugs. Each patch page on
https://support.esri.com/en-us/patches-updates lists the `BUG-000xxxxxx` identifiers addressed
by that patch. This project scrapes those pages, counts the bug IDs, and reports the totals
per patch, per product, and per year.

## Findings

Across 46 catalogued security patches, 2021 – 18 Aug 2026:

| Year | Patches | Security-labeled fixes |
| --- | --- | --- |
| 2021 | 9 | 17 |
| 2022 | 17 | 21 |
| 2023 | 3 | 4 |
| 2024 | 1 | 1 |
| 2025 | 7 | 77 |
| 2026 (to Aug 18) | 9 | 21 |

- **2022 had the most patches but few distinct defects.** Those 17 patches were largely the
  Log4Shell response — the same fix shipped across eight products. 2022's 21 fix-rows are only
  16 distinct BUG-IDs, half of them Log4j.
- **2025 is the step change**: 77 security fixes, roughly 3× the 2022 total.
- **Patches got bigger.** Before 2025 no single patch carried more than 6 security fixes; since
  then two have carried 25 each.
- Portal for ArcGIS (68) and ArcGIS Server (61) account for 91% of all 141 fixes.

Charts are in [`charts/`](charts/); the full per-patch table is in [`report.md`](report.md).

## Important caveats

Read these before quoting any number from this repo.

- **These are Esri BUG-IDs, not CVEs.** Esri publishes very few CVEs and tracks most fixes as
  internal bug identifiers. These counts are **not** comparable to a CVE count for another
  product without heavy qualification.
- **Counts are fix-rows, not distinct defects.** A fix that ships in more than one patch is
  counted once per patch. Across the whole dataset that is 141 rows for 136 distinct BUG-IDs;
  all five duplicates fall in 2022, where the same Log4j fix shipped in several patches. If you
  need distinct defects, de-duplicate `bugs_detail.csv` on `bug_id`.
- **Classification is keyword-based**, not an expert review of each fix. See
  `SECURITY_KEYWORDS` in [`scrape_bugs.py`](scrape_bugs.py). It is deliberately conservative,
  but it will both miss fixes described in unusual wording and catch the occasional
  false positive.
- **A rise in counts is not necessarily a rise in defects.** Esri may simply document more
  detail per patch over time. This data cannot distinguish the two.
- **2026 is a partial year** (1 Jan – 18 Aug 2026).

## Scope

- **Security patches only** — patches Esri flags `Critical: security` in its patch JSON, or
  whose name contains "Security" or "Log4j". A small hand-curated set of adjacent patches that
  list security vulnerabilities in their issue text without carrying the flag is included and
  tagged in the `security_label` column as `partial`.
- **Products covered**: whatever appears in the catalog — currently Portal for ArcGIS, ArcGIS
  Server, ArcGIS Data Store, ArcGIS Web Adaptor, ArcGIS Workflow Manager Server, ArcGIS
  GeoEvent Server, ArcGIS Notebook Server, ArcGIS GeoEnrichment Server, ArcGIS Data
  Interoperability for Server, and ArcGIS Insights.
- **Time window**: patches released on or after 2021-01-01 (`MIN_DATE` in
  `build_catalog_from_json.py`).

## Files

| File | Purpose |
| --- | --- |
| `build_catalog_from_json.py` | Pulls Esri's `patches.json` and writes `patches_catalog.csv` (security patches since `MIN_DATE`, consolidated per name/product/year) |
| `patches_catalog.csv` | Catalog of security patch URLs with product, year, release date, and source flag |
| `patches_catalog.json` | Raw filtered catalog (includes QFE_ID and source for traceability) |
| `scrape_bugs.py` | Fetches each catalog URL, extracts distinct `BUG-000xxxxxx` IDs, classifies each as security or non-security, writes the CSVs and `report.md` |
| `bug_counts.csv` | Output: one row per patch with its security-labeled fix count |
| `bugs_detail.csv` | Output: one row per (patch, bug ID) with its short description + `is_security` flag |
| `report.md` | Generated summary report with per-patch, per-year and per-product tables |
| `make_charts.py` | Generates three PNG charts (light + dark) from `bug_counts.csv` |
| `charts/` | Chart PNGs (patches and fixes per year, product breakdown, timeline); dark-mode twins in `charts/dark/` |
| `cache/` | On-disk cache of fetched patch HTML. Git-ignored — re-created on first run |

## How to run

```bash
python -m pip install -r requirements.txt

# 1. Build the catalog from Esri's patch notification JSON
python build_catalog_from_json.py

# 2. Scrape each patch page and count BUG IDs (caches HTML under cache/)
python scrape_bugs.py

# 3. Generate the charts into charts/ and charts/dark/
python make_charts.py

# Re-run later using only cached HTML (no network):
python scrape_bugs.py --no-fetch
```

The scraper sleeps 1 second between fetches by default (`--sleep`) and caches every page, so a
full re-run costs Esri nothing. If you fork this, please change `USER_AGENT` in
`scrape_bugs.py` to point at your own repository.

## Authoritative source

Esri publishes a machine-readable list of all patches at
`https://content.esri.com/patch_notification/patches.json`. Each entry has a
`Critical` field that Esri sets to `"security"` for security patches. That field, plus a small
hand-curated list of patches that mention security vulnerabilities in their issue text without
being flagged, is used as the catalog. This avoids relying on web search to discover patch URLs.

## Methodology notes

1. **Catalog source**: `patches_catalog.csv` is generated by `build_catalog_from_json.py` from
   Esri's `patches.json`. Patches are kept where `Critical == "security"` OR the name contains
   "Security" OR "Log4j", released on or after `MIN_DATE`. Esri ships many per-version URLs for
   the same patch name (e.g. Log4j, Notebook Server); those are consolidated to one row per
   (name, product, year), keeping the latest release's URL. An `EXTRA_PATCHES` list appends
   non-flagged patches that list explicit security vulnerabilities in their issue text
   (Web Adaptor Stability, Workflow Manager, Data Store Reliability).
2. **Counting only NEW bugs per patch**: Each patch page has a main "Issues addressed" list
   followed by cumulative "To avoid conflicts the &lt;version&gt; version also addresses:"
   re-lists of older fixes for backward-version compatibility. **Only the first list is
   counted** — the cumulative re-lists are excluded, so each patch is credited only for the
   bugs it newly addresses.
3. **"Security-labeled" count**: A bug counts as security-labeled if its description contains
   any keyword in `SECURITY_KEYWORDS` (in `scrape_bugs.py`): `security vulnerability`, `XSS`,
   `cross-site scripting`, `SQL injection`, `directory traversal`, `LFI`, `RFI`, `SSRF`,
   `CSRF`, `unvalidated redirect`, `unvalidated file upload`, `HTML injection`, `log4j`,
   `improper authentication`, `unauthorized access`, `information disclosure`,
   `encrypted user-defined setting`, `privilege escalation`, and others.
4. **Mentions without a BUG-ID**: Esri occasionally lists a security fix as plain prose with no
   `BUG-000xxxxxx` identifier (e.g. Workflow Manager "Security vulnerability allowing Workflow
   Administrators to access encrypted user-defined setting values."). These are captured as
   `security_mentions_without_bug_id` and shown in the report's "Mentions w/o BUG-ID" column.
   They are **not** added to the bug counts, because there is no trackable identifier.
5. **No cross-patch de-duplication.** Counts are per patch. The same BUG-ID appearing in two
   patches is counted twice — see the caveat above.
6. **Release dates**: taken from the `ReleaseDate` field in `patches.json`.
7. **Obsolete/replaced patches**: the Esri JSON does not surface a "replaced by" relationship,
   so the `replaced_by` column is always empty and all catalogued patches are treated as active.

## Data sources

- Esri Support "Patches and Updates" pages, e.g.
  https://support.esri.com/en-us/patches-updates/2026/portal-for-arcgis-security-2026-update-3-patch
- Esri patch notification JSON: https://content.esri.com/patch_notification/patches.json

## Managed services

Keeping an ArcGIS Enterprise estate patched is the practical problem behind this data — the
patches are getting larger and more frequent, as the charts above show. Avineon-Tensing offers
[geospatial managed services](https://www.avineon-tensing.com/en-gb/services/geospatial-managed-services)
covering exactly this.

## License and attribution

Code in this repository is released under the MIT License (see `LICENSE`).

The underlying patch data is published by Esri and remains Esri's. This project is an
independent analysis and is **not affiliated with or endorsed by Esri**. Scraped page HTML is
cached locally and deliberately not redistributed here; run the scripts to reproduce it. For
authoritative detail on any fix, follow the patch URL in `bug_counts.csv` and read the
"Issues addressed with this patch" section.
