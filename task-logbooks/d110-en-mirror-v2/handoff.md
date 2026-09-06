# D110 English mirror — admitted handoff

## Outcome

The owned D110 mirror is admitted and ready for coordinator-owned standard navigation injection. All 16 HTML pages are free of the legacy custom navigation and do not yet contain `data-central-surface-navigation=v1`. Nothing was packaged or published. Shared interface, contract, release, backend, manifest, validator, and Git files were not modified.

## Upstream binding

- Repository: `leanprover-community/mathematics_in_lean`
- Commit: `dd6d752fedb14082f557913c2dccb2d4851e5173`
- Root tree: `757ef238a7e2ded30db5b3d388ff299fc28f23d5`
- Selected scope: exact checked-in `html/` subtree plus root `LICENSE`
- Source inventory: 100 blobs; 16 HTML documents; 13,152,549 bytes

## Admission result

- Script: `task-logbooks/d110-en-mirror-v2/admit_standard_navigation.py`
- Exact legacy blocks removed: 32, comprising one top and one bottom block on each of 16 pages
- Bytes removed: 26,448
- Legacy markers remaining: zero
- Coordinator standard-navigation markers present: zero
- MathJax local rewrite retained: 11 pages
- Independent upstream recovery: reversing only the MathJax URL rewrite recovers all 16 pinned upstream HTML SHA-256 hashes and Git blob SHA-1 object IDs
- Admitted mirror: 207 files; 16 HTML documents; 33,125,251 bytes

## Component-scoped rights

- Book text: CC BY 4.0, per the rendered copyright notice preserved on every HTML page: copyright 2020–2025, Jeremy Avigad and Patrick Massot.
- Repository code and build assets: Apache-2.0 under the retained upstream root `LICENSE`.
- Vendored `mathjax@4.1.3`: Apache-2.0 under retained `_vendor/mathjax/LICENSE`.
- Retained components keep their embedded copyright and license notices.
- `docs/en/courses/D110/UPSTREAM.md` states these scopes without applying the repository license to the book text.

## Deterministic validation

- Result: PASS; zero errors; zero warnings.
- Complete selected and vendored inventory: pass.
- Independent upstream HTML recovery: pass, 16/16.
- Legacy navigation removed and admission clear: pass, 16/16.
- Local MathJax rewrite retained: pass, 11/11 applicable pages.
- Local closure: 1,001 HTML/asset references, 437 fragments, and 23 CSS references; zero broken.
- External core-resource dependencies: zero.
- Component-scoped rights and attribution: pass.
- Package artifacts: absent, as required.

## Evidence and hashes

- `task-logbooks/d110-en-mirror-v2/admission-report.json`: 7,298 bytes; SHA-256 `786b4d8e0c4d1728707745c37279564b4077e574d68ccfec9ccb3a5b066fb864`
- `task-logbooks/d110-en-mirror-v2/upstream-inventory.json`: 71,455 bytes; SHA-256 `b972a52e35f6d90510815349999406d37a71a1cb3e1cde12fd3734ee36bfeb29`
- `task-logbooks/d110-en-mirror-v2/final-inventory.json`: 39,808 bytes; SHA-256 `4757f8226d581c0fa83dbd69d5c326806a1259c42476ac35c3a00d1ff3036d99`
- `task-logbooks/d110-en-mirror-v2/validation-report.json`: 2,376 bytes; SHA-256 `5b39efe717243b38b87035eb129bfd91fa7784ec743d5ac1e09caf7da1c6597b`
- `docs/en/courses/D110/UPSTREAM.md`: 1,664 bytes; SHA-256 `c4fc3704f9d0a16d669a8778bf80be33cc6cd6ddb5e40e08c41ba35d71ac706f`

## Coordinator next action

Inject the shared standard `data-central-surface-navigation=v1` overlay into the 16 admitted HTML pages. The coordinator should update the resulting final-byte inventory after that injection; the source-recovery proof remains valid if the standard overlay is deterministically removed before reversing the MathJax rewrite.

## Limitation

No visible browser/runtime visual check was run, as required. Evidence is static, byte-level, reversible, and offline-link complete. No Lean/Lake or TeX process was started.
