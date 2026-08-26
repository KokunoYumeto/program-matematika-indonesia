# Program Matematika Indonesia v0.58.0

Mulai belajar melalui situs HTML untuk pelajar:

<https://kokunoyumeto.github.io/program-matematika-indonesia/>

Situs itu adalah pintu utama: pilih titik mulai, ikuti prasyarat, lalu buka pembaca HTML atau PDF dari kartu mata kuliah. Arsip Zenodo menampilkan PDF dan HTML mulai-belajar terlebih dahulu. Katalog JSON, skema, dan paket backend disediakan setelahnya sebagai antarmuka mesin dan bukti reproduksibilitas—bukan sebagai halaman awal bagi pelajar.

## Perubahan utama

- Menambahkan B60, *Kalkulus Vektor*, sebagai edisi lengkap kedelapan belas: buku teks CLP4 316 halaman dan buku latihan lengkap 486 halaman. Buku latihan sekarang menjadi sumber tambahan terstruktur pada kartu pelajar, bukan tautan yang tersembunyi di metadata mesin.
- Mempertahankan C100, *Bidang Euklides dan Kerabatnya*, sebagai kursus utama lengkap yang bersih hak dengan pembaca HTML semantik sebagai jalur utama. Workbook Clemens/Snapp Unit 001–010 sepanjang 110 halaman ditampilkan sebagai sumber tambahan parsial pada lini CC BY-NC-SA 4.0 yang terpisah dari edisi utama CC BY-SA 4.0.
- Memperbarui checkpoint publik yang masih diproduksi tanpa menyebutnya selesai: A10 31/82 modul (984 halaman), A30 32/87 modul sampai `m49367` (947 halaman), D10 338/672 halaman, dan D40 sampai Unit 12 (154 halaman).
- Memperbarui keluarga Lebl ke U397: 397 unit (`R006=312`, `R007=35`, `R008=50`); C10 Jilid I tetap lengkap 334 halaman, C20 mencapai 226 halaman sampai §11.8.1, dan B70 memiliki pembaca bab sistem nonlinear lengkap 40 halaman sembari korpus PDB tetap diproduksi.
- Memperbarui backend federasi v2 menjadi 2.463 rekaman: 34 dataset, 40 mata kuliah, 144 permukaan baca unik, 43 rute publik, 63 peristiwa publikasi, 16 peristiwa QA, dan 2.122 identitas silang v1. Dua build terisolasi menghasilkan 20 berkas yang identik byte; 23 uji negatif dan deterministik lulus.
- Menambahkan `supplements[]` sebagai lapisan aditif pada katalog, rekaman kursus federasi, model baca pelajar, skema, dan renderer kartu. Backend native pemilik tetap kanonik; federasi hanya menghubungkan rute, komponen, hak, dan bukti publikasi.
- Melakukan pembacaan balik anonim baru terhadap delapan PDF pemilik yang baru diadopsi. Semua jumlah byte dan SHA-256 cocok dengan tanda terima pemilik.

Delapan belas peran mata kuliah selesai itu menggunakan tujuh belas rekaman edisi yang berbeda karena C30 dan C40 berbagi satu edisi Judson. Snapshot ini tidak menyatakan seluruh terjemahan selesai. Ia menerbitkan hasil yang telah melewati pemeriksaan deterministik dan mempertahankan status produksi secara eksplisit untuk pekerjaan yang masih berjalan.

Provenance engineering: OpenAI Codex gpt-5.6-sol, Ultra, atas instruksi pengguna; kredit penulis, sumber, lisensi, dan kontributor manusia tetap dipertahankan pada setiap komponen.
