# Program Matematika Indonesia

## ▶ [Mulai belajar di situs Program Matematika Indonesia](https://kokunoyumeto.github.io/program-matematika-indonesia/)

Halaman di atas adalah pintu masuk untuk pelajar: pilih titik mulai, ikuti
prasyarat, lalu buka pembaca HTML atau PDF dari kartu mata kuliah. Berkas JSON,
schema, dan paket backend di repositori ini adalah lapisan mesin—bukan halaman
utama untuk belajar.

Situs ini adalah pintu masuk berbahasa Indonesia untuk sebuah program matematika terbuka berisi 40 mata kuliah, dari perbaikan fondasi sampai kesiapan riset.

Situs publik: <https://kokunoyumeto.github.io/program-matematika-indonesia/>. Setiap kartu edisi lengkap menautkan pembaca, DOI preservasi, dan repositori GitHub korpusnya ketika ketiganya tersedia.

## Yang tersedia

- Peta empat tingkat: A (fondasi), B (dasar universitas), C (inti sarjana), dan D (fondasi pascasarjana serta riset).
- Prasyarat yang dapat diikuti langsung antarkartu.
- Pencarian dan penyaringan berdasarkan tingkat, bidang, dan status korpus.
- Keempat puluh peran kini memiliki korpus terpilih atau spesifikasi asli yang dibekukan; status produksi dan penyelesaian tetap dicatat terpisah.
- Sembilan belas peran mata kuliah sudah memiliki edisi lengkap yang dapat dibaca secara publik. Sembilan belas peran itu memakai delapan belas rekaman edisi berbeda karena C30 dan C40 berbagi satu edisi Judson. Tambahan terbaru adalah D120 Praktik Riset yang lengkap sebagai kursus sembilan unit. C100 Geometri tetap membuka kursus utama yang bersih hak melalui pembaca HTML semantik; workbook Unit 001–011 sepanjang 123 halaman berada pada lini lisensi terpisah dan tampil sebagai sumber tambahan.
- Backend bersama v1 tetap dibekukan: 38 tabel ketat, identitas UUIDv5, varian bahasa terpisah, rute pembelajaran, hak komponen, bukti build/QA, JSONL kanonik, dan CSV lossless. Paket pusat 2.122 rekaman telah lolos dua ekspor identik. Tiga belas bukti migrasi korpus lengkap kini terikat; tambahan terbaru adalah edisi D20 Erdman, yang memproyeksikan 32.383 rekaman native dan 2.104 baris indeks menjadi 41.689 rekaman umum melalui adapter virtual lossless tanpa menyalin backend besar pemilik.
- Federasi v2 adalah lapisan penghubung ringkas, bukan pengganti situs atau buku: 2.478 rekaman menghubungkan 34 dataset, 40 mata kuliah, 154 permukaan baca unik, 43 rute publik, 67 peristiwa publikasi, 17 peristiwa QA, dan 2.122 identitas v1. Satu URL pembaca direpresentasikan satu kali dengan beberapa aksi (`learn`, `html`, atau `offline`) agar antarmuka pelajar dan mesin tidak menduplikasi permukaan yang sama. Seluruh sumber korpus dan backend native pemilik tetap menjadi otoritas; rute yang belum terbit dilabeli `planned_not_published`.
- Checkpoint produksi publik yang ditambahkan atau diperbarui pada v0.59.0 mencakup A20 (41/83 modul; 1.732 halaman), B30 CLP2 sampai §3.5 (1.102 halaman), komponen STAT 415 C140 lengkap, D30 checkpoint 32, D50 sampai Unit 16 (261 halaman), D60 checkpoint v0.31.1, D80 sampai Unit 047 (308 halaman), D90 Original Tranche 02, dan D100 sampai Unit 28 dari 30 (476 halaman). D120 kini lengkap; status sembilan kursus lain tetap parsial dan tidak dihitung sebagai korpus selesai.
- Lapisan tambahan v2.1 kini membuktikan proyeksi unit dan pencarian tanpa menyalin prosa: A00 (75 unit/201 relasi), B10 (161/284), C100 (939/994), dan D20 (19/686) semuanya lolos validasi deterministik. C100 memiliki [laman kursus](docs/id-ID/courses/C100/index.html), 20 pintu bab, pembaca HTML semantik 3.994.608 byte, seluruh 32 subbagian latihan, crosswalk 253 solusi, dan PDF solusi 331 halaman yang dipertahankan identik; D20 memiliki [indeks pelajar](docs/id-ID/courses/D20/index.html) ke 17 rute bab pemilik yang benar-benar terbit. Manifest D20 lama tetap kompatibel byte demi byte.
- Federasi riset akses pendidikan dipisahkan dari unit matematika: [paket 490 rekaman](backend/research/educational-access-v0.1.0/README.md) melayani profil bahasa, bukti, rekomendasi, intervensi aksesibilitas, dan sumber kurikulum; [proyeksi publik ringkas](docs/data/educational-access.json) tetap data mesin sekunder, bukan tombol belajar utama.
- Backend v2.1 juga memuat lapisan perencanaan akses pendidikan yang hash-bound: 29 unit kurikulum sumber, 13 portofolio kumulatif, 10 sisi prasyarat portofolio, 5 kedalaman adaptasi, 8 turunan aksesibilitas, 12 asumsi komputasi, dan 3 skenario. Ini membuat unit dapat dipilih menurut isi, kedalaman terjemahan, keluaran aksesibilitas, dan biaya kerja—tanpa mencampur prosa, data populasi, atau klaim hasil belajar ke dalam katalog mata kuliah.
- Pilot v2.2 untuk A00 mengubah pengalaman dari “satu skema memaksa semua buku” menjadi profil-lajur yang ketat: 519.678 rekaman native tetap berada pada backend pemilik, sedangkan 75 unit belajar memperoleh pemetaan stabil, rute pelajar, status terkontrol, dan ekstraksi balik yang dapat diuji. Profil kemampuan menyatakan dengan jujur apakah semantik, aset, asesmen, aksesibilitas, dan solusi dimaterialkan, direferensikan, atau belum diproyeksikan. Dua build identik dan pemeriksaan balik mencegah federasi menghilangkan struktur native atau menyamarkan data yang tidak ada.
- Tautan hanya menuju edisi atau arsip publik yang identitasnya sudah diketahui.

Situs publik dibangun langsung dari folder [`docs`](docs). Tidak ada akun, pelacak, cookie, atau layanan pihak ketiga yang diperlukan untuk menggunakannya.

## Snapshot Zenodo aktif

Snapshot v0.59.0 dipertahankan di [Zenodo, DOI 10.5281/zenodo.22133203](https://doi.org/10.5281/zenodo.22133203), dalam [lineage konsep 10.5281/zenodo.22059707](https://doi.org/10.5281/zenodo.22059707). Snapshot ini sengaja berstatus pekerjaan berjalan: 40 dari 40 peran sudah memiliki korpus terpilih atau spesifikasi asli yang dibekukan dan backend bersama dapat direproduksi, tetapi sebagian besar terjemahan, penutupan solusi, migrasi backend per-korpus, dan edisi final masih diproduksi. v0.59.0 menambahkan sepuluh rute pemilik yang terverifikasi, penyelesaian D120, workbook C100 Unit 001–011, serta pilot backend v2.2 yang reversibel. Zenodo membuka `00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.59.0.pdf` sebagai pratinjau manusia; `01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.59.0.html` adalah salinan HTML mandiri, dan situs belajar publik tetap menjadi pintu masuk utama.

Zenodo adalah jalur preservasi mandiri, bukan sekadar salinan GitHub. Setiap perubahan keadaan kanon yang material akan memperoleh versi baru pada lineage konsep yang sama. Akses akun GitHub yang sempat ditangguhkan telah dipulihkan; snapshot Zenodo tetap dipertahankan sebagai arsip independen.

## Memeriksa data

Jalankan:

```text
node scripts/validate-static-site.mjs
```

Pemeriksa memastikan tepat 40 kode mata kuliah, pemetaan semantik 40/40 ke `ownerLane` yang tepat, tidak ada peran sumber yang masih terbuka, prasyarat yang tertutup, jumlah tingkat yang benar, serta kontrak dasar HTML dan tautan.

Backend bersama dapat diregenerasi dan divalidasi dengan skrip Python dalam folder [`scripts`](scripts). [Status backend v0.55 dan rancangan fase dua](backend/GLOBAL_BACKEND_STATUS_V055.md) menjelaskan apa yang sudah diadopsi dari backend setiap korpus, batas federasi saat ini, dukungan riset akses pendidikan, dan lapisan unit/rute yang masih harus dibangun. Catatan keputusan awal tetap berada di [`backend/BACKEND_CONVERGENCE_V1.md`](backend/BACKEND_CONVERGENCE_V1.md). Prosedur migrasi tanpa mengganggu produksi korpus berada di [`backend/MIGRATION_HANDOFF_V1.md`](backend/MIGRATION_HANDOFF_V1.md); setiap bukti migrasi mengikuti [`schemas/backend-migration-receipt-v1.schema.json`](schemas/backend-migration-receipt-v1.schema.json).

Koordinasi, rekayasa backend, dan penerbitan snapshot pusat ini dilakukan oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna. Kredit penulis, penerjemah manusia, dan kontributor setiap korpus tetap dipertahankan pada edisi dan metadata komponennya masing-masing.

## Memperbarui kanon

Data mata kuliah berada di [`docs/courses.js`](docs/courses.js). Pilihan sementara tidak boleh diubah menjadi `production` atau `published` sampai korpusnya benar-benar dibekukan dalam catatan koordinasi program. Tautan publik hanya ditambahkan setelah edisi tersebut dapat dibaca kembali dari tujuan publik yang tepat.

## Lisensi

Kode situs tersedia berdasarkan [Lisensi MIT](LICENSE). Teks deskriptif dan metadata kurikulum asli pada situs ini tersedia berdasarkan [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Buku dan edisi yang ditautkan tetap menggunakan lisensi masing-masing; situs ini tidak mengganti atau menyatukan lisensi karya-karya tersebut.

---

<span lang="en">English note: This repository hosts an Indonesian-first navigation layer for an open 40-course mathematics curriculum. English is intentionally secondary.</span>
