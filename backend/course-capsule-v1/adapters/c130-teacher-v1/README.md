# Perencana rujukan C130

Perencana ini menghubungkan latihan, cek pemahaman, jawaban, kegiatan visual,
manual pengajar, dan rujukan praktikum pada edisi Bahasa Indonesia Buku 1 R017.
Antarmuka Bahasa Indonesia dan English membuka buku Bahasa Indonesia yang sama.
Ini bukan terjemahan buku ke bahasa Inggris atau sertifikasi kebenaran matematika.

## Menjalankan dan membangun ulang

Buka `site/C130.teacher.html` secara langsung di peramban. Halaman tidak perlu
peladen, pelacakan, atau penyimpanan akun. Ekstrak paket sumber dan jalankan
`python -B scripts/build-c130-teacher-v1.py` dari akar hasil ekstraksi untuk
menghasilkan halaman yang identik, termasuk paket sumber yang identik.
Pembuat halaman hanya memakai pustaka standar Python.

Unduh buku secara terpisah melalui tautan pada halaman. Untuk rujukan luring,
simpan PDF sebagai `reader.pdf` di samping halaman, lalu aktifkan pilihan lokal.
Paket praktikum dan visualisasi eksternal tidak dimasukkan ke paket perencana.

## Pemeriksaan penuh terhadap sumber

Identitas empat berkas sumber, backend, praktikum dan PDF tercatat di
`mapping.json` pada bagian `inputs`. Unduh URL tersebut ke sebuah direktori
cache; nama, jumlah byte dan SHA-256 harus sama persis. Pemeriksaan penuh
memerlukan Python dengan PyMuPDF (`fitz`), serta Node.js untuk uji antarmuka:

```
python -B scripts/test-c130-teacher-v1.py --cache /path/to/cache
node scripts/test-c130-teacher-ui-v1.cjs
```

Pemetaan menyimpan semua 530 rentang sumber individual asli. Ada 203 latihan
pembaca, termasuk 13 butir graf yang belum memiliki ID individual dalam ekspor
backend asli. ID tambahan memakai ruang nama tersendiri. Ada pula 12 cek
pemahaman beserta jawaban dan 12 kegiatan visual. Nomor cek pemahaman berasal
dari PDF, bukan nomor urut rekaan. Batas 192 bahan manual dipetakan dan di-hash
terpisah dari header asli; header bukan keseluruhan isi jawaban.

Sebanyak 104 dari 132 penyelesaian lain memiliki rujukan bagian teks yang cocok
secara unik. Dua belas lainnya kini mempunyai tautan awal penyelesaian yang
menggabungkan rujukan sumber tepat, relasi asli, dan judul tercetak yang unik;
Empat belas penyelesaian lagi dipetakan melalui beberapa potongan teks yang
semuanya cocok pada satu halaman dalam urutan sumber; dua penyelesaian pendek
dipetakan melalui judul contoh yang tepat dan awal penyelesaian yang bersebelahan.
Semua 132 kini mempunyai rujukan halaman. Rumus di antara potongan teks tidak
diverifikasi oleh metode pencocokan ini. Empat latihan cabang sumber lama
tidak tercetak di PDF ini. Keadaan ini dicatat, bukan dihapus. Tautan bagian
teks atau halaman awal tidak menyatakan bahwa keseluruhan penyelesaian berada
di satu halaman.

Perencana bukan bukti bahwa seluruh kemampuan asli C130 atau seluruh program
40 peran sudah terintegrasi. Hasil komputasi praktikum dan situs visualisasi
eksternal belum dijalankan ulang. Materi buku tetap berada dalam garis versi
aslinya; paket ini berisi kode integrasi, metadata dan bukti rujukan, bukan buku.

Pemetaan dan kode integrasi: OpenAI Codex — gpt-6-astra, Ultra effort.
Atribusi, model penerjemah dan lisensi buku tetap mengikuti edisi aslinya.
