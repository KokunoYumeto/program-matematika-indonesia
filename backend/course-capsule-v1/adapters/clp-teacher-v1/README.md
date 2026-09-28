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
jaminan nomor yang tercetak. CLP1 memetakan tiap soal sumber hanya ke **berkas**
terjemahan. Jangan menganggapnya sebagai pemetaan tiap soal Bahasa Indonesia.
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

## English

Assignment selection for B20 (695 exercises), B30 (596), B50 (497), and B60
(410). Filter by source section, recorded hints, or multiple solutions. Print
a reference list, export exact source identities and relationships as JSON,
and import the same edition's selection without losing the source mappings.

This is not a printable worksheet, a new translation, or a substitute for the
books. It does not copy book prose or claim PDF pages or HTML exercise anchors.
CLP1 has translated-file alignment only. Structural group/local numbering is
not a guarantee of printed numbering. CLP3 retains two formats per exercise
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

### Integrasi bersama / Shared integration

Di checkout program lengkap, `npm run build:clp-teacher` membangun, menguji,
mengemas dan menghubungkan pemilih ke empat peran. Jalankan pipeline program
untuk memperbarui navigasi, kartu kurikulum, dan bukti byte halaman. Pemetaan
CLP1 tetap pada tingkat berkas. Keberhasilan build lokal bukan bukti publikasi;
status publik mengikuti bukti unduhan anonim, bukan README ini.

In the full program checkout, `npm run build:clp-teacher` builds, tests,
packages and admits all four planners. The program pipeline then refreshes
navigation, curriculum cards and hosted-page identities. CLP1 stays file-level.
A local build does not establish publication; public status requires anonymous
download evidence rather than an assertion in this README.
