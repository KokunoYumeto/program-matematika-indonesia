// The versioned curriculum authority remains immutable. This overlay exposes
// newer, independently verified owner publications between central releases.
// It also records distinct translation, integration, canonical, and public
// boundaries so that a translated helper packet is never presented as an
// admitted learner edition.

const hasOwn = (value, key) => Object.prototype.hasOwnProperty.call(value, key);

function publication(value) {
  const frozen = { ...value };
  if (value.progress) frozen.progress = Object.freeze({ ...value.progress });
  for (const field of ['supplements', 'additionalSupplements']) {
    if (value[field]) frozen[field] = Object.freeze(value[field].map((item) => Object.freeze({ ...item })));
  }
  return Object.freeze(frozen);
}

export const liveCoursePublications = Object.freeze({
  A10: publication({
    state: 'production',
    edition: 'https://zenodo.org/records/22143518/files/00-elementary-algebra-2e-bahasa-indonesia-EA2-S0032-reader.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22143518',
    repository: 'https://github.com/KokunoYumeto/openstax-elementary-algebra-2e-id',
    version: '0.11.0-wip',
    note: 'Seluruh 82 modul telah diterjemahkan, diintegrasikan ke kanon, dan diekspor sebagai backend 449.680-rekaman yang lolos dua pembangunan ulang identik serta 28/28 pengujian. Pembaca lengkap masih menjalani pembangunan dan QA; edisi publik tetap checkpoint EA2-S0032 yang memuat 32 modul tidak kontigu dalam 1.011 halaman.',
    progress: {
      unitLabel: 'modul OpenStax',
      totalUnits: 82,
      translationBearingUnits: 82,
      integrationReadyUnits: 82,
      canonicalUnits: 82,
      publicUnits: 32,
      publicPages: 1011,
      publicBoundary: 'EA2-S0032 — 32/82 modul tidak kontigu; pembaca lengkap belum publik',
      updatedAt: '2026-08-29T16:29:50+02:00',
    },
  }),
  A20: publication({
    state: 'production',
    edition: 'https://zenodo.org/records/22142022/files/openstax-intermediate-algebra-2e-id-ID-0.3.0-wip-reader.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22142022',
    repository: 'https://github.com/KokunoYumeto/openstax-intermediate-algebra-2e-id',
    version: '0.3.0-wip',
    note: 'Checkpoint publik memuat 48 dari 83 modul berurutan dalam pembaca 1.977 halaman. Kanon lokal telah mencapai 51 modul, sedangkan gabungan keluaran terjemahan tersegel mencapai 73 modul; bagian yang belum diintegrasikan bukan edisi publik.',
    progress: {
      unitLabel: 'modul OpenStax',
      totalUnits: 83,
      translationBearingUnits: 73,
      canonicalUnits: 51,
      publicUnits: 48,
      publicPages: 1977,
      publicBoundary: '48/83 modul berurutan; akhir Bab 7',
      updatedAt: '2026-08-29T11:29:02+00:00',
    },
  }),
  A30: publication({
    state: 'production',
    edition: 'https://zenodo.org/records/22160769/files/OpenStax-Precalculus-2e-id-ID-0.1.0-alpha.38-reader.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22160769',
    repository: 'https://github.com/KokunoYumeto/openstax-precalculus-2e-id',
    version: '0.1.0-alpha.38-reader.1',
    note: 'Seluruh 87 modul memiliki terjemahan, 79 telah menjadi masukan integrasi, 49 berada dalam kandidat kanon pemilik, dan 38 telah diterbitkan. Edisi publik alpha.38 memuat 1.215 halaman sampai m49384; kandidat alpha.49 masih menjalani QA visual dan belum menjadi edisi publik.',
    progress: {
      unitLabel: 'modul OpenStax',
      totalUnits: 87,
      translationBearingUnits: 87,
      integrationReadyUnits: 79,
      canonicalUnits: 49,
      publicUnits: 38,
      publicPages: 1215,
      publicBoundary: '38/87 modul berurutan; sampai m49384',
      updatedAt: '2026-08-29T14:00:00+02:00',
    },
  }),
  B30: publication({
    state: 'production',
    edition: 'https://zenodo.org/records/22151145/files/CLP-2_Kalkulus_Integral_Bahasa_Indonesia_checkpoint_2026-08-29_s3.7.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22151145',
    repository: null,
    version: '2026.08.29-wip.18',
    note: 'Checkpoint publik WIP.18 mencapai akhir Bagian 3.7 dalam pembaca 1.203 halaman. Tidak ada repositori CLP2 publik yang terverifikasi; CLP3 diterjemahkan oleh pembantu tetapi masih menjalani penerimaan kanonis pemilik.',
    progress: {
      unitLabel: 'bagian CLP2',
      publicPages: 1203,
      publicBoundary: 'WIP.18 — akhir Bagian 3.7',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  B50: publication({
    state: 'production',
    note: 'Ke-138 permukaan sumber CLP3 telah memperoleh keluaran terjemahan pembantu, tetapi penerimaan pemilik belum selesai karena lima kegagalan validator yang terikat isu. Belum ada unit kanonis atau edisi publik; berkas pembantu tidak ditautkan sebagai bahan belajar.',
    progress: {
      unitLabel: 'permukaan sumber CLP3',
      totalUnits: 138,
      translationBearingUnits: 138,
      integrationReadyUnits: 0,
      canonicalUnits: 0,
      publicUnits: 0,
      publicBoundary: 'belum ada edisi kanonis atau publik',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  B95: publication({
    state: 'production',
    learner: 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/B95/',
    edition: 'https://zenodo.org/records/22148827/files/00_STATISTIKA_BERBASIS_DATA_ID_R011-B021_WORKING_READER.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22148827',
    repository: 'https://github.com/KokunoYumeto/statistika-berbasis-data-id',
    release: 'https://github.com/KokunoYumeto/statistika-berbasis-data-id/releases/tag/r011-b021-2026.08.28.1',
    version: 'R011-B021',
    note: 'Edisi kerja publik R011-B021 memuat Bab 1 sampai Bab 5, Bagian 5.3, dalam pembaca 216 halaman. B022 telah diterjemahkan tetapi belum diterima atau diterbitkan.',
    progress: {
      unitLabel: 'batas produksi R011',
      publicPages: 216,
      publicBoundary: 'B021 — Bab 5, Bagian 5.3',
      updatedAt: '2026-08-28T00:00:00+02:00',
    },
  }),
  C10: publication({
    state: 'published',
    edition: 'https://zenodo.org/records/22105195/files/Analisis_Dasar_I_Bahasa_Indonesia_v6.3.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22105195',
    repository: 'https://github.com/KokunoYumeto/lebl-mathematics-family-id',
    note: 'Analisis Dasar Jilid I lengkap dan tetap tersedia sebagai pembaca 334 halaman pada rilis U397. Sumber dan backend publik keluarga Lebl telah maju ke U420; U421 masih lokal dan tidak mengubah pembaca lengkap ini.',
    progress: {
      unitLabel: 'jilid Analisis Dasar I',
      totalUnits: 1,
      translationBearingUnits: 1,
      integrationReadyUnits: 1,
      canonicalUnits: 1,
      publicUnits: 1,
      publicPages: 334,
      publicBoundary: 'pembaca lengkap U397; sumber/backend keluarga U420',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  C90: publication({
    state: 'production',
    reader: 'https://kokunoyumeto.github.io/topology-an-inquiry-based-approach-id/o003-c90-chapters-01-17-reader.html',
    edition: 'https://zenodo.org/records/22151429/files/topologi-pendekatan-berbasis-inkuiri-bab-01-17-id.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22151429',
    repository: 'https://github.com/KokunoYumeto/topology-an-inquiry-based-approach-id',
    version: '2026.08.29-bab01-17',
    note: 'Bab 1–17 dari 20 telah diterbitkan dalam pembaca 513 halaman. Bab 18 beserta pendamping 136 entri telah selesai diterjemahkan tetapi belum diterbitkan; Bab 19 sedang diterjemahkan.',
    progress: {
      unitLabel: 'bab',
      totalUnits: 20,
      translationBearingUnits: 18,
      integrationReadyUnits: 17,
      canonicalUnits: 17,
      publicUnits: 17,
      publicPages: 513,
      publicBoundary: 'Bab 1–17',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  C100: publication({
    state: 'published',
    learner: 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/',
    reader: 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/C100/reader/',
    edition: 'https://zenodo.org/records/22102628/files/BIDANG_EUKLIDES_DAN_KERABATNYA_ID_SPINE_COMPLETE.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22102628',
    repository: null,
    version: '2026.08.25-complete-course-a11y-ch20-portable',
    note: 'Kursus utama lengkap tetap terbuka melalui rute belajar pusat. Buku kerja Clemens/Snapp pada lini lisensi terpisah juga telah selesai seluruh 22 unit; repositori edisi khusus belum tersedia dan karena itu tidak ditautkan.',
    supplements: [
      {
        id: 'clemens-snapp-workbook-u022',
        title: 'Buku kerja geometri dua dimensi — lengkap 22/22 unit',
        resourceType: 'workbook',
        state: 'complete',
        scope: 'Seluruh 22 unit, pembaca 276 halaman; lini lisensi terpisah dari kursus utama.',
        license: 'CC BY-NC-SA 4.0',
        pages: 276,
        url: 'https://zenodo.org/records/22151703/files/buku-kerja-geometri-dua-dimensi-id-unit001-022.pdf?download=1',
        zenodo: 'https://doi.org/10.5281/zenodo.22151703',
        conceptDoi: 'https://doi.org/10.5281/zenodo.22105519',
        bytes: 1143531,
        sha256: '436239ee2918f2ea43538c665aa9241ea207474e9c9ffcfc599121115ed1a90b',
      },
    ],
    progress: {
      unitLabel: 'bab kursus utama',
      totalUnits: 20,
      translationBearingUnits: 20,
      integrationReadyUnits: 20,
      canonicalUnits: 20,
      publicUnits: 20,
      publicPages: 226,
      publicBoundary: 'kursus utama 20/20; buku kerja terpisah 22/22',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  C140: publication({
    state: 'production',
    reader: 'https://kokunoyumeto.github.io/penn-state-stat-415-id/',
    edition: 'https://zenodo.org/records/22151570/files/00_00_stat415-pengantar-statistika-matematis-id.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22151570',
    repository: 'https://github.com/KokunoYumeto/penn-state-stat-415-id',
    release: 'https://github.com/KokunoYumeto/penn-state-stat-415-id/releases/tag/v2026.08.29.c140-companion-c2',
    version: '2026.08.29.c140-companion-c2',
    note: 'Rilis gabungan C2 memuat tulang punggung Penn State lengkap, donor Random lengkap, dan pendamping asli sampai C2 dalam 41 berkas. Pembaca utama berjumlah 219 halaman; kursus gabungan tetap diproduksi karena lapisan pendamping belum selesai.',
    supplements: [
      { id: 'random-mathematical-statistics-html', title: 'Komponen Random lengkap — HTML', resourceType: 'donor-reader', state: 'complete', url: 'https://kokunoyumeto.github.io/mathematical-statistics-id/' },
      { id: 'random-mathematical-statistics-pdf', title: 'Komponen Random lengkap — PDF', resourceType: 'donor-reader', state: 'complete', url: 'https://zenodo.org/records/22076539/files/00_statistika-matematis-id-reader-2026.08.24.29.pdf?download=1' },
      { id: 'random-mathematical-statistics-doi', title: 'Komponen Random lengkap — DOI', resourceType: 'donor-archive', state: 'complete', url: 'https://doi.org/10.5281/zenodo.22076539' },
    ],
    progress: {
      unitLabel: 'dokumen Penn State STAT 415',
      totalUnits: 14,
      translationBearingUnits: 14,
      integrationReadyUnits: 14,
      canonicalUnits: 14,
      publicUnits: 14,
      publicPages: 219,
      publicBoundary: 'tulang punggung lengkap; pendamping asli sampai C2',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  D10: publication({
    state: 'production',
    edition: 'https://zenodo.org/records/22161046/files/00_READ_FIRST_FONDASI_TEORI_UKURAN_V1_DAN_V2_HINGGA_BAB_26.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22161046',
    repository: 'https://github.com/KokunoYumeto/fremlin-measure-theory-id',
    version: '0.19.0-v2-through-ch26',
    note: 'Edisi publik mencapai 444 dari 672 halaman sumber melalui Bab 26 lengkap dalam pembaca reflow 477 halaman. Kandidat Bab 27 mencapai 509 halaman sumber dan telah melewati pembangunan serta QA visual, tetapi masih menunggu keputusan penerimaan pemilik dan belum menjadi edisi publik.',
    progress: {
      unitLabel: 'halaman sumber',
      totalUnits: 672,
      translationBearingUnits: 509,
      integrationReadyUnits: 509,
      canonicalUnits: 444,
      publicUnits: 444,
      totalPages: 672,
      publicPages: 477,
      publicBoundary: '444/672 halaman sumber; Bab 26 lengkap',
      updatedAt: '2026-08-29T16:32:23+02:00',
    },
  }),
  D20: publication({
    learner: 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D20/',
  }),
  D30: publication({
    state: 'production',
    learner: 'https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/D30/',
    reader: 'https://kokunoyumeto.github.io/measure-theoretic-probability-stochastic-processes-id/',
    edition: 'https://zenodo.org/records/22148902/files/00_PROBABILITAS_TEORI_UKURAN_PROSES_STOKASTIK_ID_READER_CHECKPOINT_33.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22148902',
    repository: 'https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id',
    version: '2026.08.27-checkpoint.33',
    note: 'Checkpoint publik 33 memuat QuantEcon 8 dari 8 bab, 27 halaman Random terpilih, dua laboratorium, dua jembatan asli, enam rangkaian penguasaan, dan pembaca PDF 321 halaman. Kursus tetap diproduksi.',
    progress: {
      unitLabel: 'bab QuantEcon terpilih',
      totalUnits: 8,
      translationBearingUnits: 8,
      integrationReadyUnits: 8,
      canonicalUnits: 8,
      publicUnits: 8,
      publicPages: 321,
      publicBoundary: 'checkpoint 33; keseluruhan kursus masih diproduksi',
      updatedAt: '2026-08-28T00:00:00+02:00',
    },
  }),
  D50: publication({
    state: 'published',
    reader: null,
    edition: 'https://zenodo.org/records/22160677/files/geometri-diferensial-manifold-mulus-edisi-lengkap-id.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22160677',
    repository: 'https://github.com/KokunoYumeto/brenner-differentialgeometrie-id',
    release: 'https://github.com/KokunoYumeto/brenner-differentialgeometrie-id/releases/tag/v1.0.0',
    version: '2026.08.28-complete',
    note: 'Edisi lengkap 29 unit telah diterbitkan dan dipreservasi di GitHub serta Zenodo: 712 halaman, 576 latihan inti, 84 solusi sumber, dan 6.912 rekaman backend. Rekor lengkap 22160677 menggantikan checkpoint Unit 22 yang lebih lama.',
    progress: {
      unitLabel: 'unit kuliah dan lembar kerja',
      totalUnits: 29,
      translationBearingUnits: 29,
      integrationReadyUnits: 29,
      canonicalUnits: 29,
      publicUnits: 29,
      publicPages: 712,
      publicBoundary: 'edisi lengkap di GitHub dan Zenodo',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  D60: publication({
    state: 'production',
    reader: 'https://kokunoyumeto.github.io/algebraic-topology-id/roberts-001-030-fomberg-001-007-ca01-hints-r01-r06-ca02-ca03-lab01-lab02-lab03/',
    edition: 'https://zenodo.org/records/22151513/files/00_TOPOLOGI_ALJABAR_ID_ROBERTS_001_030_FOMBERG_001_007_CA01_HINTS_R01_R06_CA02_CA03_LAB01_LAB02_LAB03_READER.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22151513',
    repository: 'https://github.com/KokunoYumeto/algebraic-topology-id',
    version: '0.31.5',
    note: 'Checkpoint publik v0.31.5 memuat Roberts 30/30, Fomberg §§1.1–1.13, penguasaan wajib 108/108, dan laboratorium komputasi 3/4. Laboratorium 4, penutupan metadata bukti, dan capstone masih diproduksi.',
    progress: {
      unitLabel: 'laboratorium komputasi',
      totalUnits: 4,
      translationBearingUnits: 3,
      integrationReadyUnits: 3,
      canonicalUnits: 3,
      publicUnits: 3,
      publicPages: 545,
      publicBoundary: 'Roberts 30/30; laboratorium 3/4',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  D70: publication({
    state: 'production',
    edition: 'https://zenodo.org/records/22151447/files/00-metode-aljabar-jilid-1-id-lengkap.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22151447',
    repository: 'https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id',
    version: '1.0.0',
    note: 'Komponen Wen-Wei Li Jilid I telah selesai dan diterbitkan sebagai pembaca 521 halaman. Pembaca Duncan 114 halaman, CRing terpilih 74 halaman, serta rute dan penguasaan asli 7 halaman sudah dibangun secara lokal tetapi belum diterima dan dipreservasi publik; mata kuliah gabungan tetap diproduksi.',
    progress: {
      unitLabel: 'jilid utama Wen-Wei Li',
      totalUnits: 1,
      translationBearingUnits: 1,
      integrationReadyUnits: 1,
      canonicalUnits: 1,
      publicUnits: 1,
      publicPages: 521,
      publicBoundary: 'Jilid I lengkap; kursus gabungan belum lengkap',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
  D100: publication({
    state: 'production',
    reader: 'https://kokunoyumeto.github.io/algebraic-geometry-bridge-id/',
    edition: 'https://zenodo.org/records/22150273/files/kurva-aljabar-id-unit-30.pdf?download=1',
    zenodo: 'https://doi.org/10.5281/zenodo.22150273',
    repository: 'https://github.com/KokunoYumeto/algebraic-geometry-bridge-id',
    version: 'unit-30',
    note: 'Jilid klasik Kurva Aljabar telah selesai seluruh 30 unit dan diterbitkan sebagai pembaca 504 halaman. Jilid Bündel, Garben und Kohomologie memiliki Unit 1–3 lokal yang telah lolos QA dalam kandidat kumulatif 50 halaman, tetapi belum publik; Unit 4 baru memiliki otoritas sumber.',
    progress: {
      unitLabel: 'unit Kurva Aljabar',
      totalUnits: 30,
      translationBearingUnits: 30,
      integrationReadyUnits: 30,
      canonicalUnits: 30,
      publicUnits: 30,
      publicPages: 504,
      publicBoundary: 'Kurva Aljabar 30/30; kursus gabungan belum lengkap',
      updatedAt: '2026-08-29T00:00:00+02:00',
    },
  }),
});

export function materializeLiveCourses(authorityCourses, overlay = liveCoursePublications) {
  const authorityIds = new Set(authorityCourses.map(({ id }) => id));
  for (const id of Object.keys(overlay)) {
    if (!authorityIds.has(id)) throw new TypeError(`Unknown live-publication course ID: ${id}`);
  }

  return Object.freeze(authorityCourses.map((authorityCourse) => {
    const update = overlay[authorityCourse.id] ?? {};
    const replaceSupplements = hasOwn(update, 'supplements');
    const supplements = replaceSupplements
      ? (update.supplements ?? [])
      : [...(authorityCourse.supplements ?? []), ...(update.additionalSupplements ?? [])];
    const { additionalSupplements: _additionalSupplements, ...fields } = update;
    const merged = { ...authorityCourse, ...fields };
    if (replaceSupplements || hasOwn(authorityCourse, 'supplements') || supplements.length) {
      merged.supplements = Object.freeze(supplements.map((item) => Object.freeze({ ...item })));
    }
    return Object.freeze(merged);
  }));
}

export function deriveNextCourseIdsById(courses) {
  const next = Object.fromEntries(courses.map(({ id }) => [id, []]));
  for (const course of courses) {
    for (const prerequisite of course.prerequisites) {
      if (!next[prerequisite]) throw new TypeError(`${course.id}: unknown prerequisite ${prerequisite}`);
      next[prerequisite].push(course.id);
    }
  }
  return Object.freeze(Object.fromEntries(Object.entries(next).map(([id, ids]) => [id, Object.freeze(ids)])));
}
