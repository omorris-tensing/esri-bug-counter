# Esri Security Bug Count Report (2021–2026 YTD)

Counts of the **security-labeled** `BUG-000xxxxxx` identifiers each Esri security patch introduces. Non-security defect fixes listed on the same patch pages are **not counted**. Cumulative “To avoid conflicts the <version> version also addresses:” re-lists of older fixes are also **excluded**, so each patch is only credited for the security bugs it newly fixes and the per-year totals are additive. A bug is classified as *security-related* when its description contains one of the keywords in `SECURITY_KEYWORDS` (XSS, SQL injection, directory traversal, SSRF, CSRF, unvalidated redirect, log4j, etc.). See `README.md` for methodology.

## Headline totals (active patches only)

- Patches catalogued: **46** (46 active, 0 obsolete/replaced)
- Security-labeled bug fixes introduced by these patches: **141** (each patch contributes only its own new security fixes; cumulative re-lists are excluded)

## Security bug counts per patch (chronological)

| Release date | Year | Product | Patch | Security bugs | Mentions w/o BUG-ID | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 2021-02-09 | 2021 | Portal for ArcGIS | [Portal for ArcGIS Security 2019 Update 2 Patch](https://support.esri.com/en-us/patches-updates/2019/portal-for-arcgis-security-2019-update-2-patch-7749) | 2 | 0 | active |
| 2021-03-16 | 2021 | ArcGIS Server | [ArcGIS (Desktop, Engine, Server) General Raster Security Patch](https://support.esri.com/en-us/patches-updates/2021/arcgis-desktop-engine-server-general-raster-security-pa-7869) | 0 | 0 | active |
| 2021-03-31 | 2021 | ArcGIS Server | [ArcGIS Server Map and Feature Service Security Patch](https://support.esri.com/en-us/patches-updates/2021/arcgis-server-map-and-feature-service-security-patch-7873) | 1 | 1 | active |
| 2021-04-26 | 2021 | Portal for ArcGIS | [Portal for ArcGIS Operations Dashboard Security Patch](https://support.esri.com/en-us/patches-updates/2021/portal-for-arcgis-operations-dashboard-security-patch-7865) | 1 | 0 | active |
| 2021-04-29 | 2021 | ArcGIS GeoEvent Server | [ArcGIS GeoEvent Server Security Update 2021 Patch](https://support.esri.com/en-us/patches-updates/2021/arcgis-geoevent-server-security-update-2021-patch-7895) | 1 | 1 | active |
| 2021-05-05 | 2021 | ArcGIS Server | [ArcGIS Server Security 2021 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2021/arcgis-server-security-2021-update-1-patch-7879) | 6 | 0 | active |
| 2021-05-07 | 2021 | ArcGIS Server | [ArcGIS Runtime Local Server SDK General Security Patch.](https://support.esri.com/en-us/patches-updates/2021/arcgis-runtime-local-server-sdk-general-security-patch-7894) | 0 | 0 | active |
| 2021-07-13 | 2021 | Portal for ArcGIS | [Portal for ArcGIS Security 2021 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2021/portal-for-arcgis-security-2021-update-1-patch-7899) | 3 | 0 | active |
| 2021-09-23 | 2021 | ArcGIS Server | [ArcGIS Server Security 2021 Update 2 Patch](https://support.esri.com/en-us/patches-updates/2021/arcgis-server-security-2021-update-2-patch-7937) | 3 | 0 | active |
| 2022-03-14 | 2022 | ArcGIS Server | [ArcGIS Server Log4j Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-server-log4j-patch-7977) | 1 | 0 | active |
| 2022-03-15 | 2022 | ArcGIS GeoEvent Server | [ArcGIS GeoEvent Server 10.9.1 Patch 1 (Windows, Linux)](https://support.esri.com/en-us/patches-updates/2022/arcgis-geoevent-server-10-9-1-patch-1-windows-linux-7998) | 2 | 0 | active |
| 2022-03-15 | 2022 | ArcGIS Data Store | [ArcGIS Data Store Log4j](https://support.esri.com/en-us/patches-updates/2022/arcgis-data-store-log4j-7981) | 1 | 0 | active |
| 2022-03-15 | 2022 | ArcGIS GeoEvent Server | [ArcGIS GeoEvent Server 10.9 Patch 1 (Windows, Linux)](https://support.esri.com/en-us/patches-updates/2022/arcgis-geoevent-server-10-9-patch-1-windows-linux-7997) | 0 | 0 | active |
| 2022-03-17 | 2022 | ArcGIS GeoEvent Server | [ArcGIS GeoEvent Server 10.8.1 Patch 4 (Windows, Linux)](https://support.esri.com/en-us/patches-updates/2022/arcgis-geoevent-server-10-8-1-patch-4-windows-linux-8000) | 1 | 0 | active |
| 2022-03-18 | 2022 | ArcGIS GeoEvent Server | [ArcGIS GeoEvent Server 10.6.1 Patch 3](https://support.esri.com/en-us/patches-updates/2022/arcgis-geoevent-server-10-6-1-patch-3-8002) | 1 | 0 | active |
| 2022-03-30 | 2022 | ArcGIS Data Store | [ArcGIS Data Store Log4j Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-data-store-log4j-patch-7985) | 1 | 0 | active |
| 2022-03-31 | 2022 | ArcGIS Data Interoperability for Server | [ArcGIS Data Interoperability for Server Log4j Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-data-interoperability-for-server-log4j-patch-8017) | 1 | 0 | active |
| 2022-04-05 | 2022 | ArcGIS Workflow Manager Server | [ArcGIS Workflow Manager Server 10.9.1 Patch for Log4j](https://support.esri.com/en-us/patches-updates/2022/arcgis-workflow-manager-server-10-9-1-patch-for-log4j-8020) | 1 | 0 | active |
| 2022-04-20 | 2022 | Portal for ArcGIS | [Portal for ArcGIS Log4j Patch](https://support.esri.com/en-us/patches-updates/2022/portal-for-arcgis-log4j-patch-7969) | 1 | 0 | active |
| 2022-04-29 | 2022 | ArcGIS Notebook Server | [ArcGIS Notebook Server Security Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-notebook-server-security-patch-8010) | 1 | 1 | active |
| 2022-05-05 | 2022 | ArcGIS GeoEnrichment Server | [ArcGIS GeoEnrichment Server Log4j Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-geoenrichment-server-log4j-patch-8026) | 1 | 0 | active |
| 2022-07-22 | 2022 | ArcGIS Server | [ArcGIS Server Map Service Security 2022 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-server-map-service-security-2022-update-1-patch-8042) | 1 | 0 | active |
| 2022-09-01 | 2022 | ArcGIS Server | [ArcGIS Server Security 2022 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-server-security-2022-update-1-patch-8043) | 5 | 0 | active |
| 2022-10-04 | 2022 | ArcGIS Server | [ArcGIS Server Security 2022 Update 2 Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-server-security-2022-update-2-patch-8064) | 1 | 0 | active |
| 2022-10-10 | 2022 | Portal for ArcGIS | [Portal for ArcGIS QuickCapture Security Patch](https://support.esri.com/en-us/patches-updates/2022/portal-for-arcgis-quickcapture-security-patch-8051) | 1 | 0 | active |
| 2022-10-14 | 2022 | ArcGIS Server | [ArcGIS Server Directory Traversal Vulnerability Patch](https://support.esri.com/en-us/patches-updates/2022/arcgis-server-directory-traversal-vulnerability-patch-8063) | 1 | 0 | active |
| 2023-06-23 | 2023 | ArcGIS Insights (Desktop) | [ArcGIS Insights Security Patch for ArcGIS Insights 2022.1](https://support.esri.com/en-us/patches-updates/2023/arcgis-insights-security-patch-for-arcgis-insights-2022-1-8104) | 1 | 0 | active |
| 2023-07-20 | 2023 | ArcGIS Server | [ArcGIS Server Security 2023 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2023/arcgis-server-security-2023-update-1-patch) | 2 | 0 | active |
| 2023-11-20 | 2023 | ArcGIS Server | [ArcGIS Server Map and Feature Service Security 2023 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2023/arcgis-server-map-and-feature-service-security-2023-update-1-patch) | 1 | 0 | active |
| 2024-03-21 | 2024 | Portal for ArcGIS | [Portal for ArcGIS Enterprise Sites Security Patch](https://support.esri.com/en-us/patches-updates/2023/portal-for-arcgis-enterprise-sites-security-patch) | 1 | 0 | active |
| 2025-01-14 | 2025 | Portal for ArcGIS | [Portal for ArcGIS Security 2024 Update 2 Patch](https://support.esri.com/en-us/patches-updates/2024/portal-for-arcgis-security-2024-update-2-patch) | 12 | 0 | active |
| 2025-04-17 | 2025 | ArcGIS Server | [ArcGIS Server Security 2025 Update 1](https://support.esri.com/en-us/patches-updates/2025/arcgis-server-security-2025-update-1) | 25 | 0 | active |
| 2025-08-07 | 2025 | Portal for ArcGIS | [Portal for ArcGIS Enterprise Sites Security 2025 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2025/portal-for-arcgis-enterprise-sites-security-2025-update-1-patch) | 5 | 0 | active |
| 2025-10-07 | 2025 | ArcGIS Server | [ArcGIS Server Feature Services Security Patch](https://support.esri.com/en-us/patches-updates/2025/arcgis-server-feature-services-security-patch) | 1 | 0 | active |
| 2025-10-20 | 2025 | ArcGIS Web Adaptor | [ArcGIS Web Adaptor (IIS) Stability Patch](https://support.esri.com/en-us/patches-updates/2025/arcgis-web-adaptor-iis-stability-patch) | 0 | 0 | active |
| 2025-12-09 | 2025 | ArcGIS Server | [ArcGIS Server Security 2025 Update 2 Patch](https://support.esri.com/en-us/patches-updates/2025/arcgis-server-security-2025-update-2-patch) | 9 | 0 | active |
| 2025-12-11 | 2025 | Portal for ArcGIS | [Portal for ArcGIS Security 2025 Update 3 Patch](https://support.esri.com/en-us/patches-updates/2025/portal-for-arcgis-security-2025-update-3-patch) | 25 | 0 | active |
| 2026-02-10 | 2026 | ArcGIS Data Store | [ArcGIS Data Store 11.5 Reliability Patch](https://support.esri.com/en-us/patches-updates/2026/arcgis-data-store-11-5-reliability-patch) | 0 | 0 | active |
| 2026-02-25 | 2026 | ArcGIS Workflow Manager Server | [ArcGIS Workflow Manager Server 11.3 Patch 3](https://support.esri.com/en-us/patches-updates/2026/arcgis-workflow-manager-server-11-3-patch-3) | 0 | 1 | active |
| 2026-05-04 | 2026 | ArcGIS Server | [ArcGIS Server Security 2026 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2026/arcgis-server-security-2026-update-1-patch) | 2 | 0 | active |
| 2026-05-27 | 2026 | ArcGIS Server | [ArcGIS Server Security 2026 Update 2 Patch](https://support.esri.com/en-us/patches-updates/2026/arcgis-server-security-2026-update-2-patch) | 2 | 0 | active |
| 2026-05-28 | 2026 | Portal for ArcGIS | [Portal for ArcGIS Security 2025 Update 2 Patch](https://support.esri.com/en-us/patches-updates/2025/portal-for-arcgis-security-2025-update-2-patch) | 1 | 0 | active |
| 2026-06-04 | 2026 | Portal for ArcGIS | [Portal for ArcGIS Security 2026 Update 1 Patch](https://support.esri.com/en-us/patches-updates/2026/portal-for-arcgis-security-2026-update-1-patch) | 2 | 0 | active |
| 2026-06-23 | 2026 | Portal for ArcGIS | [Portal for ArcGIS Security 2026 Update 2 Patch](https://support.esri.com/en-us/patches-updates/2026/portal-for-arcgis-security-2026-update-2-patch) | 1 | 0 | active |
| 2026-07-21 | 2026 | ArcGIS Workflow Manager Server | [ArcGIS Workflow Manager Server 11.5 Patch 1](https://support.esri.com/en-us/patches-updates/2026/arcgis-workflow-manager-server-11-5-patch-1) | 0 | 1 | active |
| 2026-08-04 | 2026 | Portal for ArcGIS | [Portal for ArcGIS Security 2026 Update 3 Patch](https://support.esri.com/en-us/patches-updates/2026/portal-for-arcgis-security-2026-update-3-patch) | 13 | 0 | active |

## Per-year security totals (additive — each patch counts only its own new fixes)

| Year | Patches | Security-labeled bug fixes |
| --- | --- | --- |
| 2021 | 9 | 17 |
| 2022 | 17 | 21 |
| 2023 | 3 | 4 |
| 2024 | 1 | 1 |
| 2025 | 7 | 77 |
| 2026 | 9 | 21 |

## Per-product security summary (active patches only)

| Product | Patches | Security bugs fixed |
| --- | --- | --- |
| ArcGIS Data Interoperability for Server | 1 | 1 |
| ArcGIS Data Store | 3 | 2 |
| ArcGIS GeoEnrichment Server | 1 | 1 |
| ArcGIS GeoEvent Server | 5 | 5 |
| ArcGIS Insights (Desktop) | 1 | 1 |
| ArcGIS Notebook Server | 1 | 1 |
| ArcGIS Server | 17 | 61 |
| ArcGIS Web Adaptor | 1 | 0 |
| ArcGIS Workflow Manager Server | 3 | 1 |
| Portal for ArcGIS | 13 | 68 |

## Charts

Run `python make_charts.py` to (re)generate the three charts in `charts/`, plus a dark-mode twin of each in `charts/dark/`. They are intentionally rendered as standalone PNGs so they can be dropped into a slide deck. Each chart carries its own source line and methodology footnote, and every plotted value is also in `bug_counts.csv` so no number is reachable only through the picture.

| Chart | File | Story |
| --- | --- | --- |
| Patches released and security-labeled bug fixes per year | `charts/patches_and_fixes_per_year.png` | Patch cadence and security-fix volume tell different stories (2022 had the most patches; 2025 had the most fixes) |
| Security-labeled bug fixes by product | `charts/product_breakdown.png` | Portal for ArcGIS and ArcGIS Server account for 91% of all security fixes |
| Timeline of Portal and Server patches, sized by security-fix count | `charts/timeline.png` | Since 2025 a single patch has carried up to 25 security fixes — before that, never more than 6 |

## Notes

- Counts reflect only the *new* bugs each patch introduces. Esri patch pages also include cumulative "To avoid conflicts the <version> version also addresses:" re-lists of older fixes for backward-version compatibility; those re-lists are deliberately NOT counted, so a bug is only attributed to the patch that first addressed it. This means the per-year totals are directly additive (no double counting across patches).
- Security classification is keyword-based and conservative. Bugs labeled only as "ArcGIS Server has a security vulnerability" are counted as security even though the specific vulnerability class is not named in the patch page.
- The "Mentions w/o BUG-ID" column captures security-flavored fix lines that Esri wrote without a `BUG-000xxxxxx` identifier (e.g. Workflow Manager "Security vulnerability allowing Workflow Administrators to access encrypted user-defined setting values."). These are surfaced for completeness but are NOT added to the bug counts since there is no trackable identifier.
- For authoritative details on each fix, follow the patch URL and read the "Issues addressed with this patch" section.
