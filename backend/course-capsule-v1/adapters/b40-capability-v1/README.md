# B40 common capability adapter

Thin zero-copy learner and educator capability index derived from the R005 Hefferon Linear Algebra backend for `course-learning-capability/1`. It is not a second full backend: it selects identifiers, navigation metadata, locators, hashes, rights, and receipt evidence while preserving all 3,541 stable unit IDs, all 13,999 native relation IDs, the 1,037-by-1,037 exercise-answer bijection, 114 concepts and terms, 307 corrections, 11 component-specific rights records, and eight exact native artifact identities.

The learner route spans the textbook, answer-book shell, and Sage lab with their 17 chapters and 57 sections. The educator selector distinguishes 1,035 native upstream answers from two Indonesian-edition-supplied answers authorized by HLA-A0300. Three damaged extracted headings have transparent presentation-only normalizations; their native titles, locators, and hashes remain alongside them. Historical native publication status is dated separately from current status reported by the locked anonymous readback. No segment or book body is copied, and no prerequisites, outcomes, semantic textbook HTML, EPUB, tagged-PDF, MathML, or accessibility conformance are invented or claimed.

Terms are canonical in `data/concept-index.json`; corrections are canonical in `data/ledger-references.json`; `data/rights-and-terms.json` references those stores rather than duplicating their rows. The 11 native rights records remain component-specific and are not collapsed into a blanket license.

The existing lossless common migration receipt is referenced, not replayed into an 83.9 MB duplicate. Run `python -B scripts/build_b40_capability_v1.py` and then `python -B scripts/validate_b40_capability_v1.py` from the central project root.
