# Program Matematika Indonesia v0.43.0

Snapshot pusat ini tetap merupakan pekerjaan berjalan. Empat puluh dari empat
puluh peran kurikulum memiliki korpus terpilih atau spesifikasi asli yang
dibekukan, tetapi sebagian besar terjemahan dan edisi akhir masih diproduksi.

## Perubahan utama

- Menambahkan bukti migrasi backend-v1 lengkap untuk edisi Judson aljabar
  abstrak Bahasa Indonesia: 24.733 rekaman native menghasilkan 36.978 rekaman
  bersama, dengan 24.483 ID native dipertahankan dan dua replay identik.
- Menambahkan bukti migrasi backend-v1 lengkap untuk *Yet Another Introductory
  Number Theory Textbook* Bahasa Indonesia: 5.272 rekaman native berbalik tepat
  dari 6.967 rekaman bersama dan seluruh proyeksi, aset, artefak, pembaca, QA,
  dan snapshot publik tetap terikat.
- Memvalidasi ulang bukti DMOI4 (163.583 rekaman) dan Open Logic OLP-0722
  (6.522 rekaman) dengan receipt yang disanitasi dan bebas jalur privat.
- Membuat penemuan receipt dan skrip adapter pada pembangun/validator rilis
  bersifat dinamis, sehingga migrasi baru tidak perlu ditambahkan secara manual
  ke dua daftar terpisah.
- Menambahkan metadata kartu sosial untuk build Sites dan menghapus identitas
  pribadi pengguna dari semua permukaan sumber yang masuk ke rilis baru.

Adapter Tea Time sudah diimplementasikan tetapi sengaja tidak diakui pada
snapshot ini: byte pembaca setelah QA terminologi belum memiliki receipt
publikasi dan readback publik yang cocok. Edisi Mathematics in Lean yang
dikoreksi juga tetap di luar snapshot sampai pemilik korpus membekukan dan
menerbitkan backend baru. Keduanya akan masuk hanya setelah batas publik yang
bersih terbukti.

## Provenance

Koordinasi, rekayasa backend, validasi, dan penerbitan snapshot pusat dilakukan
oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna. Kredit penulis,
penerjemah manusia, dan kontributor tetap dipertahankan pada setiap komponen.

## Preservasi

- DOI versi: `10.5281/zenodo.22062318`
- DOI konsep: `10.5281/zenodo.22059707`
- Repositori: <https://github.com/KokunoYumeto/program-matematika-indonesia>

Rilis dianggap selesai hanya setelah seluruh berkas dipublikasikan dan dibaca
kembali secara anonim dengan kecocokan nama, ukuran, dan SHA-256.
