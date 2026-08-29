# Program Matematika Indonesia v0.42.0

DOI versi: [10.5281/zenodo.22061915](https://doi.org/10.5281/zenodo.22061915)  
DOI konsep: [10.5281/zenodo.22059707](https://doi.org/10.5281/zenodo.22059707)  
Commit sumber: `12551fad03b13de1bc5f9e7f96f4a263f48a0cc3`  
Tanggal snapshot: 2026-08-22  
Status program: **pekerjaan berjalan**

## Perubahan material sejak v0.41.0

- Menambahkan bukti migrasi backend bersama v1 untuk seluruh edisi Bahasa
  Indonesia Open Logic Project OLP-0722: 722 berkas sumber, 722 berkas target,
  dan 6.522 rekaman ketat yang direkonstruksi dua kali secara byte-identik.
- Mempertahankan setiap byte sumber dan terjemahan Open Logic. Rekonstruksi
  menangani secara eksplisit materialisasi checkout CRLF yang dibuktikan oleh
  manifes penutupan, tanpa menulis ulang korpus publik.
- Menambahkan satu skema dan validator bukti migrasi yang sama untuk bukti
  DMOI 163.583 rekaman dan bukti Open Logic 6.522 rekaman.
- Menambahkan handoff migrasi aditif yang melarang restart terjemahan,
  perubahan arsitektur korpus, penggantian backend asli, atau penundaan unit
  dan transaksi penerbitan yang sedang berjalan.
- Menambahkan gerbang QA terminologi lapangan Bahasa Indonesia pada batas aman:
  sumber TeX arXiv representatif bila tersedia, atau fallback DOCX/PDF yang
  dicatat jujur; koreksi hanya setelah pertimbangan makna matematis,
  konsistensi, dan konvensi lapangan.
- Menambahkan provenance model eksplisit sambil mempertahankan seluruh kredit
  penulis, sumber, dan kontributor manusia.

## Keadaan yang tidak berubah

- Empat puluh dari empat puluh peran kurikulum memiliki arsitektur sumber yang
  dipilih atau spesifikasi asli yang dibekukan.
- Paket backend pusat tetap 2.122 rekaman pada 38 tabel; ekspor JSONL/CSV tetap
  lossless dan deterministik.
- Pemilihan sumber dan dua bukti migrasi lengkap **bukan** klaim bahwa seluruh
  terjemahan, solusi, laboratorium, atau edisi program telah selesai.
- Setiap edisi korpus mempertahankan lisensi komponen, sumber, dan identitas
  penerbitannya sendiri.

## Provenance

Koordinasi, rekayasa backend, validasi, dan penerbitan snapshot pusat ini
dilakukan oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna.
Kredit penulis, penerjemah manusia, dan kontributor setiap korpus tidak
digantikan oleh pernyataan ini.
