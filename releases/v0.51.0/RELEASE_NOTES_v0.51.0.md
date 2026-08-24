# Program Matematika Indonesia v0.51.0

v0.51.0 menutup audit pemilihan sumber O001–O018 dan memperbarui hub dengan
batas produksi yang sudah diverifikasi setelah v0.50.0. Rilis ini tidak menambah
klaim mata kuliah selesai: peta tetap memuat 40 dari 40 peran dengan sumber atau
spesifikasi asli yang dibekukan, 15 peran dengan edisi lengkap pada 14 rekaman
publik, dan nol peran sumber yang belum dipilih.

## Penutupan audit sumber

- **C100 — Geometri.** Petrunin dibekukan sebagai donor utama yang sah untuk
  buku kursus asli CC BY-SA. Clemens/Snapp dipertahankan sebagai pendamping
  terpisah berlisensi CC BY-NC-SA/GPL; sintesis, perbaikan rigor, aset, solusi,
  dan asesmen asli masih diproduksi.
- **D70 — Aljabar Pascasarjana.** Spine kini mengikat Wen-Wei Li Jilid 1,
  sumber TeX teori representasi Alexander Duncan berlisensi CC BY 4.0, enam
  rentang CRing/GFDL yang berbatas, serta lapisan penghubung dan solusi asli.
  Etingof/MIT tetap referensi saja dan lembar tugas eksternal tidak diterima
  sebagai bagian korpus.
- **D90 — Optimisasi Lanjut.** Spine editabel kanonik kini memakai Habring
  arXiv 2607.11664v1 (CC BY 4.0), modul TeX Becker berlisensi MIT, dan
  penutupan KKT, stokastik, variasional, serta solusi asli. MIT 6.253 dan Royer
  dipertahankan sebagai materi pendamping dengan lisensi terpisah.

## Batas publik dan produksi terbaru

- **B30 — Kalkulus Integral.** CLP-2 WIP.9/CP0047-R1 pada DOI
  `10.5281/zenodo.22077325` memuat pembaca 674 halaman, SHA-256
  `863e9c5709ff961b3ba09f93da973a8188849d81a4e9680900e1d66a58232bd6`.
  Backend 105.047 rekaman dapat direproduksi persis. Paket HP-CLP2-001 dan
  HP-CLP2-002 diterima oleh pemilik; R003 tetap belum lengkap.
- **B70/C10/C20/C50 — Keluarga Lebl.** Rilis U336 pada DOI
  `10.5281/zenodo.22082567` memuat 336 unit: R006 271, R007 15, dan R008 50.
  Jilid I tetap lengkap pada 334 halaman. Pembaca Jilid II mencapai 198 halaman
  sampai akhir Bagian 11.4 beserta semua 11 latihan, SHA-256
  `78543d4e8087e68589e8f15d0a3a969b3282247c7c9c2cdcb6f658dfa4b68e4f`.
  B70, C20, dan C50 tetap dalam produksi.
- **A30 — Prakalkulus.** HP-A30-001 berstatus manager-clean untuk unit
  `m49369`, `m49371`, `m49372`, `m49374`, dan `m49384`. Paket masih menunggu
  QA pemilik kanonik dan integrasi tiga-arah; paket belum terintegrasi atau
  diterbitkan dan tidak dihitung sebagai penyelesaian baru.
- **D40 — Persamaan Diferensial Parsial.** Unit 09 pada DOI
  `10.5281/zenodo.22086227` memuat pembaca 77 halaman, 4.414.297 byte,
  SHA-256 `f2869bc0c38153d2223a03e8dccc85c306cefdc4eea15f9fe6a560a6d1f7ce91`.
  Bab klasifikasi selesai pada batas publik ini; komposit lengkap masih
  diproduksi.
- **D50 — Lipatan Mulus dan Geometri Diferensial.** Batas publik tetap Unit 10,
  165 halaman, pada DOI `10.5281/zenodo.22073928`. Unit 11–13 sudah lolos QA
  berbatas secara lokal, tetapi belum diterbitkan.
- **D60 — Topologi Aljabar.** DOI `10.5281/zenodo.22084021` memuat Roberts
  Kuliah 1–30 lengkap dan jembatan Fomberg §§1.1–1.2 dalam pembaca 362 halaman,
  2.322.978 byte, SHA-256
  `fb81f2b2c0f73c17c4e3be4eaae164eaeaeb0c4ff0661580acfc7aa9b6d5f749`.
  Sisa jembatan dan penutupan asli masih diproduksi.
- **D90 — Optimisasi Lanjut.** Checkpoint pendamping publik terbaru adalah MIT
  L10 pada DOI `10.5281/zenodo.22077419`: 10 halaman, SHA-256
  `3b01d57e8e8a7d7887f36cfdc205d1b68d1d007a152bd8e0cd75479628e1abc0`.
  L11 masih lokal dan checkpoint pendamping ini bukan spine kanonik.
- **D100 — Jembatan Geometri Aljabar.** DOI `10.5281/zenodo.22077441` memuat
  Unit 1–15 dalam pembaca 267 halaman, 6.502.255 byte, SHA-256
  `e56aae414a9d7e252485d06e7da790fae9bf972514c8fe47fc31d26eddd3699c`.
  Unit 16–18 hanya lokal; Unit 19 dibekukan tetapi belum didispatch.

## Backend dan provenance

Backend pusat tetap memakai schema bersama v1: 38 tabel, 2.122 rekaman, replay
deterministik, dan sepuluh bukti migrasi korpus lengkap dengan 809.296 rekaman
target. Perubahan v0.51.0 memperbarui katalog, hak dan arsitektur sumber, serta
batas publik; ia tidak mengubah backend native milik setiap korpus.

Koordinasi, validasi, dan penerbitan snapshot pusat dilakukan oleh OpenAI Codex
gpt-5.6-sol, Ultra atas instruksi pengguna. Kredit sumber dan kontributor tetap
melekat pada setiap komponen.
