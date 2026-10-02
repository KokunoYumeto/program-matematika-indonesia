BUKTI PRODUKSI HTML D100

TAMBAHAN EKSPOR DATA BGK

bgk-backend-replay.json membuktikan dua ekspor terisolasi: 21.690 rekaman dan
19 berkas identik dari 727 masukan. Pemeriksa native memproyeksikan ulang 99
berkas Markdown, memeriksa penutupan 90 berkas sumber utama, mempertahankan
21.686 ID historis dan empat ID tambahan, serta membedakan 495 latihan dari
25 solusi sumber. Seluruh 19 berkas registri historis diperiksa. Pembaca HTML,
PDF dan bukti QA yang sudah ada merupakan dependensi eksplisit; tidak ada
PDF baru yang dibangun. Keluaran backend terkoreksi dilarang sebagai masukan.

Gunakan scripts/replay-d100-bgk-backend-v1.py dengan operasi replay,
--binding backend/course-capsule-v1/authority/d100-bgk-export-inputs-v1.json,
--native-root untuk sumber identik, dan --output untuk direktori baru di work/.
scripts/bind-d100-bgk-export-v1.py memeriksa ulang seluruh masukan/keluaran
aktual. Ketiga ekspor data terkoreksi Bahasa Indonesia kini terbukti; bukti
ini tidak meliputi pembangunan ulang edisi Inggris, PDF baru atau telaah semantik.

TAMBAHAN EKSPOR DATA KLASIK

classical-backend-replay.json membuktikan dua ekspor terisolasi: 23.869 rekaman
dan 19 berkas identik, dari 129 masukan terikat. Pemeriksa native memproyeksikan
ulang 120 berkas sumber untuk 30 unit, termasuk 8.056 segmen, 276 catatan istilah
dan 159 koreksi. Semua 22.752 ID historis dipertahankan. Tiga berkas registri
historis menyediakan ID, skema dan metadata warisan; dependensi ini dinyatakan,
bukan disembunyikan sebagai pembangunan hanya dari Markdown. Keluaran backend
terkoreksi dilarang sebagai masukan. Tidak ada berkas produsen yang diubah.

Gunakan scripts/replay-d100-classical-backend-v1.py dengan operasi replay,
--binding backend/course-capsule-v1/authority/d100-classical-export-inputs-v1.json,
--native-root untuk sumber asli yang identik, dan --output untuk direktori baru
di work/. scripts/bind-d100-classical-export-v1.py memeriksa ulang semua masukan
dan keluaran aktual sebelum mengakui bukti. Ekspor BGK dibuktikan terpisah di
atas; PDF baru dan telaah semantik tetap belum dibuktikan di sini.

TAMBAHAN EKSPOR DATA PENDAMPING

original-backend-replay.json kini membuktikan dua ekspor terisolasi dari 213
masukan yang diikat di authority/d100-original-export-inputs-v1.json. Semua
23 berkas dan 1.064 rekaman identik dengan backend asli. Pemeriksa native
merekonstruksi 3.790 rentang formula, tautan, hak, 44 solusi penguasaan baru
dan 13 rujukan solusi sumber. Masukan tidak mencakup keluaran backend yang
sedang direproduksi; proses menolak jaringan, TeX dan perubahan berkas asli.
Ekspor klasik dan BGK dibuktikan terpisah di atas; PDF baru belum dibuktikan.
Tidak ada peninjauan semantik baru atau peningkatan status paritas penuh.

Pemutaran ulang data memakai scripts/replay-d100-original-backend-v1.py dengan
operasi replay, --binding menunjuk kontrak masukan di atas, --native-root
menunjuk sumber asli dengan identitas yang sama, dan --output menunjuk direktori
baru di work/. Python memerlukan PyYAML dan jsonschema. Skrip bind pada alat
yang sama hanya untuk membekukan dependensi dari sumber asli; jangan menimpa
kontrak yang sudah dibekukan. scripts/bind-d100-original-export-v1.py memeriksa
ulang berkas hasil nyata sebelum mengakui bukti di repositori bersama.

Ketiga pembaca Bahasa Indonesia berhasil dibangun ulang, masing-masing dalam
dua direktori terisolasi. Hasilnya identik byte demi byte dengan pembaca asli:
30 unit aljabar geometri klasik, 30 unit bundel/berkas/kohomologi, dan 32 unit
pendamping editorial. Pendamping bukan tambahan 32 unit teks sumber.

HTML_REPLAY.json mengikat ketiga bukti pembangunan. Pemeriksaan pusat menolak
perubahan identitas, hasil yang hilang, jumlah unit yang salah, tautan rusak,
atau klaim PDF/backend/kanon yang tidak dibuktikan oleh pembangunan HTML ini.
Tidak ada berkas pembuat buku atau teks terjemahan yang ditimpa.

Temuan portabilitas: daftar masukan historis melewatkan 28 dependensi runtime:
enam metadata aset klasik; dua berkas BGK, termasuk sumber LaTeX untuk kontrak
serialisasi matematika; dan 20 berkas profil/kode/bukti pendamping. Tambahan
identitas di authority/d100-*-runtime-supplement-*.json diperoleh belakangan;
bukti ini tidak mengklaim bahwa daftar historis sudah lengkap sejak awal.
Untuk BGK gunakan v2; v1 adalah tahap penemuan yang belum lengkap.

Ekspor data ketiga bagian dibuktikan terpisah di atas; PDF baru belum terbukti.
Ini bukan peninjauan semantik baru terhadap istilah/kanon atau sertifikasi WCAG.
Status paritas penuh D100 dan penyelesaian seluruh program tidak dinaikkan.

Alat pada checkout repositori integrasi: scripts/replay-d100-classical-html-v1.py
dan scripts/replay-d100-native-html-v1.py. Jalankan dari akar integrasi, dengan
Pandoc 3.9.0.2 dan --native-root menunjuk salinan sumber asli yang cocok dengan
identitas bukti. --output-root wajib menunjuk direktori baru di work/.
Alat kedua menerima --lane bgk atau --lane original. Python memakai -B.
Alat tidak mengunduh masukan, menjalankan TeX, atau mengganti keluaran asli.
Paket backend bersama menyimpan bukti dan pemeriksa bukti; alat audit native
tersedia terpisah pada repositori. Seluruh korpus asli tidak disalin ke sini.

Audit/integrasi: OpenAI Codex gpt-6-astra, Ultra.
Pengerjaan teks asli yang tercatat: OpenAI Codex gpt-5.6-sol, Ultra.
Tidak ada peninjauan manusia baru yang diklaim.

ENGLISH

BGK now reproduces 21,690 records and 19 outputs twice from 727 isolated inputs.
Its independent validator reparses 99 Markdown files, checks the 90-file source
closure and preserves 21,686 historical IDs plus four additions. All 495
exercises and 25 supplied solutions remain distinct. The complete 19-file
historical registry and existing HTML/PDF/QA bytes are explicit dependencies;
this is not a new PDF build. All three corrected Indonesian data exports are
now reproduced; English-edition replay and semantic review are not established.

The classical data export now also reproduces 23,869 records in 19 files twice,
from 129 bound inputs. All 120 current source files are independently reprojected.
The three-file historical ID/schema/inherited-metadata registry is an explicit
dependency; the current corrected export is forbidden as input. All 22,752
historical IDs survive. This is not new semantic review or fresh PDF production.

Separate companion-data evidence now reproduces all 23 export files and 1,064
records twice from 213 isolated inputs, without using the existing export as
an input. Formula/link/source/rights reconstruction passes. BGK is proved
separately above; fresh PDF production and semantic review remain unproved.

Six isolated HTML builds reproduce all three Indonesian native readers exactly:
60 source units plus 32 editorial companion units. Twenty-eight omitted runtime
dependencies are explicitly hash-bound. This is HTML reproduction evidence,
not native-data-export, fresh PDF, semantic terminology or whole-backend closure.
The tools require the matching native source tree; it is not bundled here.
Integration/audit: OpenAI Codex gpt-6-astra, Ultra. Native text provenance:
OpenAI Codex gpt-5.6-sol, Ultra. No new human review is claimed.
