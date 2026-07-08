# Pre-Write Checklist

Run through this before writing the Google Doc via the Python Docs API.

## Data Checks

- [ ] Correct audit spreadsheet confirmed for this brand (see CLIENT-REGISTRY.md)
- [ ] `getSpreadsheetInfo` called to confirm sheet names (sheet names may have trailing spaces)
- [ ] Header row read (A1:Q5) to confirm column positions
- [ ] All audit rows for this report type read (see REPORT-TYPES.md)
- [ ] All supplementary sheets provided by user have been read
- [ ] Column I (Score Explanation) read for all relevant rows — primary source for finding descriptions
- [ ] Key numbers extracted (counts, percentages, affected page totals)

## Scope Checks

- [ ] Clarifying questions answered before writing begins
- [ ] Confirmed which issues are in scope vs. deferred to another report
- [ ] Confirmed supplementary docs are the ones for this brand (not another brand's sheets)
- [ ] Any cross-report references identified and noted as italic placeholders in the draft

## Style Checks

- [ ] Title included as first H1 (for `firstHeadingAsTitle: true`)
- [ ] `*Complete SEO and GEO Audit:*` is second line (italic, no link)
- [ ] No Expected Outcome sections
- [ ] Overviews are short — lead with key metric, no preamble
- [ ] Recommended actions: 2–4 items per section, highest-impact only
- [ ] No domain names in prose — "the website" only
- [ ] URL examples are in italics
- [ ] URL examples are absolute (full https://...)
- [ ] Link policy checked for this brand (see CLIENT-REGISTRY.md)
- [ ] If robots.txt included: new disallow rules are bolded, existing ones are not
- [ ] Out-of-scope findings removed and replaced with `*See [Report Name] for details.*`
- [ ] Reference docs: max one per section
- [ ] Three-part structure used per section (H2/H3): **Problem:** / **Impact:** / **Fix:** — only label word bolded; Fix replaces Recommended Actions list
- [ ] No full URL lists — describe pattern + count + italic spreadsheet placeholder instead
- [ ] No verbose writing — every sentence leads with the finding, no preamble or explanatory filler
- [ ] Em-dash count is 2 or fewer for the entire document
- [ ] No text immediately after a hyperlink on the same line

## Google Sheets Cautions

- [ ] NEVER use ARRAYFORMULA + LET() combination — confirmed to produce #ERROR in Google Sheets
- [ ] If writing classification values to a sheet column: use static text values row-by-row with `valueInputOption: "RAW"`
- [ ] Sheet names with trailing spaces must be quoted in range notation: `'Sheet Name '!A1:Z20`

## Post-Write

- [ ] Poppins font applied via `updateTextStyle` (startIndex: 1, endIndex: [endIndex from GET /documents/{DOC_ID} - 1])
- [ ] Report character count and section structure to user
- [ ] Note any data gaps (supplementary sheets not provided)
- [ ] Note any cross-report placeholders left for user to fill in
