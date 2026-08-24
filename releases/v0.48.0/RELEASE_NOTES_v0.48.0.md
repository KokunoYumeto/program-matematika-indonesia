# Program Matematika Indonesia v0.48.0

Snapshot pusat ini tetap merupakan pekerjaan berjalan. Empat puluh dari empat
puluh peran kurikulum memiliki korpus terpilih atau spesifikasi asli yang
dibekukan, sementara produksi terjemahan dan penutupan sebagian besar korpus
tetap berlangsung.

## Tiga edisi lengkap baru

v0.48.0 mengakui tiga edisi yang telah dibaca kembali dari permukaan publik
dan yang backend pemiliknya telah melewati migrasi deterministik ke kontrak
bersama v1:

- **A00 — Praaljabar dan Fondasi Kuantitatif.** *OpenStax Prealgebra 2e*
  selesai pada 75/75 referensi sumber. Pembaca PDF v0.2.7 berisi 3.016 halaman;
  backend native berisi 519.678 rekaman. DOI versi:
  `10.5281/zenodo.22070683`; repositori:
  <https://github.com/KokunoYumeto/openstax-prealgebra-2e-id-ID>.
- **C120 — Pemodelan Matematis dan Dinamika Nonlinear.** Edisi Lega v1.01
  selesai pada 22 unit sumber plus empat jembatan, 4.105 segmen, 141 rekaman
  penguasaan, 26 notebook, 12 paket proyek, dan pembaca 355 halaman. DOI versi:
  `10.5281/zenodo.22070943`; repositori:
  <https://github.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id>.
- **C130 — Optimisasi Linear dan Integer / Riset Operasi.** *Open
  Optimization Book 1* plus laboratorium Pyomo/HiGHS yang diatribusikan
  terpisah selesai pada pembaca 666 halaman, 1.993 unit, 5.525 segmen, dan
  9.545 relasi. DOI versi: `10.5281/zenodo.22070653`; repositori:
  <https://github.com/KokunoYumeto/open-optimization-or-book-id>.

Program kini mencatat lima belas peran dengan edisi lengkap pada empat belas
rekaman publik berbeda karena C30 dan C40 berbagi satu edisi Judson. Tiga edisi
baru menambahkan 4.037 halaman pembaca yang terverifikasi.

## Landing page GitHub

Setiap kartu edisi lengkap kini menampilkan tiga tindakan berbeda bila
tersedia: membuka pembaca, membuka DOI preservasi, dan membuka repositori
GitHub korpus. Halaman utama dan footer juga menautkan repositori pusat secara
langsung. Dengan demikian landing page bukan hanya katalog DOI, tetapi pintu
masuk manusia yang dapat menelusuri edisi, arsip, dan sumber/mirror.

## Backend dan peta peran

Peta `ownerLane` tetap tepat: 40 peran unik, nol salah ikat, dan nol peran
terpilih tanpa pemilik. C80 menunjuk edisi Open Logic yang telah lengkap dan
diterbitkan, sehingga tidak memerlukan produksi ulang.

Sepuluh bukti migrasi korpus lengkap kini memvalidasi 809.296 rekaman target
virtual. Tiga bukti baru bersifat streaming/replayable dan zero-copy:

- A00: 519.678 rekaman native + 3.368 rekaman turunan = 523.046;
- C120: 4.941 rekaman native, varian/alignment dan anchor = 16.029;
- C130: 17.987 rekaman native + 7.818 varian segmen = 25.805.

Backend besar pemilik tidak disalin ke repositori pusat. Receipt, adapter,
hash, rekonstruksi balik, schema ketat, dan dua assembly byte-identik cukup
untuk mematerialisasikan kembali setiap target. Paket katalog pusat tetap
2.122 rekaman karena ia menyimpan peta program, bukan salinan seluruh backend
korpus.

Koordinasi, rekayasa backend, validasi, dan penerbitan snapshot pusat dilakukan
oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna. Kredit penulis,
penerjemah manusia, dan kontributor tetap dipertahankan pada setiap komponen.

DOI pusat berada pada lineage konsep `10.5281/zenodo.22059707` melalui record
`10.5281/zenodo.22071700`; rilis dianggap selesai hanya setelah seluruh berkas
pusat dipublikasikan dan dibaca kembali secara anonim dengan kecocokan nama,
ukuran, dan SHA-256.
