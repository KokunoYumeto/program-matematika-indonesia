# Program Matematika Indonesia v0.45.0

Snapshot pusat ini tetap merupakan pekerjaan berjalan. Empat puluh dari empat
puluh peran kurikulum memiliki korpus terpilih atau spesifikasi asli yang
dibekukan, tetapi sebagian besar terjemahan dan edisi akhir masih diproduksi.

## Dua edisi lengkap yang baru diakui pusat

v0.45.0 mengakui dua penyelesaian yang telah diterbitkan dan dibaca kembali
secara publik:

- B80, *Komputasi Matematis dan Eksperimen yang Dapat Direproduksi*: rangka
  lengkap 14 unit, 75 latihan, 177 uji lulus, pembaca PDF 159 halaman, HTML,
  EPUB, sumber editabel, dan paket luring; DOI versi
  `10.5281/zenodo.22053905`.
- C70, Keller–Trotter *Applied Combinatorics*: pembaca lengkap 350 halaman,
  backend native 19.048 rekaman, HTML luring, sumber koresponding, serta mirror
  GitHub, Zenodo, dan Figshare; DOI versi `10.5281/zenodo.22062005`.

Program kini mencatat sepuluh peran dengan edisi lengkap pada sembilan rekaman
publik berbeda karena C30 dan C40 memakai satu edisi Judson yang sama. Status
ini tidak mengubah mata kuliah lain yang masih diproduksi menjadi selesai.

## Dua bukti migrasi backend tambahan

Backend native kedua edisi tetap menjadi otoritas. Paket pusat tidak menyalin
seluruh korpus; skrip deterministik dan receipt hash-bound membuktikan bagaimana
backend lengkap dapat diwujudkan pada kontrak bersama v1.

- B80: seluruh 326 entri katalog native dipertahankan satu-ke-satu beserta
  payload lengkapnya; pembalikan merekonstruksi tepat 110.511 byte katalog
  sumber. Delapan rekaman hak turunan dan lima jangkar referensi eksternal
  menghasilkan 339 rekaman bersama pada 38 tabel. Dua replay independen
  byte-identik. Receipt SHA-256:
  `ce01965df6e15bf15d38575491c11267a9cda31e2d46d58725a531eb747b4e02`.
- C70: seluruh 19.048 rekaman native dipetakan satu-ke-satu dan dibalik tanpa
  kehilangan. Satu jangkar prasyarat eksternal B10 yang eksplisit menghasilkan
  19.049 rekaman bersama dengan foreign-key closure lengkap. Dua replay
  independen byte-identik. Receipt SHA-256:
  `923781c83710d9f79759090cd97d8e751f17f5f47916f002f4885e3ffcde01cb`.

Tujuh bukti migrasi korpus lengkap kini berada di bawah satu kontrak: DMOI,
B80, Open Logic, Judson, Poritz/YAIN, Applied Combinatorics, dan Mathematics in
Lean. Paket kurikulum pusat tetap terpisah dengan 2.122 rekaman.

## Peta semantik dan validasi

Peta `ownerLane` yang dikoreksi pada v0.44.0 dipertahankan tepat: 40 peran,
40 ikatan semantik, nol ID hilang atau ekstra, dan nol salah ikat. Validator
v0.45.0 juga mengikat secara eksplisit sepuluh peran selesai, sembilan DOI versi
terkini, tujuh receipt migrasi, identitas skema katalog, commit sumber, inventaris
rilis, serta pemindaian privasi.

## Provenance

Koordinasi, rekayasa backend, validasi, dan penerbitan snapshot pusat dilakukan
oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna. Kredit penulis,
penerjemah manusia, dan kontributor tetap dipertahankan pada setiap komponen.

## Preservasi

- DOI versi: `10.5281/zenodo.22063205`
- DOI konsep: `10.5281/zenodo.22059707`
- Repositori: <https://github.com/KokunoYumeto/program-matematika-indonesia>

Rilis dianggap selesai hanya setelah seluruh berkas dipublikasikan dan dibaca
kembali secara anonim dengan kecocokan nama, ukuran, dan SHA-256.
