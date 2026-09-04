# Multilingual learner interface

The canonical learner routes are `/id/` and `/en/`. The old root remains a compatible entry, with language links preserving course fragments. Future BCP 47 language/script routes are siblings, not nested translations of Indonesian.

This interface reads the existing `courses.js`, live publication overlay, delivery/tool projections, and learner-state module. It does not regenerate the modular backend, change corpus ownership, or claim that a resource is available in a language merely because the interface uses that language.

One graph: 40 course IDs, 83 prerequisite edges. Locale copy cannot change them. Both routes, both standalone maps and both paired-package maps use the same renderer. Static cards stay available when JavaScript is missing or initialization fails. Local progress is shared between languages on the same origin; export/import supports moving records between origins, devices, and offline files. File-URL storage sharing is browser-dependent, not promised.

The integrated `learner-reader-actions-v1.json` is also consumed at build time without changing it. Its seven receipt-bound CLP PDF actions (4,077 pages) take precedence over dated catalog PDF links. Reader labels are localized, while the actual books stay labeled Indonesian. Whole-file links do not imply chapter anchors or native HTML. Verified self-contained PDFs are labeled usable offline after a separate download. Source/backend archives remain secondary to reader actions. The projection's source hash and all action hashes are included in the interface build receipt.

The interface-only `final-editions.json` refreshes A10, A20, A30, B95, C140 and D100 from completed-edition evidence. All 14 linked reader files/entries were anonymously streamed and SHA-256 verified (938,805,819 bytes; eight PDFs totaling 9,886 edition pages). It preserves C140's independent Random supplements and exposes its completed C5 companion; D100 exposes both complete source courses plus the editorial bridge. Only named obsolete checkpoint links are suppressed. Current source/backend downloads remain available through each final edition archive. The older catalog and all backend artifacts remain unchanged; this is a link/presentation correction, not a new translation or backend admission.

No HTML textbook is invented for A20, A30 or B95. The D100 HTML files are explicitly labeled downloads, not a verified current GitHub Pages edition or a promise of offline dependency closure. Its PDF downloads remain usable offline. The C140 companion's separately verified offline package is labeled accordingly.

Cross-tab progress synchronization responds only to this application's local-storage key. If a write fails, in-memory progress is retained rather than discarded by another tab's storage event; export remains available.

## Build boundaries

`pnpm build` validates the already-admitted learner projection and interface, creates static/offline pages, synchronizes the hosted mirror, and compiles the site. `pnpm build:interface` runs only the bounded multilingual generation and unit tests.

The previous backend-production pipeline remains intact as `pnpm build:backend`. It includes historical admission/replay checks and all capsule mutation tests. It is not an interface-generation prerequisite: the historical admission script assumes a particular private workspace location, and the source snapshot also references a missing `B10_PUBLIC_NATIVE_BACKEND_EVIDENCE_20260831.json`. Those backend producer checks have not been claimed as passing here. No admission, schema, or backend-validator logic has been weakened.

The backend integrator's published CLP follow-through corrected the earlier nine-versus-thirteen live-adapter assertion. That independent work is preserved when rebuilding these pages. Interface QA does not substitute for the backend producer's admission and replay evidence.

## Language binding

### Paired access: program reader and original source

All 40 course cards expose their identified original book/course sources outside collapsed details, in both interfaces and all offline maps. Existing English upstream links are labeled **Original source**, not mistaken for program-hosted mirrors. `original-sources.js` adds German Brenner course sources, Wen-Wei Li's Chinese author/book page, and the original Indonesian homes of the program-authored B80/D120 works. D100 preserves both the 2025–2026 and 2012 source courses plus BGK 2019–2020; this is not a new English reader or a change to its owner pause.

These links identify original spines and explicitly listed components, not the origin of every program-authored companion. Source sites can advance independently of frozen editions. Exact revisions, licenses, authorship, component rights and corrections remain in each edition's existing provenance. No source site is presented as endorsing an adaptation. German and Chinese links do not create new interface routes or imply that those originals are locally mirrored.

The language-independent access contract is two-track: every course/language should expose both a program-hosted readable copy and a prominent author/publisher source link. Mirror coverage remains incomplete, but original-source links remain visible when a mirror is added. Five roles have mapped program-published English editions; D100 has no mapped public English edition. These are interface binding categories, not a new census of translation completion. A hosted HTML mirror is distinct from a hosted PDF, and adding one does not claim a new translation.

A00 and A10 are the first two verified original-English mirrors under that policy. Their program-hosted readers preserve all 75 and 82 OpenStax modules respectively, native IDs, MathML, exercises, solutions, original credits, and CC BY-NC-SA 4.0 component distinctions. Each OpenStax publisher page remains a separate prominent action. Each self-contained HTML ZIP works after extraction without JavaScript or remote rendering; external citations and OpenStax services still require internet. These are presentation mirrors of frozen original English sources, not translations or evidence that the remaining roles are mirrored.

The offline payload stores the effective catalog once instead of duplicating historical and live catalogs. All original inputs remain hash-bound. Tests compare every effective course and resolved resource between online and offline execution, retaining size budgets, all six static pages, navigation and progress behavior.

`locales.js` records English source/edition links and explicit exceptions. Missing English bindings are a discovery state, not a statement about Indonesian translation completion. Original Indonesian companions remain visible with their actual language. English upstream spines are not represented as containing those original companions.

Current bindings cover 39 course roles. The earlier D70/D80 omissions were discovery errors: their independent English editions were already complete in separate English repositories. D70 now links the complete 457-page Li Volume 1 plus the 102-page Duncan, 68-page selected CRing, and 7-page original study/mastery readers (634 pages total). D80 links corrected Volume 2 r2: 146 units, two mastery bridges, 820 PDF pages and a complete HTML reader. Each PDF is hash-bound; the current HTML identity is retained in the resource row. D70's four public PDFs and D80's pinned GitHub PDF/Pages HTML were freshly read back on 2026-09-04. D80's Zenodo r2 receipt is historical; fresh Zenodo PDF access returned 403, so the immediate PDF action uses the verified pinned GitHub bytes. The DOI remains linked. Both language interfaces expose these actual English editions without changing the Indonesian counterparts.

B80 and D50 also already had complete English editions. B80 now links its 14-unit HTML reader and 161-page PDF, including all 75 exercises, hints and solutions. D50 now links its 658-page complete English PDF and 41-file HTML ZIP: all 29 lecture/worksheet pairs, ten exam/solution forms and both bridges. The ZIP bundles local media but loads MathJax 3.2.2 externally; it is not labeled fully offline. Fresh anonymous byte/hash readback of these four reader artifacts passed on 2026-09-04. These are link corrections, not new translations. D100 remains an unresolved English-main-reader binding, not a demonstrated missing translation. D120 has an existing complete English edition at its `/en/` reader. Remaining original-companion bindings require checking existing English work; the audit task coordinates any genuine gaps without duplicate translation. The exception list retains the dated 403 observation for the official C120 English host.

## B80 capability handoff

The interface consumes the audit's two new B80 actions from `course-capsules.json` through a hash-checked, build-time projection. It preserves the five legacy tools without rewriting their backend file. B80's learner and teacher pages share 14 units, 75 exercises (72 core; three require additional prerequisites), four laboratories and native stable IDs. Both destinations are Indonesian, including when linked from the English interface. They do not run Python/SageMath, grade work, or provide offline copies of externally linked lessons.

The preserved packet is `B80_NATIVE_LEARNING_CAPABILITY_V1.zip`, SHA-256 `a80132e761fa1c2d09aebe264aa3f0efc890bd2922c9dd50e0d5f90fcfcebf3a`. Its contract is `course-learning-capability/1`, not a new 2.3.1 claim. It retains all 326 native catalog records. The original packet's historical `docs/id/index.html` is an embedded snapshot, not a replacement for these current bilingual pages. Source/hash validation and later public readback remain separate from the native validation receipt's historical publication flag.

## Offline scope

### Existing reader additions

Additive `supplemental-readers.js` rows expose already-published reader resources without changing course identity, primary routes, corpus publication state or common backend capabilities. Each row is bound to anonymous byte-verification evidence; its material language stays Indonesian in both interfaces. D20 retains its existing primary chapter map and complete 298-page PDF, while adding the complete companion HTML and existing combined source/backend/HTML ZIP. The two archived readers contain 37 HTML documents and 13,481 MathML elements, with 4,058 resolved local references and no external rendering dependencies. Extract the complete ZIP and keep its directory layout; external citations still need internet. No new translation, repackaged corpus or new backend admission is implied.

B10 also gains its existing complete HTML ZIP (1,229 files, including 553 HTML documents), without replacing its primary online reader or complete 613-page PDF. Unlike D20, this ZIP loads MathJax and interactive features externally: both language interfaces explicitly say it requires internet and do not label it offline-ready. After extraction, open `matematika-diskret-id-html/index.html`. The compact public evidence binds the full local archive-audit receipt, verified download and dependency limitation; it does not claim browser testing or a newly self-contained edition.

Each `learning-map.html` embeds the catalog, presentation, scripts, and CSS. It is an offline navigator, not an archive of all linked books. External resources require a connection unless downloaded separately. There are no remote runtime dependencies. Language switching from an independently downloaded file points to the corresponding public language route.

The bilingual ZIP also includes `docs/id/learning-map-paired.html` and `docs/en/learning-map-paired.html`. `START-HERE.html` opens these paired copies. Their static language links point to each other locally, including without JavaScript; retain the extracted directory layout. Individual standalone downloads keep their online language fallback and need no sibling files. The live pages expose the existing central DOI download page for the full ZIP.

Navigation carries only the current q/topic/level/show filters and fragment. The view is maintained independently of history writes, so switching language still reflects current filters when an offline browser refuses `replaceState`. Learner progress, placement, equivalence and waiver records are not serialized into navigation links. Moving local progress between isolated file contexts uses the existing export/import controls.

The build receipt records input/output hashes and all resolved resource bindings. The bounded test executes all four offline variants without a browser and checks actual rendered language anchors, static package closure, Windows file paths, non-ASCII paths, rejected history writes, graph identity, fragments, safe URLs, filtering, navigation history, cross-language progress, unavailable storage, and byte budgets. Browser visual QA is not claimed.
