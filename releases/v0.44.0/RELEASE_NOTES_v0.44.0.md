# Program Matematika Indonesia v0.44.0

Snapshot pusat ini tetap merupakan pekerjaan berjalan. Empat puluh dari empat
puluh peran kurikulum memiliki korpus terpilih atau spesifikasi asli yang
dibekukan, tetapi sebagian besar terjemahan dan edisi akhir masih diproduksi.

## Koreksi registri semantik

Snapshot sebelumnya memiliki 40 referensi peran yang unik, tetapi sembilan
pemilik korpus terikat ke peran yang salah dalam satu permutasi tertutup.
v0.44.0 memperbaiki ikatan berikut tanpa mengubah korpus atau pekerjaan milik
lane mana pun:

- keluarga Lebl: C10, C20, B70, **C50**;
- Applied Combinatorics: **C70**;
- Poritz/YAIN: **C60**;
- Mathematics in Lean: **D110**;
- GVSU topology: **C90**;
- Petrunin geometry: **C100**;
- Lega modeling/nonlinear dynamics: **C120**;
- reader praktik riset/reprodusibilitas: **D120**;
- Open Optimization: **C130**.

Setiap entri mata kuliah kini memuat `ownerLane`. Validator membandingkan
seluruh peta semantik 40/40 secara eksplisit; jumlah dan keunikan ID saja tidak
lagi cukup untuk meluluskan rilis. Metadata edisi selesai juga dikoreksi:
C60/Poritz-YAIN dan D110/Mathematics in Lean masuk pada peran yang tepat,
sedangkan D120 tetap berstatus produksi.

## Mathematics in Lean dan backend bersama

- Menambahkan bukti migrasi backend-v1 lengkap untuk *Mathematics in Lean*
  v4.30.0-id.3: 10.978 rekaman native dipetakan satu-ke-satu ke 10.978 rekaman
  bersama, 38/38 tabel hadir, 14 tabel berisi data, dan pembalikan menghasilkan
  tepat 10.978 rekaman asli.
- Dua eksekusi lengkap menghasilkan receipt byte-identik dengan SHA-256
  `f09e6fd1a8d08da1b03ed26aadad6fbf46ef26a1bdae200a4001ed5117cbd9f2`.
- Arsip backend publik GitHub, Zenodo, dan Figshare terikat pada 7.101.665 byte
  dan SHA-256
  `522abc439742b99a623f083bfbcb29bc0eab45de7622bfe2c1b227a6c868c5d0`.
- Satu field receipt GitHub menulis 10.876, sedangkan teks receipt, handoff,
  ekspor lokal, validator, dan `records.jsonl` publik semuanya membuktikan
  10.978. Koreksi ini dicatat sebagai salah ketik scalar; receipt dan lane
  pemilik tidak ditulis ulang.
- QA terminologi edisi Lean tetap terikat ke sumber Indonesia arXiv
  `2001.05854v1`; perubahan yang telah dipropagasikan adalah *ruang topologi*
  dan *prapeta*.

Lima receipt migrasi korpus lengkap kini mengikuti satu kontrak: DMOI, Open
Logic, Judson, Poritz/YAIN, dan Mathematics in Lean. Paket backend pusat tetap
memuat 2.122 rekaman kurikulum; migrasi korpus adalah bukti terpisah yang
direproduksi dari backend pemilik dan tidak menyalin seluruh korpus ke paket
pusat.

## Pengerasan rilis

- Katalog, manifest sumber, dan validasi lokal wajib menunjuk commit sumber
  penuh yang sama; validasi ditolak bila commit itu bukan `HEAD` yang sedang
  diuji.
- URI `$schema` katalog dan `$id` salinan skema sekarang menunjuk byte skema
  v1 yang sama pada rekaman v0.44.0.
- Klaim lima migrasi dalam katalog dicocokkan dengan identitas dan jumlah
  rekaman pada receipt masing-masing.
- Inventaris prapublikasi harus tepat, gambar kartu sosial harus byte-identik
  dengan aset situs, dan setiap berkas serta entri ZIP melewati pemindaian
  privasi sebelum dapat dinyatakan lulus.

## Provenance

Koordinasi, rekayasa backend, validasi, dan penerbitan snapshot pusat dilakukan
oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna. Kredit penulis,
penerjemah manusia, dan kontributor tetap dipertahankan pada setiap komponen.

## Preservasi

- DOI versi: `10.5281/zenodo.22062832`
- DOI konsep: `10.5281/zenodo.22059707`
- Repositori: <https://github.com/KokunoYumeto/program-matematika-indonesia>

Rilis dianggap selesai hanya setelah seluruh berkas dipublikasikan dan dibaca
kembali secara anonim dengan kecocokan nama, ukuran, dan SHA-256.
