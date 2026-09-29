# Perencana tugas OpenLogic — C80

Antarmuka Bahasa Indonesia dan English memilih rujukan ke buku **Bahasa
Indonesia**, bukan menerjemahkan ulang buku atau menyalin soal ke lembar baru.
Ada 442 kemunculan tercetak dari 427 soal sumber berbeda: 411 dalam buku utama
dan 31 dalam suplemen. Lima belas kemunculan tambahan memakai kembali sumber
dalam konteks pembaca berbeda. Sepuluh soal dinonaktifkan oleh tag edisi dan
satu soal tidak tercetak akibat pemicu pencetakan tertunda yang hilang.
Kesebelas soal itu tetap dicatat, tanpa tautan PDF yang dibuat-buat.

Jawaban, petunjuk, dan penyelesaian belum diaudit. Pemetaan ini membuktikan
hubungan struktural, bukan mutu terjemahan atau kebenaran matematis. Judul
bagian berasal dari penanda navigasi PDF yang dihubungkan melalui identitas
tujuan persis, bukan perluasan makro LaTeX yang ditebak.

## Bangun dan gunakan

Dari akar hasil ekstraksi, jalankan Python 3 (hanya pustaka standar):

    python -B scripts/build-openlogic-teacher-v1.py
    python -B scripts/test-openlogic-teacher-build-v1.py

Uji fungsi antarmuka memerlukan Node.js:

    node scripts/test-openlogic-teacher-ui-v1.mjs

Buka `backend/course-capsule-v1/adapters/openlogic-teacher-v1/site/C80.teacher.html`
atau `C80.teacher.en.html`. Tabel rujukan tetap dapat dibaca tanpa JavaScript.
Pilihan disimpan dengan ekspor JSON; tidak ada penyimpanan persisten, analitik,
atau permintaan jaringan latar belakang. Impor menolak edisi atau rujukan yang
berubah, urutan yang berubah, identitas tidak dikenal, dan duplikat.

Untuk membaca luring, unduh PDF gabungan yang ditautkan pada halaman, simpan
sebagai `reader.pdf` di samping HTML, dan aktifkan tautan lokal. Nomor halaman
adalah nomor fisik PDF. Badan buku tidak disertakan dalam paket perencana.
Tautan program dan unduhan daring tetap memerlukan koneksi.

## Asal bukti

Empat JSON masukan dibekukan menurut ukuran dan SHA-256 di pembangun.
`mapping-tests.json` mencatat dua pemutaran ulang identik atas sumber dan PDF.
Paket ini mereproduksi perencana dari hasil pemetaan beku; ia **tidak** mengklaim
mereproduksi pemetaan sumber/PDF tanpa arsip buku asli. Skrip verifikasi penuh
dan identitas arsip terdapat dalam repositori program. Arsip buku tetap pada
jalur rilis `KokunoYumeto/OpenLogic-id`, tag `id-olp-0722-20260814`.

Integrasi perencana dan pemetaan: OpenAI Codex — gpt-6-astra, tingkat upaya Ultra.
Tidak ada klaim terjemahan buku baru atau peninjauan manusia. Buku Open Logic
Project dan edisi Bahasa Indonesia berlisensi CC BY 4.0; rilis buku memuat
teks lisensi dan sumbernya. Catatan ini tidak mengganti atribusi buku.

## English

Both interfaces select references into the Indonesian reader. The planner
accounts for all 438 source exercises: 427 rendered sources, ten disabled by
edition tags, one absent because a deferred-printing hook was not triggered.
There are 442 selectable occurrences because fifteen sources are reused.
Answers, hints and solutions remain unaudited. No missing PDF location is
invented. Section titles come from exact PDF bookmark destinations.

Run the commands above from the extracted source root; open either HTML file.
The source ZIP rebuilds the planner offline from its frozen evidence inputs,
not the entire source/PDF mapping audit. Download the separately linked book as
`reader.pdf` for local page links. Export JSON to save a selection; no analytics,
background network requests or persistent browser storage are used. Import
checks the full edition binding, every reference and canonical record order.
The complete static reference table remains readable without JavaScript.

Planner/mapping integration: OpenAI Codex — gpt-6-astra, Ultra effort. No new
book translation or human review is claimed.
