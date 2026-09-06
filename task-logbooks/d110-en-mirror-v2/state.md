# D110 English mirror state

## Durable workflow

- Objective: create a bounded, original-English, program-hosted mirror of the checked-in `html/` subtree and `LICENSE` from `leanprover-community/mathematics_in_lean` at commit `dd6d752fedb14082f557913c2dccb2d4851e5173`, tree `757ef238a7e2ded30db5b3d388ff299fc28f23d5`, under `docs/en/courses/D110`.
- Write boundary: only the new `docs/en/courses/D110` subtree, the deterministic package `task-logbooks/d110-en-mirror-v2/package/D110-en-offline-dd6d752f.zip`, and this new logbook. Do not modify shared interfaces, manifests, validators, backend, release files, or Git state.
- Authority chain: the delegated request in `user-inputs.md`; GitHub commit and tree APIs for binding; the exact upstream Git blobs for source bytes; Apache-2.0 `LICENSE` from the bound commit.
- Production sequence: resolve and verify commit/tree; fetch the exact archive; verify every selected blob against the upstream Git object ID; materialize all selected files; inject mechanically reversible navigation at the top and bottom of every HTML page; add bounded attribution; write inventories; generate a deterministic offline ZIP.
- Validation gates: exact selected inventory; reversible upstream blob verification; local HTML/static/CSS link closure; fragment closure; no remote resource needed for core reading; required top/bottom reciprocal navigation and authoritative source link on every HTML page; license/attribution checks; two identical deterministic ZIP builds; complete SHA-256/byte inventory.
- Publication gate: none. Publication is explicitly excluded.
- Terminal condition: the mirror, package, inventory, validation report, and handoff receipt exist and every deterministic gate passes, or a concrete non-human operational failure is recorded with the next executable remedy.
- Resume paths: this file; `user-inputs.md`; `upstream-inventory.json`; `final-inventory.json`; `validation-report.json`; `handoff.md` in this directory.

## Current cursor — admitted mirror

- Status: complete; no package or publication exists.
- Verified upstream binding: `leanprover-community/mathematics_in_lean` commit `dd6d752fedb14082f557913c2dccb2d4851e5173` resolves to root tree `757ef238a7e2ded30db5b3d388ff299fc28f23d5`.
- Admission: `admit_standard_navigation.py` removed the exact legacy top and bottom blocks from all 16 pages: 32 blocks and 26,448 bytes. No `D110_PROGRAM_NAV`, `d110-program-nav`, or prematurely injected `data-central-surface-navigation` marker remains.
- Independent source proof: the local MathJax rewrite remains on 11 pages; reversing only that rewrite recovers the pinned source SHA-256 and Git blob SHA-1 for all 16 upstream HTML files.
- Rights: rendered book text says CC BY 4.0; repository code/build assets are Apache-2.0 under the retained root `LICENSE`; vendored MathJax is Apache-2.0 under `_vendor/mathjax/LICENSE`; retained components keep embedded notices.
- Final mirror: 207 files, 16 HTML documents, 33,125,251 bytes.
- Link validation: 1,001 local HTML/asset references, 437 fragments, and 23 CSS references checked; zero broken references and zero external core-resource dependencies.
- Validation: all eight deterministic gates passed with zero errors and zero warnings. See `admission-report.json`, `validation-report.json`, and `handoff.md`.
- Handoff state: all 16 pages are deliberately free of program navigation so the root coordinator can inject the standard `data-central-surface-navigation=v1` overlay.
- Limitation: no browser runtime/visual QA was performed because visible browser use was excluded. No shared interface/contract/release/Git file was changed.
