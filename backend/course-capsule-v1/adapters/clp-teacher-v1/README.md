# Perencana tugas CLP / CLP assignment planner

## Bahasa Indonesia

Pemilih tugas untuk B20 (695 soal), B30 (596), B50 (497), dan B60 (410).
Soal dapat disaring menurut bagian sumber dan ketersediaan petunjuk atau
beberapa penyelesaian. Pilihan dapat dicetak sebagai daftar rujukan, disimpan
sebagai JSON dengan identitas dan lokasi sumber lengkap, lalu dimuat kembali.
Data dari edisi lain atau data soal yang berubah ditolak tanpa menghapus pilihan.

Ini bukan lembar soal siap cetak, terjemahan baru, atau pengganti buku. Isi buku
tidak disalin. Buku Inggris asli dan PDF Bahasa Indonesia tetap ditautkan ke
sumbernya. Nomor kelompok/lokal menunjukkan urutan struktur sumber, bukan
jaminan nomor yang tercetak pada edisi lain. Ekspor native CLP1 tetap merekam
pemetaan tingkat berkas; lapisan tambahan `clp1-navigation.json` menyediakan
rentang terjemahan dan halaman awal PDF yang telah diverifikasi untuk 695 soal,
620 petunjuk, 695 jawaban, dan 695 penyelesaian. Tiga puluh soal dari dua berkas
anak berada dalam berkas terjemahan induknya; status historis tidak ditulis ulang.
Nomor PDF bukan nomor halaman tercetak. Pemetaan ini membuktikan identitas
struktur dan rujukan baca, bukan peninjauan baru atas mutu terjemahan atau
kebenaran matematika. Tautan PDF membutuhkan jaringan. Untuk membaca luring,
unduh buku secara terpisah dan gunakan nomor PDF yang ditampilkan.
CLP3 mempertahankan dua format per soal, termasuk tiga perbedaan vektor bantuan.
CLP4 mempertahankan sebelas soal dengan dua penyelesaian. Tidak ada petunjuk
baru yang dibuat untuk mengisi ketiadaan petunjuk pada sumber.

Integrasi ini dibuat oleh OpenAI Codex — **gpt-6-astra, Ultra**. Ini bukan klaim
penulisan, penyuntingan, atau peninjauan manusia. Penulis asli CLP: Joel Feldman,
Andrew Rechnitzer, dan Elyse Yeager. Identitas hak per komponen tetap tersedia;
materi sumber berlisensi CC BY-NC-SA 4.0. Teks lisensi disertakan dalam paket
sumber. Pengungkapan model di sini berlaku untuk integrasi perencana, bukan
penggantian keterangan asal-usul terjemahan buku.

### Reproduksi luring

Dari akar arsip, jalankan perintah di bawah dengan Python 3 dan Node.js yang
sudah tersedia. Tidak memerlukan paket tambahan, jaringan, TeX, atau salinan
seluruh buku. Jangan menjalankan intake untuk reproduksi biasa: data masukan
beku sudah disertakan. Buka berkas `site/B20.teacher.html` di bawah direktori
adapter ini. Pertahankan `teacher.js` dan `teacher.css` di samping HTML.

```text
python scripts/build-clp-teacher-v1.py
python scripts/test-clp-teacher-v1.py
```

`intake-clp-teacher-v1.py` hanya untuk audit ulang terhadap arsip native dan
adapter bersama yang terikat hash. Intake memeriksa byte arsip, hash anggota,
dan identitas soal; tidak mengubah sumber. Masukan portabel tidak menyertakan
isi soal. Hash pada `input/source-lock.json` mengikat metadata dan rute baca.

Lapisan navigasi CLP1 memiliki kunci hash tersendiri dalam
`input/clp1-navigation-lock.json`. Paket menyertakan seluruh metadata,
pemetaan, kode pembangun, dan bukti validasi. Reproduksi perencana tetap
tidak memerlukan buku. Audit ulang pemetaan terhadap buku memerlukan arsip
sumber, arsip backend yang diperbaiki, serta PDF yang hash-nya tercatat di
`clp1-navigation.json`, ditambah PyMuPDF dan lxml. Gunakan
`scripts/map-clp1-navigation-v1.py --help` untuk argumen berkas; tidak ada
pengunduhan otomatis atau perubahan pada buku. Pilihan JSON lama dari
korpus CLP1 yang sama masih dapat dimuat; rujukan baru diambil dari pemetaan
terverifikasi, bukan dari nomor halaman yang tidak dipercaya dalam impor.

## English

Assignment selection for B20 (695 exercises), B30 (596), B50 (497), and B60
(410). Filter by source section, recorded hints, or multiple solutions. Print
a reference list, export exact source identities and relationships as JSON,
and import the same edition's selection without losing the source mappings.

This is not a printable worksheet, a new translation, or a substitute for the
books. It does not copy book prose. The additive CLP1 overlay binds all 695
questions and 2,010 recorded support items to exact translated source spans
and verified Indonesian PDF start pages. The original native file-level
records remain unchanged, including thirty source-child exercises translated
in their parent files. This is structural and navigation verification, not a
fresh semantic or translation-quality audit. PDF page numbers differ from
printed page numbers, and links do not assert full multi-page solution bounds.
Structural group/local numbering is not a guarantee of numbering in other
editions. CLP3 retains two formats per exercise
and their three asymmetric support vectors; CLP4 retains eleven exercises with
two solutions. Missing recorded hints remain missing.

Planner integration: OpenAI Codex — **gpt-6-astra, Ultra effort**, without a
claim of human authorship or review. Original CLP authors: Joel Feldman, Andrew
Rechnitzer and Elyse Yeager. Native component rights identities are retained;
the source material is CC BY-NC-SA 4.0. Full original license texts accompany
the editable source package. This attribution concerns the integration only,
not the authorship or original model provenance of the translated books.

Run the two commands above from the archive root. The self-contained frozen
metadata rebuilds the planner without network, TeX, third-party packages, or
producer checkouts. Normal replay does not rerun intake. For offline use open
`site/B20.teacher.en.html` beside its JavaScript and CSS. Download books
separately. No analytics, external scripts, or browser persistence are used.
The new navigation metadata and its validation lock are included in the
source package. Re-auditing against the books needs the three hash-pinned
external release files plus PyMuPDF and lxml; see the mapping script's
`--help`. Ordinary planner rebuilding needs neither library nor book files.
Old same-corpus CLP1 assignments remain importable; verified navigation is
added from the current model, never accepted from a modified import.

### Integrasi bersama / Shared integration

Di checkout program lengkap, `npm run build:clp-teacher` membangun, menguji,
mengemas dan menghubungkan pemilih ke empat peran. Jalankan pipeline program
untuk memperbarui navigasi, kartu kurikulum, dan bukti byte halaman. Pemetaan
native CLP1 tetap dipertahankan; rujukan tiap butir merupakan lapisan tambahan.
Keberhasilan build lokal bukan bukti publikasi;
status publik mengikuti bukti unduhan anonim, bukan README ini.

In the full program checkout, `npm run build:clp-teacher` builds, tests,
packages and admits all four planners. The program pipeline then refreshes
navigation, curriculum cards and hosted-page identities. CLP1 native records
stay file-level; the separate overlay carries the verified item references.
A local build does not establish publication; public status requires anonymous
download evidence rather than an assertion in this README.
