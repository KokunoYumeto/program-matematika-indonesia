# Program Matematika Indonesia v0.53.0

## Mulai belajar

**Situs untuk pelajar:**
<https://kokunoyumeto.github.io/program-matematika-indonesia/>

Pilih titik mulai, ikuti prasyarat dan petunjuk **Lanjut ke**, lalu buka
pembaca HTML atau PDF dari kartu mata kuliah. Zenodo menampilkan
`00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.53.0.pdf` sebagai lembar
mulai-belajar manusia. Salinan HTML mandiri adalah
`01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.53.0.html`.

## Perubahan

- Menambahkan edisi D20 *Analisis Fungsional* lengkap: 298 halaman, seluruh 17
  bab, 52 solusi latihan sumber, 10 solusi hasil kerja pembaca, 13 unit
  jembatan, PDF, dan pembaca HTML publik.
- Menambahkan navigasi kelanjutan langsung pada setiap kartu mata kuliah, yang
  diturunkan secara deterministik dari graf prasyarat 40-peran.
- Menambahkan bukti migrasi backend D20 yang lossless dan dapat diputar ulang:
  32.383 rekaman native dan 2.104 baris indeks diproyeksikan menjadi 41.689
  rekaman umum tanpa mengganti backend kanonik pemilik.
- Menaikkan federasi backend v2 menjadi v0.2.0: 2.430 rekaman menghubungkan 34
  dataset, 40 mata kuliah, 126 permukaan baca unik, 41 rute web, 16 kejadian
  QA, dan semua 2.122 identitas backend v1. Aksi `learn` dan `html` untuk URL
  yang sama kini menyatu pada satu permukaan, bukan dua rekaman semu.
- Membuat builder federasi mengikat katalog, paket pendahulu, kontrak, peta
  peran, migrasi, waktu rekam, dan tujuan publik sebagai input rilis eksplisit;
  perintah replay portabelnya direkam bersama paket.
- Mempertahankan situs belajar sebagai tujuan utama. PDF mulai-belajar dan HTML
  mandiri berada sebelum JSON, schema, CSV, dan ZIP pada inventaris rilis.

Koordinasi, rekayasa backend, validasi, dan penerbitan dilakukan oleh OpenAI
Codex gpt-5.6-sol, Ultra atas instruksi pengguna. Kredit sumber dan kontributor
tetap melekat pada setiap komponen.
