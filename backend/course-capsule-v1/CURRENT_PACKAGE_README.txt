PAKET BACKEND BERSAMA — 40 PERAN KURIKULUM

Paket ini menyimpan versi kerja lapisan integrasi: identitas sumber, metadata
terjemahan, peta belajar, hubungan latihan dan solusi, alat peserta belajar,
bahan pengajar, kode adaptor, serta bukti dan pemeriksaan yang menyertainya.
Paket ini bukan pernyataan bahwa semua kemampuan backend telah selesai.
Status dan batas setiap kemampuan tetap tercatat pada masing-masing kursus.

Tambahan D60: buka /backend/d60/native-ledger/ledger.html untuk menelusuri
istilah, segmen, koreksi dan hak penggunaan yang terhubung ke unit belajar.
Sebelas aliran metadata asli mempertahankan 8.338 rekaman. Label penelusuran
pada unit induk tidak menyatakan bahwa setiap pilihan berlaku pada semua
paragraf turunannya. Sebanyak 73 identitas berkas sasaran berbeda tetap
ditampilkan sebagai temuan; bukan klaim bahwa 73 paragraf salah. Antarmuka
Inggris tersedia pada ledger-en.html; tautan isi buku masih berbahasa Indonesia.
Implementasi asli adaptor D60: OpenAI Codex — gpt-6.1-sol, tingkat upaya Ultra.
Perbaikan integrasi, pengujian dan pengemasan lanjutan: OpenAI Codex —
gpt-6-astra, tingkat upaya Ultra. Ini bukan peninjauan kanon oleh manusia.

Kode pengemasan, perbaikan pemeriksaan identitas, dan panduan paket ini dibuat
oleh OpenAI Codex — gpt-6-astra, Ultra effort. Atribusi ini hanya mencakup
pekerjaan integrasi tersebut; bukan pengakuan kepengarangan, penerjemahan,
penyuntingan manusia, atau peninjauan ahli atas buku yang dirujuk.

Peta lintas program menghubungkan 40 mata kuliah fondasi dengan 71 mata kuliah
lanjutan dan 951 pelajaran dalam edisi publik yang dibekukan. Buka /id/programme/
atau /en/programme/. Sebanyak 183 hubungan belajar menghubungkan mata kuliah
lanjutan ke fondasi; peta ini tidak menyatakan semua pembuktian prasyarat telah
diperiksa. Proyeksi lokal phone berisi 58 mata kuliah/900 unit merupakan
snapshot berbeda dan tidak boleh dijumlahkan sebagai materi tambahan.
Peta, data masukan beku dan pembuatnya disertakan; isi pelajaran lanjutan tetap
di repositori asal. Integrasi lintas program asli: OpenAI Codex — gpt-6.1-sol,
tingkat upaya Ultra. Penggabungan dengan alat D60 dan pengujian paket terkini:
OpenAI Codex — gpt-6-astra, tingkat upaya Ultra.

Isi buku tetap berada dalam repositori dan arsip publik asalnya. Paket ini tidak
menyalin seluruh korpus buku, tidak menjamin semua buku tersedia luring, dan tidak
mengaku telah membangun ulang sumber asli semua penerbit. Untuk membaca buku
yang ditautkan, gunakan koneksi internet atau unduh edisinya terlebih dahulu.
Pembaca D50 yang disertakan masih memakai MathJax dari CDN untuk menampilkan
rumus; bagian itu memerlukan jaringan. Daftar dependensi jaringan dicatat
secara eksplisit pada runtime_boundary dalam manifest paket.

Mulai: jalankan `python -m http.server 8000 --directory docs`, lalu buka
http://localhost:8000/backend/ pada peramban. Layanan lokal diperlukan bagi
alat yang mengambil data JSON; membuka berkas HTML langsung dapat dibatasi
oleh kebijakan peramban. Tautan di luar paket tetap mengacu ke program daring.

Pemutaran ulang kapsul: gunakan Node.js 22 dan Python 3.10+ dengan jsonschema.
Lingkungan yang diuji: Node.js 22.17.0, Python 3.13.9, jsonschema 4.26.0,
dan zlib 1.3.1. Kebutuhan Python dicatat pada
scripts/current-backend-requirements-v1.txt. Pembuatan ulang ZIP dengan versi
kompresor berbeda dapat menghasilkan byte ZIP berbeda meski isinya identik.
Jalankan, dari akar hasil ekstraksi:
  node scripts/build-course-capsules-v1.mjs --output-root=replay/a
  node scripts/build-course-capsules-v1.mjs --output-root=replay/b
  node scripts/validate-course-capsules-v1.mjs --output-root=replay/a --peer-output-root=replay/b
  node scripts/test-course-capsule-ui-v1.mjs
  node scripts/test-local-evidence-identities-v1.mjs
  node scripts/build-cross-programme-integration-v1.mjs --check
  node scripts/test-cross-programme-current-v1.mjs

Pemeriksaan peramban D60 memakai Playwright dan satu peramban Chromium tanpa
jendela. Jalankan `node scripts/test-d60-native-browser-v1.cjs` setelah memasang
Playwright dan perambannya di lingkungan Anda. Bila memakai instalasi yang
sudah ada, PLAYWRIGHT_MODULE_PATH menunjuk modul Playwright dan
PLAYWRIGHT_BROWSER_PATH menunjuk program peramban. Keduanya bersifat opsional;
tidak ada direktori pribadi pembuat yang diperlukan. Pemeriksaan hanya memakai
server lokal sementara dan memblokir permintaan jaringan eksternal.

CURRENT_BACKEND_PACKAGE_MANIFEST.json mencatat setiap berkas, ukuran, SHA-256,
alasan penyertaan, dan bukti lokal untuk setiap peran. Pemutaran ulang ini
menguji kapsul dan antarmuka bersama; bukan audit baru atas mutu terjemahan,
penggunaan kanon, atau aksesibilitas seluruh buku.

Panduan peserta belajar dua bahasa bersumber pada docs/guides/start-v0.63.32.tex.
Sumber itu lengkap dalam satu berkas dan memakai paket standar LaTeX:
inputenc, fontenc, geometry, lmodern, xcolor, enumitem, dan hyperref.
Pada Windows, jalankan scripts/build-learner-guide-v06332.ps1 untuk dua lintasan
pdfLaTeX dengan mutex TeX bersama. Hasil masuk ke work/learner-guide-v06332.
Di lingkungan terpisah, dua lintasan `pdflatex -halt-on-error -no-shell-escape
docs/guides/start-v0.63.32.tex` membangun dokumen yang sama. Versi distribusi TeX
dan font dapat memengaruhi byte PDF; identitas rilis dicatat terpisah.

Panduan Inggris tambahan / additional English guide:
This is the current shared integration snapshot, not the complete book corpus
or a declaration that all backend work is finished. Serve the docs directory
with a local HTTP server and open /backend/. Book links still need internet or
separately downloaded editions. The commands above reproduce and validate the
forty common capsules. Individual native-source rebuilds may require separately
pinned upstream inputs. The manifest preserves those distinctions.
The complete bilingual learner-guide LaTeX is docs/guides/start-v0.63.32.tex.
Build it with two pdfLaTeX passes and the standard packages listed above; the
Windows build script also respects the machine-wide TeX mutex.

D60 adds a native metadata explorer with exact study-unit links, term choices,
segments, correction history and rights records. The English interface does
not turn its Indonesian reader links into an English edition. Browser QA uses
Playwright with optional PLAYWRIGHT_MODULE_PATH and PLAYWRIGHT_BROWSER_PATH;
it runs headlessly against a temporary local server with outside requests
blocked. Original D60 adapter: OpenAI Codex — gpt-6.1-sol, Ultra effort.
Subsequent integration repairs, QA and packaging: OpenAI Codex — gpt-6-astra,
Ultra effort. No human canon review or whole-book rebuild is claimed.

The included /en/programme/ and /id/programme/ outlines preserve the upstream
links between forty core courses and the frozen public edition of 71 advanced
courses/951 lessons. All six current online/offline curriculum pages retain
these routes alongside the D60 native-record tools. The 183 preparation-course
links are not proof-dependency certification. The separate local phone snapshot
has 58 courses/900 units and is not an additional, additive corpus count.
Original cross-programme integration: OpenAI Codex — gpt-6.1-sol, Ultra effort.
Combined-current integration and package QA: OpenAI Codex — gpt-6-astra, Ultra effort.
