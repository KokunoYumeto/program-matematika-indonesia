# D110 · Pemilih belajar dan mengajar

Paket ini menyediakan pemilih belajar dan mengajar untuk D110 dan menggunakan
hasil kerja backend Mathematics in Lean
yang sudah ada. Buku maupun kode Lean tidak diterjemahkan ulang atau dijalankan.

Tersedia antarmuka Bahasa Indonesia dan English, daftar 13 bab / 43 bagian,
pencarian 2.177 unit asli, pilihan latihan dan ekspor rencana dengan relasi
solusi. Semua 330 cuplikan solusi/deklarasi pendukung tersedia dalam kedua
bahasa dan cocok dengan hash teks yang dicatat sumber. Dua catatan pendamping
tanpa latihan tidak dihitung sebagai solusi. Jumlah unit bertanda latihan 243,
bukan hanya 239 unit berjenis exercise. Enam unit bertanda latihan tidak
mempunyai relasi solusi tercatat. Solusi untuk satu lubang bukti, alternatif,
dan solusi demonstrasi bukan jumlah latihan tambahan.

Tautan pembaca menunjuk konteks bab/bagian yang diperiksa. Pembaca Inggris
memakai revisi berbeda; tidak dinyatakan sama untuk setiap deklarasi kode.
Nomor baris asli tidak dipakai sebagai nomor baris terjemahan. Cuplikan solusi
menggunakan proyeksi sumber yang sebenarnya, termasuk indentasi dan penanda
yang ikut dalam hash. Tidak ada bukti baru yang dibuat.

## Membangun ulang

Dari akar paket sumber, dengan Python 3 dan Node.js yang sudah tersedia:

```text
python -B scripts/build-d110-surface-v1.py
python -B scripts/test-d110-surface-v1.py
node scripts/d110-surface/test-d110-ui.mjs
python -B scripts/package-d110-surface-v1.py
python -B scripts/build-d110-hosted-v1.py
```

Hasil berada dalam direktori `portable` di samping berkas ini. Buka
`index.html` atau `teacher.html`; versi Inggris menggunakan `.en.html`.
Pembangunan ulang dari saksi yang dipatok tidak memakai jaringan, checkout
produsen, TeX, atau Lean. Pembaca buku daring tetap memerlukan jaringan.
Paket ini bukan seluruh buku atau lingkungan Lean luring.
Langkah terakhir menyiapkan `docs/backend/d110/`; lapisan navigasi program
ditambahkan oleh pembangun program bersama. Catatan pemeriksaan lokal tidak
sendiri membuktikan bahwa berkas telah diterbitkan.

Kode buku berlisensi Apache-2.0 dan teks bukunya CC BY 4.0; identitas hak
komponen disimpan dalam `input/rights.jsonl`. Sumber antarmuka, pembangun,
pengujian, metadata dan saksi semuanya disertakan. Implementasi antarmuka dan
pemetaan ini dibuat oleh OpenAI Codex — GPT-6 Astra, Ultra effort.
Pernyataan ini mengatribusikan kode integrasi, bukan penerjemahan buku asli.
Teks lisensi lengkap disertakan dalam `input/LICENSE-APACHE-2.0.txt` dan
`input/LICENSE-CC-BY-4.0.txt` serta disalin ke hasil `portable`.
Pernyataan ini bukan pengakuan pemeriksaan manusia atau publikasi selesai.

## English

This is a source-preserving D110 study/teaching selector, not a newly
translated book, everyday-English edition, or Lean runtime. Use the commands
above to rebuild the four pages and their data from bundled witnesses. The
source package reproduces all generated files offline; reading the complete
linked books still requires a network connection.

Native identities, original records, proof-hole distinctions, alternative
solutions, support edges, code hashes and six absent solution relations remain
explicit. All 330 solution/support excerpts reproduce their recorded English
and Indonesian hashes. The English reading context is separately versioned;
chapter alignment does not establish declaration-level equivalence. The two
no-exercise companion records are not extra solutions. Original component
rights remain separate. The final command stages `docs/backend/d110/`; the
shared programme builder then adds reversible navigation. Local validation
receipts alone do not establish public deployment.

Integration code and mapping produced by OpenAI Codex — GPT-6 Astra, Ultra
effort. This attribution does not claim the original book translation or
human review. Full original component licence texts are bundled with the
input and portable files.
