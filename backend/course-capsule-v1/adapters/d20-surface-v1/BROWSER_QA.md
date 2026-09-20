# D20 browser check — 2026-09-21

Tested the generated English teaching view in a hidden in-app browser. Exact-ID
search returned one exercise; selecting it enabled export. Opening the support
disclosure exposed its exact admitted companion-solution link. The actual JSON
download was structurally equal to an independently reconstructed plan for
`FAOA-2015-CH01-NODE-0003`, with one selected unit and one supporting unit.
Download size: 24,665 bytes. SHA-256:
`b5230ad0ba0789ab451551598fd87121c255d9715677acf4303cf595d267173d`.

Clearing selection and search restored 1–40 / 62 practice items; next page showed
41–62 / 62. The vector-space chapter-concept filter returned seven Chapter 1
practice items. Switching language opened the Indonesian teaching view with the
expected heading and 1–40 / 62 initial range. The browser warning/error log was
empty. The checked desktop document width equalled the viewport width. Rendered
screenshots were inspected for readable headings, notices and links.

Some browser-automation convenience locators did not resolve native summary or
label elements. Retargeting the observed DOM elements worked; no page exception
was observed. This is a desktop functional check, not a full mobile or
accessibility certification. No producer source or translation was changed.
