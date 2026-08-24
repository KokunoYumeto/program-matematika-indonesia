# Program Matematika Indonesia v0.49.0

v0.49.0 adalah pembaruan ketepatan metadata dan tautan publik. Rilis ini tidak
menambah klaim mata kuliah selesai: peta tetap memuat 40 dari 40 peran dengan
sumber atau spesifikasi asli yang dibekukan, 15 peran dengan edisi lengkap pada
14 rekaman publik, 32 pemilik produksi, dan tidak ada peran terpilih yang tidak
memiliki pemilik.

## Kemajuan publik yang baru diikat

- Keluarga Lebl U319 diterbitkan pada DOI
  `10.5281/zenodo.22073827`. Delapan berkas publik berjumlah 11.092.047 byte dan
  telah dibaca kembali dengan SHA-256 yang tepat. Batasnya adalah 319 unit:
  R006 254 unit, R007 15 unit, dan R008 50 unit. Jilid I tetap lengkap pada 334
  halaman; pembaca Jilid II kini 180 halaman dan mencapai seluruh sepuluh
  latihan yang menutup Bagian 11.2. R007 mencapai rumus integral tentu untuk
  masalah nilai awal, sedangkan R008 mencapai akhir bagian bola Riemann.
  R007, R008, dan Jilid II tetap belum lengkap.
- D20/Analisis Fungsional kini menautkan checkpoint publik Erdman Bab 1–12 pada
  DOI `10.5281/zenodo.22072541`: pembaca 179 halaman, 2.001.449 byte, SHA-256
  `476b1f1fd6ca82deddeeb9edac1b07286567ede5663a6df32906a36dd3ea5ab6`.
  Produksi sesudah Bab 12 tidak dinyatakan publik atau selesai oleh hub ini.
- C140/Statistika Matematis kini menautkan checkpoint pendukung Random 16 dari
  29 pada DOI `10.5281/zenodo.22071140`. Pembaca publiknya 197 halaman dan
  85.357.801 byte, SHA-256
  `f1a886ff1285315478bb7e50a773e8a5d79b47e6170a86e82e7b98126f6f6160`.
  Checkpoint ini bukan penyelesaian C140: spine Penn State, edisi Random penuh,
  dan pendamping asli masih diproduksi.

## Peta peran dan backend

Audit independen tidak menemukan salah ikat korpus atau pemilik pada O004,
O006, atau O008. Peta semantik `ownerLane` tetap 40/40. Tidak ada tugas produksi
baru yang dibuat dan tidak ada korpus pemilik yang diubah oleh rilis pusat ini.

Backend pusat tetap memakai schema bersama v1: 38 tabel, 2.122 rekaman, replay
deterministik, dan sepuluh bukti migrasi korpus lengkap dengan total 809.296
rekaman target. Rilis ini hanya memperbarui katalog, situs, dan rujukan publik;
ia tidak mengubah payload backend pemilik.

Koordinasi, validasi, dan penerbitan snapshot pusat dilakukan oleh OpenAI Codex
gpt-5.6-sol, Ultra atas instruksi pengguna. Kredit sumber dan kontributor tetap
melekat pada setiap komponen.
