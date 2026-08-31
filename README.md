# Program Matematika Indonesia

## ▶ [Mulai belajar di situs Program Matematika Indonesia](https://kokunoyumeto.github.io/program-matematika-indonesia/)

Halaman di atas adalah pintu masuk untuk pelajar: pilih titik mulai, ikuti
prasyarat, lalu buka pembaca HTML atau PDF dari kartu mata kuliah. Berkas JSON,
schema, dan paket backend di repositori ini adalah lapisan mesin—bukan halaman
utama untuk belajar.

Situs ini adalah pintu masuk berbahasa Indonesia untuk sebuah program matematika terbuka berisi 40 mata kuliah, dari perbaikan fondasi sampai kesiapan riset.

Situs publik: <https://kokunoyumeto.github.io/program-matematika-indonesia/>. Setiap kartu edisi lengkap menautkan pembaca, DOI preservasi, dan repositori GitHub korpusnya ketika ketiganya tersedia.

## Cara backend dibangun dan disatukan

Produksi berlangsung secara terdistribusi: 40 peran kurikulum dikerjakan melalui 33 keluarga backend native. Setiap jalur lebih dahulu mempertahankan struktur sumber, identitas, hak, validator, dan kebutuhan pedagogisnya sendiri. Setelah implementasi nyata tersedia, audit lintas-korpus membandingkan kekuatan dan kegagalannya. Lapisan pusat kemudian menambahkan kapsul dan adapter tipis yang dapat direproduksi tanpa mengganti otoritas backend pemilik. Hanya data yang lolos validasi dan mempunyai rute publik yang boleh membangun antarmuka pelajar.

| Keadaan pada 31 Agustus 2026 | Hasil |
|---|---:|
| Peran kurikulum dengan korpus atau spesifikasi terpilih | 40/40 |
| Peran dengan edisi lengkap publik | 35 |
| Peran yang masih diproduksi | 5: A20, A30, B95, C140, D100 |
| Keluarga implementasi native yang dibandingkan | 33 |
| Ikatan peran adapter kontrak 2.3.1 yang diterima | 9 peran melalui 8 paket: A00, B10, C30, C40, C80, C130, D20, D60, D110 |
| Keluarga yang belum mempunyai adapter 2.3.1 dengan replay publik lengkap | 28 |

Hasil backend sudah dipakai oleh pelajar secara nyata: kartu kursus memperoleh aksi baca dan unduh dari data delivery tervalidasi, sedangkan A00 memperoleh peta 8.105 latihan yang membuka jangkar latihan atau solusi yang tepat. Pekerjaan itu masih parsial—bukan klaim bahwa semua keluarga telah dikonvergensikan. [Baca metode dan temuan lengkap](MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md) atau [jelajahi katalog backend yang berorientasi pelajar](docs/backend/index.html).

## Yang tersedia

- Peta empat tingkat: A (fondasi), B (dasar universitas), C (inti sarjana), dan D (fondasi pascasarjana serta riset).
- Prasyarat yang dapat diikuti langsung antarkartu.
- Pencarian dan penyaringan berdasarkan tingkat, bidang, dan status korpus.
- Keempat puluh peran kini memiliki korpus terpilih atau spesifikasi asli yang dibekukan; status produksi dan penyelesaian tetap dicatat terpisah.
- Tiga puluh lima peran mata kuliah sudah memiliki edisi lengkap yang dapat dibaca secara publik; lima lainnya—A20, A30, B95, C140, dan D100—tetap berstatus produksi. Ke-35 peran lengkap itu memakai 31 rekaman DOI edisi terbit yang berbeda karena beberapa peran berbagi satu keluarga edisi. A10 kini lengkap 82/82 modul dalam pembaca 2.154 halaman; B20, B30, dan B50 lengkap bersama buku soal serta backend modularnya; C20 lengkap sebagai pembaca 241 halaman; D20 lengkap 17/17 bab; D30 lengkap sebagai pembaca 447 halaman dengan lima laboratorium dan dua formulir asesmen; D40 kini lengkap dengan pembaca HTML dan paket luring terverifikasi; D60 lengkap pada v0.31.7; dan keluarga Lebl menutup B70, C10, C20, serta C50 dalam lineage kompositnya. Status lengkap dan produksi tidak dicampur.
- Backend bersama v1 tetap dibekukan: 38 tabel ketat, identitas UUIDv5, varian bahasa terpisah, rute pembelajaran, hak komponen, bukti build/QA, JSONL kanonik, dan CSV lossless. Paket pusat 2.122 rekaman telah lolos dua ekspor identik. Tiga belas bukti migrasi korpus lengkap kini terikat; tambahan terbaru adalah edisi D20 Erdman, yang memproyeksikan 32.383 rekaman native dan 2.104 baris indeks menjadi 41.689 rekaman umum melalui adapter virtual lossless tanpa menyalin backend besar pemilik.
- Federasi v2 adalah lapisan penghubung ringkas, bukan pengganti situs atau buku: 2.490 rekaman menghubungkan 34 dataset, 40 mata kuliah, 164 permukaan baca unik, 43 rute publik, 69 peristiwa publikasi, 17 peristiwa QA, dan 2.122 identitas v1. Buku teks, buku soal, jawaban, dan laboratorium yang berbeda memperoleh permukaan belajar sendiri. Satu URL yang sama tetap direpresentasikan satu kali dengan beberapa aksi (`learn`, `html`, `pdf`, atau `offline`) agar antarmuka pelajar dan mesin tidak menduplikasi bahan yang sama. Seluruh sumber korpus dan backend native pemilik tetap menjadi otoritas; rute yang belum terbit dilabeli `planned_not_published`.
- Lapisan publikasi langsung mempertahankan semantik katalog awal sambil menampilkan bukti edisi yang lebih baru. B30, yang sebelumnya berada pada WIP.18 melalui Bagian 3.7, kini selesai sebagai edisi publik 1.243 halaman; D30 telah menutup kursus pada checkpoint 38 lengkap. D60 kini merupakan edisi komposit lengkap v0.31.7: pembaca HTML tetap pintu belajar utama, PDF 564 halaman adalah unduhan edisi, dan ZIP sumber/backend hanya suplemen reproduksibilitas sekunder. A10, C90, dan paket gabungan D70 juga benar-benar lengkap. Checkpoint yang belum lengkap tidak dihitung sebagai korpus selesai.
- Kemajuan belajar dapat dicatat secara lokal di browser: penyelesaian, penempatan, kesetaraan, dan waiver khusus satu sisi prasyarat. Data ini tidak dikirim ke server, dan kelayakan mata kuliah selalu dihitung ulang—tidak disimpan sebagai fakta baru.
- Lapisan tambahan v2.1 kini membuktikan proyeksi unit dan pencarian tanpa menyalin prosa: A00 (75 unit/201 relasi), B10 (161/284), C100 (939/994), dan D20 (19/686) semuanya lolos validasi deterministik. C100 memiliki [laman kursus](docs/id-ID/courses/C100/index.html), 20 pintu bab, pembaca HTML semantik 3.994.608 byte, seluruh 32 subbagian latihan, crosswalk 253 solusi, dan PDF solusi 331 halaman yang dipertahankan identik; D20 memiliki [indeks pelajar](docs/id-ID/courses/D20/index.html) ke 17 rute bab pemilik yang benar-benar terbit. Manifest D20 lama tetap kompatibel byte demi byte.
- Federasi riset akses pendidikan dipisahkan dari unit matematika: [paket 490 rekaman](backend/research/educational-access-v0.1.0/README.md) melayani profil bahasa, bukti, rekomendasi, intervensi aksesibilitas, dan sumber kurikulum; [proyeksi publik ringkas](docs/data/educational-access.json) tetap data mesin sekunder, bukan tombol belajar utama.
- Backend v2.1 juga memuat lapisan perencanaan akses pendidikan yang hash-bound: 29 unit kurikulum sumber, 13 portofolio kumulatif, 10 sisi prasyarat portofolio, 5 kedalaman adaptasi, 8 turunan aksesibilitas, 12 asumsi komputasi, dan 3 skenario. Ini membuat unit dapat dipilih menurut isi, kedalaman terjemahan, keluaran aksesibilitas, dan biaya kerja—tanpa mencampur prosa, data populasi, atau klaim hasil belajar ke dalam katalog mata kuliah.
- Paket pendahulu v2.2 A00 yang tetap dipreservasi mengubah pengalaman dari “satu skema memaksa semua buku” menjadi kontrak global enam lapisan dengan sepuluh kapabilitas opsional dan dua belas gerbang validasi. Pilot itu mempertahankan 519.678 rekaman native pada backend pemilik, memetakan 75 unit belajar secara stabil, dan menambahkan shard owner-native berisi 8.105 asesmen, 5.240 solusi eksplisit, serta 2.865 celah solusi yang dinyatakan jujur. Profil kapabilitas membedakan semantik, terjemahan, navigasi, aset, asesmen, aksesibilitas, solusi, hak, provenance, dan QA; dua build identik serta pemeriksaan balik mencegah federasi menghilangkan struktur native atau menyamarkan data yang tidak ada. Adapter A00 kontrak 2.3.1 pada butir berikutnya adalah penerusnya sekarang.
- Overlay penerus backend v2.3 kini menerima sembilan ikatan peran melalui delapan paket kontrak 2.3.1: A00, B10, C30, C40, C80, C130, D20, D60, dan D110. Lima ikatan sudah memiliki replay publik lengkap; C30, C40, C80, dan C130 diterima lokal dan menunggu publikasi rilis pusat penerus. Adapter A00 + O001 memakai ulang spine ringkas 1.313 rekaman, mempertahankan 24.315 rekaman asesmen native sebagai shard rujukan, dan menghubungkan 8.105 asesmen serta 13.345 komponen ke 21.450 jangkar HTML yang tepat tanpa menjadikannya unit navigasi. Halaman [Latihan & diagnosis A00](docs/id-ID/courses/A00/latihan/index.html) membuat hasil backend itu langsung berguna bagi pelajar sambil menandai jujur 2.865 latihan tanpa solusi eksplisit dalam sumber. Paket konformansi A00 lama pada [rilis pusat v0.62.6](https://github.com/KokunoYumeto/program-matematika-indonesia/releases/tag/v0.62.6) tetap publik sebagai bukti pendahulu. Adapter B10 v0.2.0 memetakan 161 unit dan 284 relasi ke 1.264 rekaman; peta Judson bersama memberi [15 bab C30](docs/backend/judson/C30.html) dan [8 bab C40](docs/backend/judson/C40.html) dari satu graf sumber dengan 23 sambungan native tanpa menggandakan unit; [Open Logic C80](docs/backend/openlogic/C80.html) mengikat 722/722 unit ke pembaca 1.116 halaman; [Riset Operasi C130](docs/backend/c130/C130.html) mengikat 1.993 unit dan tujuh rute publik ke pembaca 666 halaman; D20 memetakan 138.894 rekaman kanonik; D60 memvalidasi 27.642 rekaman; dan D110 memvalidasi 41.460 rekaman. Kesembilan ikatan mempertahankan backend native sumber, memakai proyeksi JSONL/CSV yang dapat dibalik, dan tidak mengklaim kepatuhan 31 peran lain. Indeks immutable rilis terdahulu tetap berada di [indeks backend v2.3](docs/schema/v2.3/index.html); overlay penerus tersedia di [katalog backend](docs/backend/index.html).

- Metode backend global sengaja dimulai dari implementasi native yang berbeda-beda, bukan dari satu skema yang dipaksakan. Tiga puluh tiga keluarga implementasi untuk 40 peran kemudian dibandingkan pada identitas stabil, relasi, status terjemahan, provenance/hak, aksesibilitas, replay deterministik, pertukaran reversibel, dan pemakaian nyata oleh pembaca. [Catatan metode dan temuan](MODULAR_BACKEND_METHOD_AND_FINDINGS_V1.md), [indeks pola 33 keluarga](backend/authority/modular-backend-pattern-index-v1.json), dan [kapsul kursus terbuka](backend/course-capsule-v1/README.md) mempertahankan hasil sintesis tersebut tanpa mengganti backend native pemilik.
- Tautan hanya menuju edisi atau arsip publik yang identitasnya sudah diketahui.

Situs publik dibangun langsung dari folder [`docs`](docs). Tidak ada akun, pelacak, cookie, atau layanan pihak ketiga yang diperlukan untuk menggunakannya.

## Snapshot Zenodo aktif

Snapshot publik terbaru selalu tersedia melalui [lineage konsep Zenodo 10.5281/zenodo.22059707](https://doi.org/10.5281/zenodo.22059707). Setiap versi mempertahankan situs belajar sebagai tautan pertama dan menempatkan JSON, CSV, skema, serta paket backend sebagai lampiran mesin sekunder. Lampiran publik mencakup catatan metode dan temuan, indeks pola 33 keluarga, skema kapsul dan kosakata kapabilitas, inventaris adapter, receipt validasi/readback, serta artefak belajar luring. Snapshot sengaja berstatus pekerjaan berjalan: 40 dari 40 peran sudah memiliki korpus terpilih atau spesifikasi asli yang dibekukan dan backend bersama dapat direproduksi, tetapi produksi lima peran—A20, A30, B95, C140, dan D100—serta penutupan solusi, migrasi backend per-korpus, dan beberapa edisi final masih berlangsung.

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
