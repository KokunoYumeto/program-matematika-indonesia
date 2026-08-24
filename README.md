# Program Matematika Indonesia

Situs ini adalah pintu masuk berbahasa Indonesia untuk sebuah program matematika terbuka berisi 40 mata kuliah, dari perbaikan fondasi sampai kesiapan riset.

Situs publik: <https://kokunoyumeto.github.io/program-matematika-indonesia/>. Setiap kartu edisi lengkap menautkan pembaca, DOI preservasi, dan repositori GitHub korpusnya ketika ketiganya tersedia.

## Yang tersedia

- Peta empat tingkat: A (fondasi), B (dasar universitas), C (inti sarjana), dan D (fondasi pascasarjana serta riset).
- Prasyarat yang dapat diikuti langsung antarkartu.
- Pencarian dan penyaringan berdasarkan tingkat, bidang, dan status korpus.
- Keempat puluh peran kini memiliki korpus terpilih atau spesifikasi asli yang dibekukan; status produksi dan penyelesaian tetap dicatat terpisah.
- Lima belas peran mata kuliah sudah memiliki edisi lengkap yang dapat dibaca secara publik. Kelima belas peran itu memakai empat belas rekaman edisi berbeda karena C30 dan C40 berbagi satu edisi Judson. v0.51.0 mempertahankan jumlah itu, menutup audit pemilihan sumber O001–O018, dan memperbarui batas publik yang terverifikasi tanpa menyamarkan edisi kerja atau paket pembantu sebagai korpus lengkap.
- Backend bersama v1 kini dibekukan: 38 tabel ketat, identitas UUIDv5, varian bahasa terpisah, rute pembelajaran, hak komponen, bukti build/QA, JSONL kanonik, dan CSV lossless. Paket pusat 2.122 rekaman telah lolos dua ekspor identik. Sepuluh bukti migrasi korpus lengkap kini terikat, termasuk bukti baru A00, C120, dan C130. Seluruh migrasi mempertahankan backend native pemilik sebagai otoritas, memvalidasi transformasi secara deterministik, dan tidak menggandakan backend besar pemilik ke paket pusat.
- Tautan hanya menuju edisi atau arsip publik yang identitasnya sudah diketahui.

Situs publik dibangun langsung dari folder [`docs`](docs). Tidak ada akun, pelacak, cookie, atau layanan pihak ketiga yang diperlukan untuk menggunakannya.

## Snapshot Zenodo aktif

Snapshot v0.51.0 dipertahankan di [Zenodo, DOI 10.5281/zenodo.22086601](https://doi.org/10.5281/zenodo.22086601), dalam [lineage konsep 10.5281/zenodo.22059707](https://doi.org/10.5281/zenodo.22059707). Snapshot ini sengaja berstatus pekerjaan berjalan: 40 dari 40 peran sudah memiliki korpus terpilih atau spesifikasi asli yang dibekukan dan backend bersama dapat direproduksi, tetapi sebagian besar terjemahan, penutupan solusi, migrasi backend per-korpus, dan edisi final masih diproduksi. Tidak ada peran baru yang dinyatakan selesai pada v0.51.0. Hub kini mengikat CLP-2 WIP.9 (674 halaman), keluarga Lebl U336, D40 Unit 09 (77 halaman), D50 Unit 10 dengan Unit 11–13 hanya lokal, D60 Roberts Kuliah 1–30 plus Fomberg §§1.1–1.2 (362 halaman), checkpoint pendamping D90 MIT L10, dan D100 Unit 15 (267 halaman; Unit 16–18 hanya lokal dan Unit 19 dibekukan tetapi belum didispatch). HP-A30-001 berstatus manager-clean untuk lima unit tetapi masih menunggu owner-QA serta integrasi tiga-arah; paket itu belum terintegrasi atau diterbitkan. Arsitektur sumber C100, D70, dan D90 juga telah diperbaiki sesuai audit terakhir. Setiap mata kuliah membawa `ownerLane` yang divalidasi terhadap peta semantik lengkap; pemeriksaan independen terbaru meluluskan 53 dari 53 cek atas 40 peran, 82 ujung dependensi, ikatan sumber, dan grup pemilik bersama.

Zenodo adalah jalur preservasi mandiri, bukan sekadar salinan GitHub. Setiap perubahan keadaan kanon yang material akan memperoleh versi baru pada lineage konsep yang sama. Akses akun GitHub yang sempat ditangguhkan telah dipulihkan; snapshot Zenodo tetap dipertahankan sebagai arsip independen.

## Memeriksa data

Jalankan:

```text
node scripts/validate-static-site.mjs
```

Pemeriksa memastikan tepat 40 kode mata kuliah, pemetaan semantik 40/40 ke `ownerLane` yang tepat, tidak ada peran sumber yang masih terbuka, prasyarat yang tertutup, jumlah tingkat yang benar, serta kontrak dasar HTML dan tautan.

Backend bersama dapat diregenerasi dan divalidasi dengan skrip Python dalam folder [`scripts`](scripts). Kontrak lengkap dan alasan pemilihannya berada di [`backend/BACKEND_CONVERGENCE_V1.md`](backend/BACKEND_CONVERGENCE_V1.md). Prosedur migrasi tanpa mengganggu produksi korpus berada di [`backend/MIGRATION_HANDOFF_V1.md`](backend/MIGRATION_HANDOFF_V1.md); setiap bukti migrasi mengikuti [`schemas/backend-migration-receipt-v1.schema.json`](schemas/backend-migration-receipt-v1.schema.json).

Koordinasi, rekayasa backend, dan penerbitan snapshot pusat ini dilakukan oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna. Kredit penulis, penerjemah manusia, dan kontributor setiap korpus tetap dipertahankan pada edisi dan metadata komponennya masing-masing.

## Memperbarui kanon

Data mata kuliah berada di [`docs/courses.js`](docs/courses.js). Pilihan sementara tidak boleh diubah menjadi `production` atau `published` sampai korpusnya benar-benar dibekukan dalam catatan koordinasi program. Tautan publik hanya ditambahkan setelah edisi tersebut dapat dibaca kembali dari tujuan publik yang tepat.

## Lisensi

Kode situs tersedia berdasarkan [Lisensi MIT](LICENSE). Teks deskriptif dan metadata kurikulum asli pada situs ini tersedia berdasarkan [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Buku dan edisi yang ditautkan tetap menggunakan lisensi masing-masing; situs ini tidak mengganti atau menyatukan lisensi karya-karya tersebut.

---

<span lang="en">English note: This repository hosts an Indonesian-first navigation layer for an open 40-course mathematics curriculum. English is intentionally secondary.</span>
