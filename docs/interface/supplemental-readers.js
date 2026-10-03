// Additive learner links only; course-native source and backend stay canonical.
export const supplementalReaders = [
  {
    courseId: 'C110', id: 'C110:released-pdf-mirror',
    href: 'https://github.com/KokunoYumeto/tea-time-numerical-analysis-id/releases/download/v3.0-id.2-r1/Tea-Time-Numerical-Analysis-id-ID.pdf',
    labels: {id: 'PDF edisi 3.0-id.2-r1 — 387 halaman', en: 'Edition 3.0-id.2-r1 PDF — 387 pages'},
    notes: {id: 'Salinan PDF rilis yang sama; sumber kumulatif menghasilkan kembali berkas ini byte-identik.', en: 'The same released Indonesian PDF; the cumulative source reproduces this file byte-for-byte.'},
    kind: 'companion', format: 'PDF', offlineAfterDownload: false,
    evidenceFile: 'docs/interface/evidence/c110-cumulative-source.json', contentLanguage: 'id',
    bytes: 8202487, sha256: 'd573b7233d0baa07381e2052a749757885db3a31fbfe695c5a4851ea42d91b6d'
  },
  {
    courseId: 'C110', id: 'C110:cumulative-tex',
    href: 'https://github.com/KokunoYumeto/tea-time-numerical-analysis-id/releases/download/v3.0-id.2-r1/TeaTimeNumericalAnalysis-id-ID.tex',
    labels: {id: 'LaTeX kumulatif lengkap — edisi 3.0-id.2-r1', en: 'Complete cumulative LaTeX — edition 3.0-id.2-r1'},
    notes: {id: 'Teks lengkap, termasuk latihan, solusi dan jawaban. Gunakan gambar, bibliografi dan gaya dalam ZIP sumber edisi yang sama.', en: 'Complete Indonesian text, including exercises, solutions and answers. Use the figures, bibliography and styles from the same edition’s source ZIP.'},
    kind: 'editable_source', format: 'TEX', offlineAfterDownload: false,
    evidenceFile: 'docs/interface/evidence/c110-cumulative-source.json', contentLanguage: 'id',
    bytes: 1271002, sha256: '45261d1ac680ded22b099f4925b7db5d7d7c8aed66c12045511d612c6fc5774e'
  },
  {
    courseId: 'C110', id: 'C110:released-source-archive',
    href: 'https://github.com/KokunoYumeto/tea-time-numerical-analysis-id/releases/download/v3.0-id.2-r1/Tea-Time-Numerical-Analysis-id-ID-v3.0-id.2-r1-source-backend.zip',
    labels: {id: 'ZIP sumber lengkap dan backend — edisi 3.0-id.2-r1', en: 'Complete source and backend ZIP — edition 3.0-id.2-r1'},
    notes: {id: '895 berkas rilis asli; sumber, gambar, bibliografi, gaya, backend, lisensi dan petunjuk build. Bukan EPUB atau paket pembaca HTML.', en: '895 original release files: source, figures, bibliography, styles, backend, licences and build instructions. Not an EPUB or HTML reader bundle.'},
    kind: 'source_archive', format: 'ZIP', offlineAfterDownload: false,
    evidenceFile: 'docs/interface/evidence/c110-cumulative-source.json', contentLanguage: 'id',
    bytes: 33244105, sha256: '0eebe482eec535942524d4e5cb1fb164b9ac7de07f2eb9421e0d7bf29fa7ee4c'
  },
  {
    courseId: 'B40', id: 'B40:original-en-partial-tex',
    href: 'https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/hefferon-linear-algebra/sources/00-linear-algebra-cumulative.tex',
    labels: {id: 'Sumber LaTeX kumulatif — 34 bagian bahasa Inggris', en: 'Cumulative editable LaTeX — 34 English sections'},
    notes: {id: 'Sumber lengkap untuk 34 bagian yang disajikan, bukan seluruh buku. Berkas pendukung dan petunjuk reproduksi tersedia dalam ZIP edisi yang sama.', en: 'Complete source for the 34 presented sections, not the entire book. Dependencies and reproduction instructions are in the same edition’s ZIP.'},
    kind: 'editable_source', format: 'TEX', offlineAfterDownload: false,
    evidenceFile: 'docs/interface/evidence/b40-original-english-reading.json', contentLanguage: 'en',
    bytes: 2379861, sha256: 'dcc6e3cdc1f8dec361760d02ef072c5a71fc1e4525b04738e7f8a991cd134f96'
  },
  {
    "courseId": "D20",
    "id": "D20:complete-companion-html",
    "href": "https://kokunoyumeto.github.io/functional-analysis-erdman-id/output/html-companion/index.html",
    "labels": {
      "id": "Solusi dan jembatan spektral — HTML lengkap",
      "en": "Complete solutions and spectral bridge — HTML"
    },
    "notes": {
      "id": "52 solusi latihan sumber, 10 solusi hasil kerja pembaca, dan jembatan spektral/SVD 13 unit. Bahan berbahasa Indonesia.",
      "en": "52 source-exercise solutions, 10 reader-work solutions, and a 13-unit spectral/SVD bridge. Material is in Indonesian."
    },
    "kind": "companion",
    "format": "HTML",
    "offlineAfterDownload": false,
    "evidenceFile": "docs/interface/evidence/d20-existing-readers.json",
    "contentLanguage": "id",
    "bytes": 5682,
    "sha256": "e3e615c98717eef968097044f1feb00afc61175f29f4e4cc346685db5c512984"
  },
  {
    "courseId": "D20",
    "id": "D20:complete-offline-html",
    "href": "https://zenodo.org/records/22088947/files/functional-analysis-erdman-id-2026.08.25-backend-artifact-reconciliation-source-backend-html.zip?download=1",
    "labels": {
      "id": "Buku dan pendamping HTML luring — ZIP",
      "en": "Offline textbook and companion HTML — ZIP"
    },
    "notes": {
      "id": "Paket yang sudah terbit juga memuat sumber/backend. Ekstrak seluruh ZIP; dalam folder buku, buka output/html/index.html atau output/html-companion/index.html. Pertahankan folder. Kutipan eksternal tetap memerlukan internet.",
      "en": "This existing package also contains source/backend files. Extract the whole ZIP; inside the book folder, open output/html/index.html or output/html-companion/index.html. Keep the folders. External citations still require internet."
    },
    "kind": "portable_html",
    "format": "HTML ZIP",
    "offlineAfterDownload": true,
    "evidenceFile": "docs/interface/evidence/d20-existing-readers.json",
    "contentLanguage": "id",
    "bytes": 3793368,
    "sha256": "ac5b3ec1fe7c2cf0a17eacce29c920ca5976c0c7d15e37f0ba0476afe9c48e32"
  },
  {
    "courseId": "B10",
    "id": "B10:complete-html-download",
    "href": "https://zenodo.org/records/22060439/files/MATEMATIKA_DISKRET_EDISI_KEEMPAT_ID_HTML.zip?download=1",
    "labels": { "id": "Paket HTML lengkap — ZIP", "en": "Complete HTML download — ZIP" },
    "notes": {
      "id": "Ekstrak ZIP, lalu buka matematika-diskret-id-html/index.html. MathJax dan fitur daring memerlukan internet; gunakan PDF untuk membaca luring.",
      "en": "Unzip and open matematika-diskret-id-html/index.html. MathJax and online features require internet; use the PDF for offline reading."
    },
    "kind": "html_download",
    "format": "HTML ZIP",
    "offlineAfterDownload": false,
    "evidenceFile": "docs/interface/evidence/b10-existing-readers.json",
    "contentLanguage": "id",
    "bytes": 7309181,
    "sha256": "58f73b309e6421dcc687638fe9ae0727de2dd311a022bb0e593bc31070d5f360"
  },
  {
    "courseId": "D90",
    "id": "D90:original-02-central-html",
    "href": "https://kokunoyumeto.github.io/program-matematika-indonesia/readers/d90/original-02/",
    "labels": {
      "id": "Tranche Original-02 — HTML pusat",
      "en": "Original-02 tranche — central HTML"
    },
    "notes": {
      "id": "Pendamping parsial untuk materi Original-02. Ini bukan pembaca lengkap mata kuliah D90; gunakan sumber utama dan tautan asli untuk cakupan penuh.",
      "en": "A partial companion for the Original-02 material. This is not the complete D90 course reader; use the primary resource and original-source links for full coverage."
    },
    "kind": "companion",
    "format": "HTML",
    "offlineAfterDownload": false,
    "evidenceFile": "docs/interface/evidence/d90-central-original-02.json",
    "contentLanguage": "id",
    "bytes": 190680,
    "sha256": "d867f4551cf05e531cc6f53336a55b9ba3ee0dfffbc4acede425e1bceae82a24"
  }
];
