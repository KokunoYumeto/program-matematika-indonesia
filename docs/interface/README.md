# Multilingual learner interface

The canonical learner routes are `/id/` and `/en/`. The old root remains a compatible entry, with language links preserving course fragments. Future BCP 47 language/script routes are siblings, not nested translations of Indonesian.

This interface reads the existing `courses.js`, live publication overlay, delivery/tool projections, and learner-state module. It does not regenerate the modular backend, change corpus ownership, or claim that a resource is available in a language merely because the interface uses that language.

One graph: 40 course IDs, 83 prerequisite edges. Locale copy cannot change them. Both routes and both offline maps use the same renderer. Static cards stay available when JavaScript is missing or initialization fails. Local progress is shared between languages on the same origin; export/import supports moving records between origins, devices, and offline files.

The integrated `learner-reader-actions-v1.json` is also consumed at build time without changing it. Its seven receipt-bound CLP PDF actions (4,077 pages) take precedence over dated catalog PDF links. Reader labels are localized, while the actual books stay labeled Indonesian. Whole-file links do not imply chapter anchors or native HTML. Verified self-contained PDFs are labeled usable offline after a separate download. Source/backend archives remain secondary to reader actions. The projection's source hash and all action hashes are included in the interface build receipt.

Cross-tab progress synchronization responds only to this application's local-storage key. If a write fails, in-memory progress is retained rather than discarded by another tab's storage event; export remains available.

## Build boundaries

`pnpm build` validates the already-admitted learner projection and interface, creates static/offline pages, synchronizes the hosted mirror, and compiles the site. `pnpm build:interface` runs only the bounded multilingual generation and unit tests.

The previous backend-production pipeline remains intact as `pnpm build:backend`. It includes historical admission/replay checks and all capsule mutation tests. It is not an interface-generation prerequisite: the historical admission script assumes a particular private workspace location, and the source snapshot also references a missing `B10_PUBLIC_NATIVE_BACKEND_EVIDENCE_20260831.json`. Those backend producer checks have not been claimed as passing here. No admission, schema, or backend-validator logic has been weakened.

The inherited full capsule-site validator also fails on its unchanged assertion of nine semantic adapters: the checked source projection already has thirteen. That assertion and its backend-production gate are preserved unchanged for the backend integrator; this interface does not claim to repair or certify that backend snapshot.

## Language binding

`locales.js` records English source/edition links and explicit exceptions. Missing English bindings are a discovery state, not a statement about Indonesian translation completion. Original Indonesian companions remain visible with their actual language. English upstream spines are not represented as containing those original companions.

Public-source checks on 2026-09-03/04 found direct English learning resources for 35 course roles. B80, D50, D70, D80, and D100 have no English main-reader binding in the scoped checks. D120 has an existing complete English edition at its `/en/` reader. The exception list also records original companion gaps and a 403 response from the official C120 English host.

## Offline scope

Each `learning-map.html` embeds the catalog, presentation, scripts, and CSS. It is an offline navigator, not an archive of all linked books. External resources require a connection unless downloaded separately. There are no remote runtime dependencies. Language switching from an independently downloaded file points to the corresponding public language route.

The build receipt records input/output hashes and all resolved resource bindings. The bounded test executes both standalone scripts without a browser and checks static coverage, graph identity, fragments, safe URLs, filtering, navigation history, cross-language progress, unavailable storage, and byte budgets. Browser visual QA is not claimed.
