# O014 source authority

Status: admitted primary corpus, frozen 2026-08-21.

## Primary authority

- Work: Wen-Wei Li, *Methods of Algebra, Volume 2: Linear Algebra*.
- Author-controlled books page: <https://wwli.asia/zh/docs/books/>.
- Authoritative repository: <https://gitee.com/wen-wei-li/AlJabr-2>.
- Official mirror: <https://github.com/wenweili/AlJabr-2>.
- The author's site policy says the Gitee copy prevails if mirrors differ.
- Branch: `master`.
- Commit: `9a5803ff77dd3257484cb177f851a73770a59dd3`.
- Tree: `23bd05c2fb8434278df4fdfb636559a6a2b0d2ff`.
- Commit timestamp/message: `2026-07-22T06:12:45+02:00`, `Minor revision`.
- Tags/releases: none; the commit and tree are therefore the edition anchors.

The Higher Education Press paper edition is the first edition of September
2024, ISBN `978-7-04-062754-1`. The author describes the downloadable edition
as an online edition that differs slightly from the paper edition. This lane
translates the pinned online edition, not an inferred reconstruction of print.

## Exact archive and tree

- Archive URL: <https://codeload.github.com/wenweili/AlJabr-2/zip/9a5803ff77dd3257484cb177f851a73770a59dd3>.
- Local archive: `authority/archives/AlJabr-2-9a5803ff77dd3257484cb177f851a73770a59dd3.zip`.
- ZIP bytes: `6257898`.
- ZIP SHA-256: `657346b78a07a27925ac8f6254483b6d46e956214ba23a7e4def393d929215eb`.
- Expanded repository: 35 files, 7,765,237 bytes.
- Per-file size/hash inventory: `AUTHORITY_FILE_MANIFEST.csv`.

The editable closure is flat and complete: main file, prelude, chapters 1-9,
two appendices, bibliography, custom class and style/configuration files,
Makefile, cover/license assets, editable errata, generated PDFs, and a separate
class template. `pre-prelude.tex` and the template are repository material but
are not included by `Al-jabr-2.tex`; they are not canonical reader text.

## Official PDF baseline

- Author PDF: <https://www.wwli.asia/downloads/books/Al-jabr-2.pdf>.
- Pinned repository PDF: `Al-jabr-2.pdf`.
- The two byte streams are identical.
- Bytes: `4307219`.
- SHA-256: `3e1b06656cf794321412b659de4ee5fb0a0177e62f1dc0fc484736c9cf57d58c`.
- Extent: 650 physical pages (two cover labels, six Roman pages, Arabic 1-642).
- PDF 1.7, unencrypted, creation date 2026-07-22.

Current errata is also byte-identical between the author download and pinned
repository: 3 pages, 98,206 bytes, SHA-256
`7a0a3483352ebc511b095f4bf08fad98476d89b7cf84fbf0100a608bf52d14b1`.

## Reader and pedagogy closure

The main file includes the prelude, chapters 1-9, and appendices A-B. The
course contains 194 top-level exercises and 117 embedded hints. Every chapter
and appendix ends with exercises. There is no answer section, solution
environment, solution file, or solution manual. The solution/mastery layer is
therefore an explicit authoring obligation, not a hidden upstream asset.

The main reader's diagrams are source-native TikZ/TikZ-CD. Its only raster
inclusion is `ccby.png`; `Lanzhou.png` belongs to the separate template. The
upstream provides LaTeX/PDF only: no HTML, EPUB, tagged PDF, MathML, or semantic
alternative text surface.

