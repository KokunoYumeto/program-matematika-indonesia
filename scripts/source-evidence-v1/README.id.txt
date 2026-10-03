PENELUSURAN SUMBER DAN HASIL — PANDUAN REPRODUKSI

Alat ini membuka rekaman penggunaan sumber yang sudah ada dalam dua arah:
hasil ke sumber dan sumber ke hasil. Identitas asli, syarat lengkap, peran
penggunaan sumber, atribusi manusia dan pengamatan revisi dipertahankan.
Alat tidak membuat tag global atau daftar pustaka pengganti. Tidak ada klaim
tinjauan manusia atau pemeriksaan matematis baru.

Buka docs/id/source-evidence.html di peramban, lalu pilih projection.json.
Berkas yang dipilih tidak diunggah dan tidak disimpan dalam penyimpanan
peramban. Antarmuka berfungsi secara luring. Pilihan bahasa tidak mengubah
bahasa isi bukti asli. Rekaman bukan sensus langsung keadaan mata kuliah.

Daftar sources.jsonl bersama dapat dibuka secara opsional. Kunci hanya
dicocokkan melalui hash berkas eksak yang telah dinyatakan dalam daftar itu.
Kecocokan ganda tetap ambigu; kunci, tanggal akses, izin dan konsultasi sumber
yang tidak diketahui tidak dikarang. Pernyataan yang dikutip tanpa bukti
tidak dinyatakan sebagai bukti yang sudah tersedia.

Reproduksi HTML dari sumber (Node.js, tanpa paket tambahan):
  node scripts/build-source-evidence-explorer.mjs
Periksa hasil tanpa menulis ulang:
  node scripts/build-source-evidence-explorer.mjs --check
Buat/periksa ZIP sumber (Python 3.9+):
  python -B scripts/package-source-evidence-explorer.py
  python -B scripts/package-source-evidence-explorer.py --check

Untuk memproyeksikan masukan bukti yang dipilih secara eksplisit:
  python -B scripts/source-evidence-v1/project_evidence.py inputs.json --output keluaran-privat
  python -B scripts/source-evidence-v1/project_evidence.py inputs.json --output keluaran-privat --check
  python -B scripts/source-evidence-v1/project_evidence.py inputs.json --result ID-HASIL
  python -B scripts/source-evidence-v1/project_evidence.py inputs.json --source HASH-SHA256

freeze_inputs.py dapat membuat rekaman baru dari direktori inti dan lanjutan
yang ditentukan secara eksplisit. Ia menolak menimpa rekaman lama. Pertahankan
pasangan masukan dan validasi yang sesuai. Jangan menaruh masukan privat dalam
docs, public atau arsip rilis. ZIP alat ini tidak berisi rekaman privat.

Uji peramban tambahan memakai Playwright yang sudah tersedia, ditunjuk melalui
OPEN_COURSES_NODE_MODULES, dan berkas proyeksi contoh yang diberikan sebagai
argumen ke scripts/test-source-evidence-explorer.mjs. Uji tersebut memeriksa
perangkat lunak dan rujukan, bukan kebenaran bukti matematis.

Antarmuka dan integrasi diproduksi oleh OpenAI Codex — GPT-6 Astra, tingkat
upaya Ultra. Adaptor Python mempertahankan atribusi produksinya sendiri.
Paket ini berisi perangkat lunak, bukan buku matematika baru atau edisi PDF.
