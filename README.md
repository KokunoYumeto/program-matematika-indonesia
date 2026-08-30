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
- Dua puluh delapan peran mata kuliah sudah memiliki edisi lengkap yang dapat dibaca secara publik. Peran-peran itu memakai dua puluh tujuh rekaman edisi berbeda karena C30 dan C40 berbagi satu edisi Judson. A10 kini lengkap 82/82 modul dalam pembaca 2.154 halaman; B20 dan B50 lengkap bersama buku soal serta backend modularnya; D20 lengkap 17/17 bab; D60 lengkap pada v0.31.7; dan paket gabungan D70 lengkap dalam empat komponen. Status lengkap dan produksi tidak dicampur.
- Backend bersama v1 tetap dibekukan: 38 tabel ketat, identitas UUIDv5, varian bahasa terpisah, rute pembelajaran, hak komponen, bukti build/QA, JSONL kanonik, dan CSV lossless. Paket pusat 2.122 rekaman telah lolos dua ekspor identik. Tiga belas bukti migrasi korpus lengkap kini terikat; tambahan terbaru adalah edisi D20 Erdman, yang memproyeksikan 32.383 rekaman native dan 2.104 baris indeks menjadi 41.689 rekaman umum melalui adapter virtual lossless tanpa menyalin backend besar pemilik.
- Federasi v2 adalah lapisan penghubung ringkas, bukan pengganti situs atau buku: 2.490 rekaman menghubungkan 34 dataset, 40 mata kuliah, 164 permukaan baca unik, 43 rute publik, 69 peristiwa publikasi, 17 peristiwa QA, dan 2.122 identitas v1. Buku teks, buku soal, jawaban, dan laboratorium yang berbeda memperoleh permukaan belajar sendiri. Satu URL yang sama tetap direpresentasikan satu kali dengan beberapa aksi (`learn`, `html`, `pdf`, atau `offline`) agar antarmuka pelajar dan mesin tidak menduplikasi bahan yang sama. Seluruh sumber korpus dan backend native pemilik tetap menjadi otoritas; rute yang belum terbit dilabeli `planned_not_published`.
- Lapisan publikasi langsung mempertahankan semantik katalog v0.62.0 sambil menampilkan bukti pemilik yang lebih baru. B30 tetap produksi pada WIP.18 melalui Bagian 3.7 dan D30 berada pada checkpoint publik 36. D60 kini merupakan edisi komposit lengkap v0.31.7: pembaca HTML tetap pintu belajar utama, PDF 564 halaman adalah unduhan edisi, dan ZIP sumber/backend hanya suplemen reproduksibilitas sekunder. A10, C90, dan paket gabungan D70 juga benar-benar lengkap. Checkpoint yang belum lengkap tidak dihitung sebagai korpus selesai.
- Kemajuan belajar dapat dicatat secara lokal di browser: penyelesaian, penempatan, kesetaraan, dan waiver khusus satu sisi prasyarat. Data ini tidak dikirim ke server, dan kelayakan mata kuliah selalu dihitung ulang—tidak disimpan sebagai fakta baru.
- Lapisan tambahan v2.1 kini membuktikan proyeksi unit dan pencarian tanpa menyalin prosa: A00 (75 unit/201 relasi), B10 (161/284), C100 (939/994), dan D20 (19/686) semuanya lolos validasi deterministik. C100 memiliki [laman kursus](docs/id-ID/courses/C100/index.html), 20 pintu bab, pembaca HTML semantik 3.994.608 byte, seluruh 32 subbagian latihan, crosswalk 253 solusi, dan PDF solusi 331 halaman yang dipertahankan identik; D20 memiliki [indeks pelajar](docs/id-ID/courses/D20/index.html) ke 17 rute bab pemilik yang benar-benar terbit. Manifest D20 lama tetap kompatibel byte demi byte.
- Federasi riset akses pendidikan dipisahkan dari unit matematika: [paket 490 rekaman](backend/research/educational-access-v0.1.0/README.md) melayani profil bahasa, bukti, rekomendasi, intervensi aksesibilitas, dan sumber kurikulum; [proyeksi publik ringkas](docs/data/educational-access.json) tetap data mesin sekunder, bukan tombol belajar utama.
- Backend v2.1 juga memuat lapisan perencanaan akses pendidikan yang hash-bound: 29 unit kurikulum sumber, 13 portofolio kumulatif, 10 sisi prasyarat portofolio, 5 kedalaman adaptasi, 8 turunan aksesibilitas, 12 asumsi komputasi, dan 3 skenario. Ini membuat unit dapat dipilih menurut isi, kedalaman terjemahan, keluaran aksesibilitas, dan biaya kerja—tanpa mencampur prosa, data populasi, atau klaim hasil belajar ke dalam katalog mata kuliah.
- Backend v2.2 mengubah pengalaman dari “satu skema memaksa semua buku” menjadi kontrak global enam lapisan dengan sepuluh kapabilitas opsional dan dua belas gerbang validasi. Pilot A00 mempertahankan 519.678 rekaman native pada backend pemilik, memetakan 75 unit belajar secara stabil, dan menambahkan shard owner-native berisi 8.105 asesmen, 5.240 solusi eksplisit, serta 2.865 celah solusi yang dinyatakan jujur. Profil kapabilitas membedakan semantik, terjemahan, navigasi, aset, asesmen, aksesibilitas, solusi, hak, provenance, dan QA; dua build identik serta pemeriksaan balik mencegah federasi menghilangkan struktur native atau menyamarkan data yang tidak ada.
- Backend v2.3 kini memiliki tiga bukti jalur yang diterima: A00, B10, dan D60. Paket konformansi v0.1.1 pada [rilis pusat v0.62.6](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.6) tetap dibatasi pada A00 + O001. Adapter B10 v0.2.0 memakai kontrak generik 2.3.1 untuk memetakan 161 unit dan 284 relasi ke 1.264 rekaman tanpa menyalin prosa atau 163.583 rekaman native pemilik. Adapter D60 v0.1.0 pada [rilis pusat v0.62.10](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.10) memvalidasi 27.642 rekaman kanonik, 2.204 unit, 6.279 pemetaan materialisasi-native reversibel, dan 19 tabel JSONL/CSV, sambil mempertahankan 8.338 rekaman backend native pemilik tanpa menyalin prosa. Rute belajar ketiganya tetap halaman HTML pemilik; tiga bukti ini tidak mengklaim kepatuhan 37 peran lain. Rincian dan skema publik berada di [indeks backend v2.3](docs/schema/v2.3/index.html).
- Tautan hanya menuju edisi atau arsip publik yang identitasnya sudah diketahui.

Situs publik dibangun langsung dari folder [`docs`](docs). Tidak ada akun, pelacak, cookie, atau layanan pihak ketiga yang diperlukan untuk menggunakannya.

## Snapshot Zenodo aktif

Snapshot publik terbaru selalu tersedia melalui [lineage konsep Zenodo 10.5281/zenodo.22059707](https://doi.org/10.5281/zenodo.22059707). Setiap versi mempertahankan situs belajar sebagai tautan pertama dan menempatkan JSON, CSV, skema, serta paket backend sebagai lampiran mesin sekunder. Snapshot sengaja berstatus pekerjaan berjalan: 40 dari 40 peran sudah memiliki korpus terpilih atau spesifikasi asli yang dibekukan dan backend bersama dapat direproduksi, tetapi banyak terjemahan, penutupan solusi, migrasi backend per-korpus, dan edisi final masih diproduksi.

Zenodo adalah jalur preservasi mandiri, bukan sekadar salinan GitHub. Setiap perubahan keadaan kanon yang material memperoleh versi baru pada lineage konsep yang sama; GitHub dan Zenodo tetap dua rute publik independen.

## Memeriksa data

Jalankan:

```text
node scripts/validate-static-site.mjs
```

Pemeriksa memastikan tepat 40 kode mata kuliah, pemetaan semantik 40/40 ke `ownerLane` yang tepat, tidak ada peran sumber yang masih terbuka, prasyarat yang tertutup, jumlah tingkat yang benar, serta kontrak dasar HTML dan tautan.

Backend bersama dapat diregenerasi dan divalidasi dengan skrip Python dalam folder [`scripts`](scripts). [Status backend v0.55 dan rancangan fase dua](backend/GLOBAL_BACKEND_STATUS_V055.md) menjelaskan apa yang sudah diadopsi dari backend setiap korpus, batas federasi saat ini, dukungan riset akses pendidikan, dan lapisan unit/rute yang masih harus dibangun. Catatan keputusan awal tetap berada di [`backend/BACKEND_CONVERGENCE_V1.md`](backend/BACKEND_CONVERGENCE_V1.md). Prosedur migrasi tanpa mengganggu produksi korpus berada di [`backend/MIGRATION_HANDOFF_V1.md`](backend/MIGRATION_HANDOFF_V1.md); setiap bukti migrasi mengikuti [`schemas/backend-migration-receipt-v1.schema.json`](schemas/backend-migration-receipt-v1.schema.json).

Arsip v2.3 menyertakan generator, validator, pemeriksa replay, skema, manifest, checksum, dan batas cakupan. Dua build direktori serta dua arsip deterministik harus identik byte-for-byte sebelum paket dapat masuk ke snapshot pusat.

Koordinasi, rekayasa backend, dan penerbitan snapshot pusat ini dilakukan oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna. Kredit penulis, penerjemah manusia, dan kontributor setiap korpus tetap dipertahankan pada edisi dan metadata komponennya masing-masing.

## Memperbarui kanon

Data mata kuliah berada di [`docs/courses.js`](docs/courses.js). Pilihan sementara tidak boleh diubah menjadi `production` atau `published` sampai korpusnya benar-benar dibekukan dalam catatan koordinasi program. Tautan publik hanya ditambahkan setelah edisi tersebut dapat dibaca kembali dari tujuan publik yang tepat.

## Lisensi

Kode situs tersedia berdasarkan [Lisensi MIT](LICENSE). Teks deskriptif dan metadata kurikulum asli pada situs ini tersedia berdasarkan [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Buku dan edisi yang ditautkan tetap menggunakan lisensi masing-masing; situs ini tidak mengganti atau menyatukan lisensi karya-karya tersebut.

---

<span lang="en">English note: This repository hosts an Indonesian-first navigation layer for an open 40-course mathematics curriculum. English is intentionally secondary.</span>
