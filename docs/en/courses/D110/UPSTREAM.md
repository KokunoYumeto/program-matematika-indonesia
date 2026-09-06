# D110 · Mathematics in Lean — original English mirror

This directory is an additive, program-hosted mirror of the checked-in HTML edition of **Mathematics in Lean**, by Jeremy Avigad, Patrick Massot, and the Lean community.

- Authoritative original: https://leanprover-community.github.io/mathematics_in_lean/
- Upstream source: https://github.com/leanprover-community/mathematics_in_lean
- Bound commit: `dd6d752fedb14082f557913c2dccb2d4851e5173`
- Bound root tree: `757ef238a7e2ded30db5b3d388ff299fc28f23d5`
- Mirrored upstream scope: `html/` plus `LICENSE`
- Book text: CC BY 4.0, as stated in the rendered copyright notice retained on every HTML page.
- Repository code and build assets: Apache License 2.0 under the retained root [LICENSE](LICENSE).
- Retained components keep their embedded copyright and license notices.

Program navigation is intentionally absent from these admitted pages. The root coordinator owns injection of the standard `data-central-surface-navigation=v1` overlay. The build inventory in `task-logbooks/d110-en-mirror-v2/upstream-inventory.json` records the Git blob identity and SHA-256 of every source file; the validator reverses only the local MathJax URL rewrite and proves that every recovered HTML file matches its bound upstream Git blob.

For offline formula rendering, the inherited unpinned MathJax 4 CDN request is redirected to a complete local copy of npm package `mathjax@4.1.3`, verified against npm integrity `sha512-BN/8Pkgn7G1pIDYJqd9md+JHsE/jydSYbyOZnSdSA0WziuVO8mRxdYiWFumkVVly/8U+hm9DpIIoWuvySverzw==`. MathJax is Apache-2.0 licensed; its package metadata and license are retained in `_vendor/mathjax/`.
