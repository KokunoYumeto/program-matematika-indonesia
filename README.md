# Program Matematika Indonesia: peta belajar terbuka 40 mata kuliah matematika

Program terbuka berisi 40 mata kuliah matematika dalam Bahasa Indonesia, dari perbaikan fondasi sampai kesiapan
riset, dengan peta belajar yang menghubungkan prasyarat antar-mata kuliah. Setiap kartu mata kuliah menautkan buku
atau edisi terbuka yang dipakai, pembacanya dalam HTML atau PDF, dan situs penulis atau penerbit aslinya. Peta yang
sama tersedia dalam Bahasa Inggris.

[▶ Buka peta belajar Bahasa Indonesia](https://kokunoyumeto.github.io/program-matematika-indonesia/id/) ·
[Open the English learning map](https://kokunoyumeto.github.io/program-matematika-indonesia/en/) ·
[Situs program](https://kokunoyumeto.github.io/program-matematika-indonesia/)

## Cara program dibuat

Mata kuliah memakai buku teks terbuka dan edisi Bahasa Indonesianya, antara lain buku OpenStax, CLP (*Calculus*
dari UBC), buku Jiří Lebl, *Discrete Mathematics: An Open Introduction* dan *Mathematics in Lean*. Terjemahan Bahasa
Indonesia dikerjakan oleh AI; setiap edisi mencatat model, sumber dan kredit penulis aslinya. Koordinasi, rekayasa
backend dan penerbitan situs pusat ini dilakukan oleh **OpenAI Codex gpt-5.6-sol, Ultra**.

Peta terdiri atas empat tingkat: A (fondasi), B (dasar universitas), C (inti sarjana) dan D (fondasi pascasarjana
serta riset). Prasyarat dapat diikuti langsung antarkartu, dan mata kuliah dapat dicari dan disaring menurut
tingkat, bidang dan status. Kemajuan belajar dapat dicatat secara lokal di browser; data ini tidak dikirim ke server.

## Status

Pada 7 September 2026 ke-40 peran kurikulum mempunyai edisi publik lengkap. Peta Bahasa Inggris menautkan bahan
belajar berbahasa Inggris untuk 39 mata kuliah; beberapa mata kuliah (A00–A30, B10, B20, B30, D110) juga mempunyai
salinan buku asli berbahasa Inggris yang di-host program. Bahasa setiap bahan dinyatakan pada kartunya. Terjemahan AI
dapat memuat kesalahan; koreksi diterima melalui [isu GitHub](https://github.com/KokunoYumeto/program-matematika-indonesia/issues).

## Isi repositori

- [`docs/`](docs): situs publik (peta Bahasa Indonesia dan Inggris, pembaca, unduhan); situs dibangun langsung dari
  folder ini, tanpa akun, pelacak atau cookie. Data mata kuliah ada di [`docs/courses.js`](docs/courses.js).
- [`backend/`](backend): backend bersama untuk 40 peran dan 33 keluarga implementasi native;
  [metode dan temuan](MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md), [status backend v0.55](backend/GLOBAL_BACKEND_STATUS_V055.md),
  [metode navigasi pembaca universal](UNIVERSAL_READER_NAVIGATION.md).
- [`scripts/`](scripts): generator dan validator. Pemeriksaan situs: `node scripts/validate-static-site.mjs`.

| Keadaan pada 7 September 2026 | Hasil |
|---|---:|
| Peran kurikulum dengan korpus atau spesifikasi terpilih | 40/40 |
| Peran dengan edisi lengkap publik | 40/40 |
| Keluarga implementasi native yang dibandingkan | 33 |
| Adapter kapsul pertukaran bersama yang tervalidasi | 40/40 |
| Kontrak native utama | 15 × `2.3.1`; 19 × `course-learning-capability/1`; 4 × Lebl; 1 × topologi; 1 × geometri |
| Peran dengan paritas kapabilitas native lengkap menurut gerbang bukti saat ini | 12/40 |

B30 kini selesai sebagai edisi publik 1.243 halaman. D60 kini merupakan edisi komposit lengkap v0.31.7: pembaca HTML
tetap pintu belajar utama, PDF 564 halaman adalah unduhan edisi, dan ZIP sumber/backend hanya suplemen
reproduksibilitas sekunder.

## Sumber dan kredit

Kredit penulis, penerjemah manusia dan kontributor setiap korpus dipertahankan pada edisi dan metadata komponennya
masing-masing; setiap kartu mata kuliah menautkan situs penulis atau penerbit asli, misalnya
[CLP-1](https://personal.math.ubc.ca/~CLP/CLP1/) dan [CLP-2](https://personal.math.ubc.ca/~CLP/CLP2/).

## Lisensi

Kode situs tersedia berdasarkan [Lisensi MIT](LICENSE). Teks deskriptif dan metadata kurikulum asli pada situs ini
tersedia berdasarkan [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Buku dan edisi yang ditautkan tetap
menggunakan lisensi masing-masing.

---

## English

An open programme of 40 mathematics courses in Indonesian, from foundation repair to research readiness, with a
learning map that links the prerequisites between courses. Each course card links the open textbook or edition used,
its HTML or PDF reader, and the original author's or publisher's site. The same map is available in English.

The courses use open textbooks and their Indonesian editions, among them the OpenStax books, CLP (*Calculus* from
UBC), Jiří Lebl's books, *Discrete Mathematics: An Open Introduction* and *Mathematics in Lean*. The Indonesian
translations are AI-translated; each edition records its models, sources and the credits of its original authors.
Coordination, backend engineering and the publication of this central site were done by OpenAI Codex gpt-5.6-sol,
Ultra.

On 7 September 2026 all 40 curriculum roles had complete public editions. The English map links English learning
material for 39 courses; several courses (A00–A30, B10, B20, B30, D110) also have programme-hosted copies of the
original English books. Each card states the language of each resource. AI translations may contain errors;
corrections are welcome through [GitHub issues](https://github.com/KokunoYumeto/program-matematika-indonesia/issues).

The site code is under the [MIT License](LICENSE); the descriptive text and original curriculum metadata are under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); the linked books and editions keep their own licences.
