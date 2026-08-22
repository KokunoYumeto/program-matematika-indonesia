# Program Matematika Indonesia — snapshot v0.41.0

DOI versi: [10.5281/zenodo.22060393](https://doi.org/10.5281/zenodo.22060393)  
DOI konsep: [10.5281/zenodo.22059707](https://doi.org/10.5281/zenodo.22059707)  
Tanggal keadaan: 22 Agustus 2026  
Commit sumber lokal: `8d95e419456a36158127288640ff6981cb3d3641`

## Perubahan material

- Backend modular bersama v1 telah dipilih setelah audit lintas-korpus. Kernel struktural berasal dari backend DMOI yang sudah terbukti pada 163.583 rekaman; kontraknya diperluas menjadi 38 tabel ketat untuk rute, anggota rute, snapshot rilis, alignment, resep build, dan eksperimen.
- Paket pusat v1 menormalkan keempat puluh peran mata kuliah menjadi 2.122 rekaman: 40 kursus, 40 pernyataan sumber terpilih, 40 unit peran, 200 segmen netral, 200 varian `id-ID`, delapan konsep bidang, 442 relasi, satu rute program, dan hak komponen eksplisit.
- Paket pusat lolos Draft 2020-12, inventaris/hash, JSONL kanonik, rekonstruksi CSV lossless, keunikan ID global, penutupan foreign key, dan dua ekspor byte-identik.
- Seluruh backend DMOI sebanyak 163.583 rekaman lolos migrasi zero-copy yang reversibel: hanya nama/versi skema berubah, tanpa satu pun ID atau payload matematika berubah.
- Profil sumber ketat mempertahankan topologi CNXML, PreTeXt, LaTeX, LyX, MediaWiki, dan Pressbooks/HTML tanpa menjadikan proyeksi backend sebagai pengganti sumber yang dapat diedit.

## Keadaan kurikulum yang dipertahankan

- 40 peran mata kuliah dalam empat tingkat.
- 40 peran memiliki korpus terpilih atau spesifikasi asli yang dibekukan; tidak ada pemilihan sumber yang masih terbuka.
- Delapan peran memiliki edisi publik lengkap dalam tujuh rekaman edisi berbeda; C30 dan C40 memakai satu edisi Judson.
- Snapshot tetap berstatus pekerjaan berjalan. Backend bersama yang valid bukan klaim bahwa seluruh terjemahan, solusi, migrasi per-korpus, atau edisi final sudah selesai, dan bukan klaim akreditasi.

## Isi rilis

- pembaca katalog HTML mandiri, katalog JSON, dan skema katalog;
- sumber situs dan alat backend yang dapat direproduksi;
- skema backend v1 dan skema profil sumber;
- paket backend pusat lengkap dengan JSON, JSONL, CSV lossless, manifes, dan laporan validasi;
- keputusan konvergensi backend dan receipt migrasi penuh DMOI;
- kartu visual dan checksum SHA-256.

## Preservasi dan transport

Zenodo adalah jalur preservasi mandiri dalam concept DOI yang sama. Akses akun GitHub yang sempat ditangguhkan setelah penggunaan VPN telah dipulihkan; snapshot ini dipublikasikan ke lineage Zenodo yang sama dan mirror pusat didorong kembali ke repositori aslinya, tanpa membuat repositori pengganti.

Teks deskriptif dan metadata kurikulum asli berlisensi CC BY 4.0. Perangkat lunak dan skema hub berlisensi MIT. Korpus, edisi, aset, dan komponen tertaut mempertahankan hak, atribusi, dan identitasnya masing-masing; paket pusat tidak melisensikan ulang karya tersebut.
