# Program Matematika Indonesia v0.59.0

Mulai belajar melalui situs HTML untuk pelajar:

<https://kokunoyumeto.github.io/program-matematika-indonesia/>

Situs itu adalah pintu utama: pilih titik mulai, ikuti prasyarat, lalu buka pembaca HTML atau PDF dari kartu mata kuliah. Arsip Zenodo menampilkan PDF dan HTML mulai-belajar terlebih dahulu. Katalog JSON, skema, serta paket backend v1, v2, v2.1, dan v2.2 disediakan setelahnya sebagai antarmuka mesin dan bukti reproduksibilitas—bukan sebagai halaman awal bagi pelajar.

## Perubahan utama

- Menambahkan D120, *Membaca Riset, Eksposisi, dan Kerja Matematis Reprodusibel*, sebagai edisi lengkap kesembilan belas: sembilan unit publik dengan pembaca HTML, arsip offline, DOI, dan repositori yang dapat dibuka langsung dari kartu pelajar.
- Mengindeks sepuluh rute publik pemilik yang baru atau diperbarui tanpa menyebut edisi parsial sebagai selesai: A20 41/83 modul (1.732 halaman), B30 CLP2 sampai §3.5 (1.102 halaman), komponen STAT 415 C140 lengkap, serta checkpoint D30, D50, D60, D80, D90, dan D100. D120 adalah satu-satunya penambahan status selesai pada rilis ini.
- Memperluas workbook C100 yang berlisensi terpisah menjadi Unit 001–011 sepanjang 123 halaman, sambil mempertahankan kursus utama C100 yang lengkap dan bersih hak sebagai jalur HTML utama.
- Memperbarui federasi v2 menjadi 2.478 rekaman: 34 dataset, 40 mata kuliah, 154 permukaan baca, 43 rute publik, 67 peristiwa publikasi, 17 peristiwa QA, dan 2.122 identitas silang v1. Dua build terisolasi menghasilkan 20 berkas yang identik byte; 23 uji negatif dan deterministik lulus.
- Menambahkan pilot backend v2.2 untuk A00. Pilot ini mempertahankan 519.678 rekaman native pada backend pemilik tanpa menyalinnya, lalu memproyeksikan 1.313 rekaman ketat pada 19 tabel untuk 75 unit dan rute pelajar. Sembilan puluh dua baris pemetaan identitas, ekstraksi balik, dan dua build identik membuktikan bahwa struktur native tetap dapat direkonstruksi.
- Mengikat setiap rute HTML baru pada pembacaan balik publik serta mengikat manifes penerimaan, bukti rute pemilik, dan reservasi DOI ke bundel rilis. Lapisan mesin tetap sekunder terhadap HTML dan PDF pelajar.

Sembilan belas peran mata kuliah selesai itu menggunakan delapan belas rekaman edisi yang berbeda karena C30 dan C40 berbagi satu edisi Judson. Snapshot ini tidak menyatakan seluruh terjemahan selesai. Ia menerbitkan hasil yang telah melewati pemeriksaan deterministik dan mempertahankan status produksi secara eksplisit untuk pekerjaan yang masih berjalan.

Provenance engineering: OpenAI Codex gpt-5.6-sol, Ultra, atas instruksi pengguna; kredit penulis, sumber, lisensi, dan kontributor manusia tetap dipertahankan pada setiap komponen.
