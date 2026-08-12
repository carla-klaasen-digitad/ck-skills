# Client Registry

Maps Danone USA brand names to their audit spreadsheet IDs. **Never use the wrong spreadsheet for a brand.**

## Active Audits

| Brand | Audit Spreadsheet ID | Output Folder ID | Audit Date | Notes |
|---|---|---|---|---|
| Danone North America | 1CQGjjezKvlxIgLcQe0mdqoMXmvY2u4wBoOmlsGtbH9E | 1R8hdsQr0gYlQU7dCLamCT89LXIN86o5E | 2025-12 | Reports largely complete as of April 2026 |
| Light + Fit | 121IdfgBkjVaees1G6xnLtrig9NHn56hiZGNmrtjvfgE | 1ykePmyRYv-RwxqVB9XgXgMgb0OP8YLEs | 2026-01 | Active — April 2026 |
| Oikos | 1u10YOkqM3E7tcKKF_uE196pxrwGjukLpL_y1Yv7AsPY | 14qABaxYAqy-YAR7OH8TX7h96yaTJmGj_ | TBD | Reports begin May 2026 |
| International Delight | 13s6hUPF0MVUm5kGZOC53NbQEB07ScelUQKvO9uYhbVk | 1cy3K1eFszPz7PIjhqz3rjlyUyf5y2Oih | TBD | Reports begin May 2026 |
| SToK | 1ZLEfNU-xw8TnX39jCQRFx4p8BRetBGFUzVmrzCBtSHM | TBD | TBD | Reports begin April 2026 |
| Too Good | 1gdjiifkJVlOPDCaGYHSncVoOWBuCrkEuQpJZeKlKHT0 | TBD | TBD | Reports begin March 2026 |
| Silk | 1nsn-ThmRAltcwR-xqm3FW66uCvEwf9NPo5Q4sSNui3Q | 11S0dUN4YLTWwf6MwltH77lZp7Rpk9wEq | 2025-Q4 | Q2 2026 report in progress |
| Evian | 1V9eET0RTtyLjsWjP9B8Bnf0LOfvUuSQlpWnwuw5DYvg | 1jn0usoIK1ZC5rD_1W4vVz5CqciIzWIVq | TBD | Performance report done (prior session) |
| Happy Family | TBD | TBD | TBD | Not yet started |
| Activia | 1gLSwEBpE7Usr8Cyj_eFtZgY4o7EUhO1TJFkH1C4NUzw | 1c_h2u1Xj2oV_X3ZWPtvgz4RWWkyEi48X | 2026-06 | Big Drive: 1ddux6YrnZWrg0HHYdfeHxF-twlr4NUm_ |
| Dannon | 1sYCZJV8Z3o1aMY6Nw1RBWUUSYH4aWxsUWn69UNbNrj0 | 10oazOzmQ4Ii8Gx-gld9DfWWtBHW6r5si | 2026-03 | Tier 3 |
| YoCrunch | 170sceAJr3wgvr532AYT2ZoDHGURHmiYXGY5gxcHhJUI | 1Tqvn97UfskZB3h5kOZBTI9YcdFcEqCRX | 2026-03 | Tier 3 |
| Danimals | 1U0Mg7WAr20vPD3sLBw2AhfOK5KcgOzltZNsB8lXGSSg | 17rATKAHD7D_DnpI-kewo17NunODhe1Vz | 2026-03 | Tier 3 |
| Dunkin' Creamers | 1_Lm66qr-n4wM6B3gC7221GTB1tgKCJM5n7e2cbi-xBk | 1XBolzAjDBqarO3op4jnUiRkem7HY-bzK | 2026-04 | Tier 3 |
| So Delicious Dairy Free | 1Tf7xXDUiUJZMy6ULURDz_zwG99Fe_pAi-C-I1G027qU | 1_2Lq2nNFleAPT8_Cb4z2QBEQTtvh7kNu | 2026-04 | Tier 3 |
| Follow Your Heart | 1KTtG46rMAnZ-myNqWidB_dT4oCzJt4y8mYYPojv-F5U | 1i3y43RAsU_v7qDWYzVLY6VcxvQ0Q4AnL | 2026-04 | Tier 3 |

## Production Plan Source

All upcoming reports tracked in: **2026 - SEO Production Plan - DANONE USA**
Spreadsheet ID: `13ZKd5UVG_OcvRS9Wri8c8XSbwqiCguiJBDvUuUN9hbg`
Tab: TECHNICAL & LOCAL (ALL) - Optimizations

## Technical Recommendations Delivery Tracker

After writing each technical recommendations doc, update:
- Spreadsheet ID: `1o526Qv4UzP_Qfe-cjrfvcA7jRUi6zUtd9Ecp2WPMIhQ`
- Tab: `Technical Recommendations ` (note trailing space — quote in range notation)
- Column A: Brand name | Column G: Q2 link | Column I: Q3 link | Column K: Q4 link
- **Always re-scan Column A for the brand row — never cache row positions** (rows shift as brands are added)

## Client Separation Rule

Before reading any audit data:
1. Confirm the brand with the user
2. Cross-check the spreadsheet ID in this registry
3. If the registry shows TBD, ask the user for the spreadsheet URL before proceeding
4. Never infer a spreadsheet ID from a previous brand's session

## CMS Notes (affects what issues to look for)

| Brand | CMS | Known CMS-specific issues |
|---|---|---|
| Danone North America | Adobe AEM | Internal CMS paths (/content/corp/noram/) surfacing publicly; recursive .html appending; dot instead of slash path separators |
| Activia | Adobe AEM | AEM internal paths: /crx/, /system/, /content/dam/ not blocked by default; BazaarVoice review pagination (?bvstate=pg:X/ct:r) creates uncanonicalized duplicates; product filter variants (?type=cups, ?type=dailies) require canonical tags; no parameter blocking in robots.txt on initial deployment |
| Light + Fit | WordPress | /wp-admin/, /wp-includes/ in robots.txt; wp-content/uploads/ legacy image 404s |
| Evian | Unknown | TBD |
| Others | Unknown | TBD — populate as first report for each brand is written |

## Link Policy by Brand

| Brand | Include links in report? |
|---|---|
| Danone North America | Yes |
| Light + Fit | No — user adds manually |
| Happy Family | No — user adds manually |
| Too Good & Co. | No — user adds manually |
| Silk | Yes |
| SToK | Yes |
| Activia | Yes — links confirmed Q2 2026 |
| Dannon | Yes — links confirmed Q2 2026 |
| YoCrunch | No — confirm with user |
| Danimals | No — confirm with user |
| Dunkin' Creamers | No — confirm with user |
| So Delicious Dairy Free | No — confirm with user |
| Follow Your Heart | No — confirm with user |
| Others | No — leave for manual insertion unless user explicitly confirms links should be included |
