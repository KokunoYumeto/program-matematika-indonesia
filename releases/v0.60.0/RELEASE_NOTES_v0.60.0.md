# Program Matematika Indonesia v0.60.0

Mulai belajar melalui situs HTML untuk pelajar:

<https://kokunoyumeto.github.io/program-matematika-indonesia/>

Situs itu adalah pintu utama: pilih titik mulai, ikuti prasyarat, lalu buka pembaca HTML atau PDF dari kartu mata kuliah. Arsip Zenodo menampilkan PDF dan HTML mulai-belajar terlebih dahulu. Katalog JSON, skema, kontrak kapabilitas, serta paket backend disediakan setelahnya sebagai antarmuka mesin dan bukti reproduksibilitas—bukan sebagai halaman awal bagi pelajar.

## Perubahan utama

- Memperbarui C110 ke edisi publik 3.0-id.2-r1 yang lengkap: 31 unit dan pembaca PDF 387 halaman pada DOI versi terbaru dalam garis konsep yang sama.
- Memperbarui D40 ke checkpoint Unit 13: pembaca PDF 193 halaman dan pembaca HTML/MathML 42 halaman yang dimirror pada situs pusat dengan 57 berkas dan pembacaan balik publik yang identik byte. Kursus D40 tetap berstatus produksi.
- Menambahkan shard asesmen owner-native O001/A00 tanpa menyalin isi soal: 8.105 asesmen, 13.345 komponen, 5.240 solusi eksplisit, dan 2.865 celah solusi yang tercatat tepat pada 75 modul. Semua identitas adalah UUIDv5; struktur sumber–target dan dua build deterministik lulus.
- Menetapkan kontrak kapabilitas backend global: enam lapisan terpisah, sepuluh profil kapabilitas opsional yang wajib dinyatakan secara jujur, dan dua belas gerbang validasi. Granularitas semantik, granularitas terjemahan, dan navigasi pelajar dipertahankan sebagai proyeksi yang berbeda.
- Memperbarui federasi v2 menjadi 2.479 rekaman: 34 dataset, 40 mata kuliah, 155 permukaan baca, 43 rute publik, 67 peristiwa publikasi, 17 peristiwa QA, dan 2.122 identitas silang v1. Dua build terisolasi menghasilkan 20 berkas yang identik byte dan seluruh validasi skema, rute, hak, sumber, serta hubungan lulus.
- Memperluas paket backend v2.2 agar menyertakan kontrak global dan shard asesmen tervalidasi, sambil mempertahankan backend native setiap pemilik sebagai otoritas utama. JSON tetap merupakan permukaan mesin sekunder; situs dan pembaca adalah permukaan utama bagi pelajar.

Sembilan belas peran mata kuliah selesai menggunakan delapan belas rekaman edisi yang berbeda karena C30 dan C40 berbagi satu edisi Judson. Snapshot ini tidak menyatakan seluruh program atau seluruh terjemahan selesai. Ia menerbitkan hasil yang telah melewati pemeriksaan deterministik dan mempertahankan status produksi secara eksplisit untuk pekerjaan yang masih berjalan.

Provenance engineering: OpenAI Codex gpt-5.6-sol, Ultra, atas instruksi pengguna; kredit penulis, sumber, lisensi, dan kontributor manusia tetap dipertahankan pada setiap komponen.
