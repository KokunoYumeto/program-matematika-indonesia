# Program Matematika Indonesia v0.50.0

v0.50.0 memperbarui peta publik dengan lima batas produksi yang sudah dapat
dibaca dan diverifikasi. Rilis ini tidak menambah klaim mata kuliah selesai:
peta tetap memuat 40 dari 40 peran dengan sumber atau spesifikasi asli yang
dibekukan, 15 peran dengan edisi lengkap pada 14 rekaman publik, 32 pemilik
produksi, dan tidak ada peran terpilih tanpa pemilik.

## Batas publik baru yang diikat

- **D30 — Probabilitas Teoretis-Ukuran dan Proses Stokastik.** Checkpoint 20
  pada DOI `10.5281/zenodo.22074332` memuat pembaca 223 halaman, 22.232.234
  byte, SHA-256
  `6697a3857e9284d5883dc613e23f2f855fb0e43d72e11db3fd9985f247f6ccf0`.
  Tiga dari delapan bab QuantEcon selesai; korpus tetap dalam produksi.
- **D40 — Persamaan Diferensial Parsial.** Unit 07 Dionne pada DOI
  `10.5281/zenodo.22074306` memuat 46 halaman, 2.986.749 byte, SHA-256
  `890663ab4e6ced2fe56ad1c3e1c3733dc1258a2ab7a1a60d8c98d715b5b48564`.
  Deskripsi korpus diperbaiki menjadi delapan simpul FEniCSx: tujuh wajib dan
  satu pengayaan. Kemajuan lokal setelah Unit 07 tidak dinyatakan publik.
- **D50 — Lipatan Mulus dan Geometri Diferensial.** Unit 10 pada DOI
  `10.5281/zenodo.22073928` memuat pembaca 165 halaman, 5.733.895 byte,
  SHA-256
  `4eaec807347feeab2b3334056d3109d5ce6e5eb30ed3649a507ae6124049856d`.
  Unit 11–12 sudah lolos QA berbatas secara lokal, tetapi belum diterbitkan.
- **D60 — Topologi Aljabar.** GitHub/Pages memuat Unit 1–25 dengan pembaca
  298 halaman, 1.972.209 byte, SHA-256
  `581d62162633a6624687517c5cf1595f5fc02a2701c2222b279711e0520b9a3f`.
  Zenodo tetap mempreservasi Unit 1–24 pada DOI
  `10.5281/zenodo.22074233`, pembaca 286 halaman, 1.907.368 byte, SHA-256
  `5189b04f2f28d7e8192c16e8ef070e23bbf98085d150d1f2124d15c071ccf9b8`.
  Kedua batas itu dinyatakan terpisah; Unit 26 belum diterbitkan.
- **D100 — Jembatan Geometri Aljabar.** Unit 08 pada DOI
  `10.5281/zenodo.22070936` memuat pembaca 161 halaman, 5.491.421 byte,
  SHA-256
  `94d279d5748761cc1648d728451a80562cffaffeac9005d93220e980556d72b6`.
  Unit 09 adalah checkpoint internal terverifikasi, bukan rilis publik.

## Peta peran dan backend

Pemeriksaan independen terbaru meluluskan 53 dari 53 cek: tepat 40 peran,
40 baris peta, 82 ujung dependensi yang sah, ikatan sumber timbal balik, nol
kesalahan semantik, 32 pemilik tugas unik, dan tiga grup pemilik bersama yang
tepat. C80 tetap satu-satunya peran tanpa tugas karena edisi Open Logic Project
Bahasa Indonesia sudah selesai sebelum pembagian tugas produksi ini.

Backend pusat tetap memakai schema bersama v1: 38 tabel, 2.122 rekaman, replay
deterministik, dan sepuluh bukti migrasi korpus lengkap dengan total 809.296
rekaman target. Rilis ini memperbarui katalog, situs, dan rujukan publik; ia
tidak mengubah backend native milik setiap korpus.

Koordinasi, validasi, dan penerbitan snapshot pusat dilakukan oleh OpenAI Codex
gpt-5.6-sol, Ultra atas instruksi pengguna. Kredit sumber dan kontributor tetap
melekat pada setiap komponen.
