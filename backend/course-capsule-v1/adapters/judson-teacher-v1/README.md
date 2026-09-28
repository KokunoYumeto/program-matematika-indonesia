# Perencana tugas aljabar abstrak — C30 dan C40

Perencana ini memakai 913 identitas soal dari backend buku *Aljabar Abstrak:
Teori dan Penerapan* karya Thomas W. Judson: 610 untuk C30 dan 303 untuk C40.
Ini bukan terjemahan baru atau salinan isi buku. Pilih soal menurut bab, jenis
bantuan atau edisi; ekspor/impor daftar tugas dengan identitas sumber tetap;
dan cetak daftar rujukan untuk pelajar.

## Batas yang penting

- 213 petunjuk memiliki isi. Seluruh 116 elemen respons kosong: tempat pelajar
  menulis jawaban, **bukan** 116 jawaban atau penyelesaian yang disediakan.
- 814 soal ada dalam pembaca WEB; 99 soal lainnya hanya ada dalam edisi Sage.
  Identitas dan jalur kedua edisi tetap dipertahankan.
- Nomor lokal mengikuti kelompok dalam XML sumber, bukan halaman PDF.
- Antarmuka Inggris memakai kumpulan soal yang sama dan menunjuk pada pembaca
  Bahasa Indonesia versi 2026.08.22.2. Jangan menyebutnya pembaca Inggris.
- Pemetaan dibuktikan terhadap arsip beku. Tidak ada klaim bahwa pembaca daring
  terkini identik dengan versi tersebut, atau bahwa kualitas bahasa seluruh
  buku telah ditinjau ulang oleh integrator.
- Tautan langsung pembaca daring telah diperiksa pada 79 halaman untuk semua
  913 identitas soal; bukti waktu, hash halaman dan jangkar ada pada
  `input/reader-access.json`. Ini membuktikan akses ke soal, bukan bahwa semua
  perubahan edisi daring telah dibandingkan dengan arsip beku.
- JavaScript perencana tidak mengirim permintaan jaringan, tidak menyimpan
  data secara persisten dan tidak menjalankan Sage. Tautan unduhan dibuka hanya
  ketika pembaca memilihnya. Menjalankan perhitungan Sage merupakan hal terpisah.

## Memakai buku secara luring

Unduh arsip WEB dan SAGE dari tautan yang tersedia pada halaman perencana.
Ekstrak isinya masing-masing ke direktori `book-web/` dan `book-sage/` di samping
halaman HTML perencana. Setelah itu aktifkan **Aktifkan tautan buku lokal**.
Identitas arsip dan SHA-256 setiap halaman buku yang dirujuk ada dalam data soal.
Arsip buku tidak disalin ke paket perencana ini.

## Sumber dan pengujian

Paket sumber mempertahankan struktur direktori proyek. Python 3.11+ pustaka
standar cukup untuk membuat kembali halaman; Node.js dipakai untuk pengujian
pilihan/impor. Dari akar paket:

```text
python scripts/build-judson-teacher-v1.py
python scripts/test-judson-teacher-v1.py
node scripts/test-judson-teacher-ui-v1.mjs
python scripts/package-judson-teacher-v1.py
```

Keluaran terdapat dalam `backend/course-capsule-v1/adapters/judson-teacher-v1/site/`.
Pengujian tanpa `--source-archive` membuktikan proyeksi dan reproduksi perencana,
bukan mengulangi audit arsip buku. Audit masukan asli dapat diulang dengan
`scripts/intake-judson-teacher-v1.py`: berikan `--source-archive`, `--sage-archive`
dan `--cache`. Ia juga memerlukan adapter Judson v2.3.1 asli dan manifest rilis
yang berada di samping arsip sumber. `--cache` menyimpan arsip WEB beku; berkas
yang sudah cocok dipakai ulang. Jangan mengganti arsip dengan edisi berbeda.

Hak buku: sumber asli GFDL-1.2-or-later; edisi Bahasa Indonesia
GFDL-1.3-or-later. Tidak ada bagian invarian atau teks sampul. `COPYING` dan
`gfdl.xml` mempertahankan teks hukum asli. Perubahan integrasi ini menambahkan
pemilihan/rujukan soal tanpa mengubah buku atau menambahkan jawaban.

Integrasi perencana, kode, dan dokumentasi dibuat oleh OpenAI Codex —
gpt-6-astra, tingkat upaya Ultra. Ini bukan klaim peninjauan manusia dan bukan
atribusi model untuk terjemahan buku sumber.

---

## English

This reference planner preserves 913 exercise identities across C30 (610) and
C40 (303). It supports chapter/support filtering, assignment export/import and
printing reference lists. The 213 hints contain material; all 116 response
elements are empty answer slots, not supplied solutions. 99 exercises require
the separate Sage reader. The English interface still opens Indonesian books.

To read offline, extract the frozen WEB and SAGE archives into `book-web/` and
`book-sage/` beside the planner HTML, then enable local book links. The planner
does not bundle book bodies or execute Sage. Build/test commands and output
paths appear above. A metadata-only replay does not repeat whole-book source
verification. The original and modified-edition licences are retained verbatim.

Planner integration produced by OpenAI Codex — gpt-6-astra, Ultra effort.
No new book translation or human review is claimed.
