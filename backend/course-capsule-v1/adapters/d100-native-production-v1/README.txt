BUKTI PRODUKSI HTML D100

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

Ekspor data backend asli dan produksi PDF memerlukan pembuktian terpisah.
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

Six isolated HTML builds reproduce all three Indonesian native readers exactly:
60 source units plus 32 editorial companion units. Twenty-eight omitted runtime
dependencies are explicitly hash-bound. This is HTML reproduction evidence,
not native-data-export, fresh PDF, semantic terminology or whole-backend closure.
The tools require the matching native source tree; it is not bundled here.
Integration/audit: OpenAI Codex gpt-6-astra, Ultra. Native text provenance:
OpenAI Codex gpt-5.6-sol, Ultra. No new human review is claimed.
