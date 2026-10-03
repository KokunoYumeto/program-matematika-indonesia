B80 paired format repair and preservation

This adapter preserves the released Indonesian and English course content.
It does not rerun Python/Sage experiments, replace the native Quarto master,
translate the course again, or claim a fresh mathematical review.

Inputs: the exact native EPUB/source archives in outputs/b80-formats-20261003.
Pinned original EPUB hashes are in build_b80.py. The original releases remain:
https://github.com/KokunoYumeto/mathematical-computing-reproducible-experiments-id/releases/tag/v2026.08.22.1
https://github.com/KokunoYumeto/mathematical-computing-reproducible-experiments-en/releases/tag/v2026.08.31.en1

Derived PDF / direct cumulative LaTeX / full-source ZIP / repaired EPUB:
https://zenodo.org/records/23116530 (Bahasa Indonesia)
https://zenodo.org/records/23116541 (English)
These are versions of the original language-specific concepts, not new concepts.
The original records and every inherited download remain public and unchanged.

Production sequence:
1. build_b80.py: one invalid outer alt attribute repaired; all course bodies
   checked, then cumulative LaTeX exported through Pandoc 3.9.0.2.
2. test_build_b80.py: eleven tests, including loss-detection negative cases.
3. build_pdf.ps1: serialized XeLaTeX, no shell escape or package installation.
4. inspect_pdf.py: geometry/internal-link checks and Poppler page renderings;
   actual visual review is recorded separately, never inferred from compilation.
5. package_sources.py: exact editable LaTeX, EPUB tree, figure, manifests,
   component licences, and portable rebuild scripts in each 39-member ZIP.
6. Isolated REPRODUCE.ps1 and REBUILD_EPUB.py: byte-identical PDF/EPUB replay.
7. finalize.py: bind final bytes to preservation, geometry, visual and replay
   evidence. Source-stage pending flags remain historical, not final status.
8. publish_github.py and publish_zenodo.py: exact native release/concept targets;
   public inventory and anonymous byte/hash readback; no asset overwrite.
9. integrate.py: admit only verified URLs into the bilingual central hub.

The public evidence is docs/interface/evidence/b80-repaired-formats.json.
Each source ZIP independently rebuilds its paired PDF and EPUB. Native Quarto
sources are linked and retained separately; do not claim this derived source
reproduces the original PDF pagination or the Python/Sage experiment runtime.

Format repair/export/integration: OpenAI Codex - GPT-6 Astra, Ultra effort.
No human review is implied. Original credits and component licences apply.
