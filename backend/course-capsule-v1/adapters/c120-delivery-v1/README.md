# C120 — pemeriksaan pembaca daring

Paket ini menghubungkan bukti pembaca asli **Pemodelan Matematika dan Dinamika
Nonlinear** ke katalog program. Buku tetap berada dalam repositori aslinya;
paket ini tidak menyalin atau menerjemahkan ulang isi buku.

## Lingkup yang diperiksa

- 26 unit, 27 halaman HTML, 667 tautan internal dan 51 gambar.
- 6.283 elemen MathML dengan anotasi TeX; CSS cetak pada 26 unit.
- 253 berkas publik, termasuk PDF lengkap, dengan ukuran dan SHA-256.
- Commit sumber `cf1f7b2d7374818d2f0f48c899addc7c83db3083`.
- Isi elemen `main` pada seluruh halaman sama dengan saksi lokal yang dipakai
  adapter. Perubahan navigasi pada 27 halaman dan pembaruan 26 manifest paket
  direproduksi menurut skrip deployment asli yang dipertahankan di `deployment/`.

Ini bukan sertifikasi WCAG, audit ulang mutu terjemahan, pemeriksaan visual
setiap halaman PDF, atau bukti adanya EPUB maupun paket pembaca HTML luring.
Tautan sumber berbahasa Inggris tidak dianggap sebagai pembaca bahasa Inggris
yang sudah terintegrasi. Ketersediaan versi Inggris empat unit jembatan masih
perlu diperiksa terpisah.

## Validasi dan pengulangan

Dari akar repositori program, jalankan:

```text
node scripts/test-c120-delivery-evidence-v1.mjs
```

Perintah tersebut memeriksa ikatan bukti dan penerimaan dalam katalog, termasuk
kasus negatif. Ia tidak mengunduh ulang buku atau mengklaim pengamatan publik
baru. `deployed-readback.json` mencatat waktu pengamatan aslinya.

Untuk audit daring baru, sediakan repositori asli sebagai direktori sejajar
`mathematical-modeling-nonlinear-dynamics-id`, dengan lingkup berkas yang dicatat
di `input-manifest.json`. Gunakan Python dengan `beautifulsoup4` dan `requests`:

```text
python -B scripts/test-c120-delivery-v1.py
python -B scripts/audit-c120-delivery-v1.py --deployed
```

Audit daring hanya membaca berkas asli, menulis bukti baru di direktori adapter
ini, dan membuat permintaan jaringan secara berurutan. Receipt percobaan lama
tidak diperlukan. Bila edisi atau lingkup berubah, selidiki perubahan itu sebelum
memperbarui batas pemeriksaan; jangan menimpa bukti historis untuk membuat tes lolos.

Integrasi, perangkat pemeriksaan dan catatan ini dibuat dengan OpenAI Codex —
gpt-6-astra, Ultra effort. Keterangan ini tidak menggantikan atribusi penulis dan
penerjemah buku pada edisi aslinya.
