# D50 — pemilih bacaan, latihan, dan rencana pengajaran

Alat ini menghubungkan identitas backend Geometri Diferensial dengan bacaan
Bahasa Indonesia yang sudah diterbitkan. Ini bukan terjemahan baru atau bukti
bahwa seluruh backend program telah selesai.

## Cakupan yang diperiksa

- 1.206 rekaman unit dan 160 bagian sumber dipertahankan dan diperhitungkan.
- 1.223 unit/bagian dapat dipilih: 1.202 tujuan tepat dan 21 tautan ke bagian
  induk yang secara terbuka diberi keterangan.
- 576 latihan lembar kerja memiliki 84 solusi sumber tercatat. Sebanyak 492
  latihan tidak memiliki solusi sumber tercatat; alat ini tidak membuat jawaban.
- 123 kemunculan soal ujian mewakili 119 identitas soal. Sebanyak 24 tempat
  kosong bukan soal. Solusi ujian terdiri dari 117 solusi sumber dan enam
  solusi tambahan asli yang tidak dinisbahkan kepada sumber.
- 32 soal jembatan memiliki petunjuk dan solusi asli dalam bacaan yang sama.
- 39 kaitan konsep dan sembilan prasyarat jembatan disalin dari metadata asli;
  ini bukan pernyataan bahwa semua konsep pada seluruh kursus telah dipetakan.

Antarmuka tersedia dalam Bahasa Indonesia dan English. Bahasa bacaan tetap
Indonesia. English bukan edisi baru dari buku atau penulisan ulang dengan
ragam sehari-hari. Semua pemilihan dilakukan di peramban tanpa pelacakan,
penyimpanan kemajuan, atau pengiriman data ke server.

## Menggunakan alat secara lokal

1. Bangun alat dari akar repositori dengan
   `node scripts/build-d50-surface-v1.mjs`.
2. Unduh arsip HTML asli melalui URL yang dibekukan dalam
   `input/reader-witness.json`. SHA-256 arsip:
   `65ce76d031baea3e049df09218963c187615f25e324bcfd48216afd5fd8cb5e5`.
3. Ekstrak isi arsip ke `portable/reader/`. Berkas masukannya harus berada di
   `portable/reader/index.html`, bukan satu tingkat folder tambahan.
4. Buka `portable/index.html`, atau `portable/teacher.html` untuk pengajar.
   Pilih unit dan unduh rencana JSON. Rencana menyimpan identitas, kaitan solusi,
   lisensi komponen, bukti hash, dan batas cakupan; rencana bukan buku lengkap.

Paket sumber alat berisi masukan metadata yang dibekukan dan semua skrip untuk
membangun ulang alat ini. Buku tidak disalin atau diubah. Kode sumber dan
bahan buku tetap berada pada
[rilis sumber D50](https://github.com/KokunoYumeto/brenner-differentialgeometrie-id/releases/tag/v1.0.1).
Pada pemeriksaan 22 September 2026, repositori sumber belum memiliki situs
GitHub Pages. Karena itu, alat ini **belum** dinyatakan terhubung sebagai alat
pelajar daring baru dalam indeks pusat.

## Pemeriksaan dan reproduksi

`node scripts/test-d50-surface-v1.mjs` memeriksa semua rekaman yang diproyeksikan,
kaitan solusi, nomor slot ujian, hak komponen, 17 masukan rusak, ekspor seluruh
731 soal latihan, serta dua pembangunan dengan byte identik.
`tests.json` dan `browser-qa.json` memisahkan pemeriksaan otomatis dari
pemeriksaan antarmuka. `input/reader-witness.json` mencatat pemeriksaan unduhan
anonim atas 44 berkas arsip, CRC, 1.766 jangkar unik, dan kesamaan byte dengan
bacaan asli. Skrip intake adalah operasi jaringan terpisah; pembangunan biasa
menggunakan metadata lokal yang sudah dibekukan.

Integrasi, pemetaan metadata, kode alat, dan penyuntingan penjelasan ini dibuat
oleh **OpenAI Codex — GPT-6 Astra, Ultra effort**. Metadata penerbit sumber
menyebut **OpenAI Codex gpt-5.6-sol, Ultra** untuk terjemahan dan bahan aslinya.
Ini bukan klaim peninjauan manusia atau audit matematis baru atas seluruh buku.

## English

This is a reproducible Indonesian-reader selector with Indonesian and English
interfaces. It preserves native unit identities, exam occurrences, component
rights, and the distinction between source solutions and original additions.
It is not an Everyday-English rewrite or a completed forty-course backend.

Build with `node scripts/build-d50-surface-v1.mjs`; run the independent checks
with `node scripts/test-d50-surface-v1.mjs`. Extract the original hash-verified
HTML archive into `portable/reader/`, then open `portable/index.en.html` or
`portable/teacher.en.html`. The exact archive URL and hashes are in the reader
witness. The source package reproduces the tool; it does not silently include
or replace the textbook. Central hosted delivery remains unfinished.

Metadata integration, tool code and this explanation: **OpenAI Codex — GPT-6
Astra, Ultra effort**. Source-edition attribution: **OpenAI Codex gpt-5.6-sol,
Ultra**. No human review or new whole-book mathematical review is claimed.
