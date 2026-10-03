ALAT FORMAT MATA KULIAH LURING - VERSI 1

Alat ini menghubungkan edisi PDF/LaTeX/ZIP/EPUB yang sudah memiliki ikatan
sumber dengan direktori bacaan luring yang mudah digunakan. Alat ini tidak
menerjemahkan mata kuliah, membuat EPUB, mengompilasi LaTeX, menjalankan kode
dari arsip sumber, menghubungi server, atau menerbitkan bahan. Struktur sumber
asli dan bita berkas edisi dipertahankan tanpa perubahan.

OpenAI Codex - GPT-6 Astra, upaya Ultra: pemeriksaan paket, navigasi luring,
pengujian, dan dokumentasi. Kepengarangan, lisensi komponen, serta asal-usul
pekerjaan AI tetap mengikuti mata kuliah asal. Lisensi perangkat lunak: MIT;
teks aslinya disertakan dalam LICENSE.

KEBUTUHAN
Python 3.11 atau lebih baru dengan pypdf dan lxml. Pengujian memakai pypdf
6.12.2 dan lxml 6.1.1. Pemeriksaan peramban opsional memerlukan Node.js,
Playwright, dan Chromium. Alat tidak mengunduh isi mata kuliah. Pasang
dependensi secara terpisah bila diperlukan.

PENGGUNAAN DARI ARSIP ALAT YANG SUDAH DIEKSTRAK
python -B scripts/course-formats-v1/course_formats.py PAKET_LOKAL --reader DIREKTORI_BACA_BARU --report CATATAN_PRIVAT_BARU.json

PAKET_LOKAL harus memuat HANDOFF.json dengan skema
programme-course-format-handoff/1 atau /2 beserta catatan ekspor, manifes,
indeks lokasi, bukti, sumber asli, dan keempat berkas format yang dirujuknya.
Manifes sumber memakai course-format-source/2. Inventaris ZIP sumber memakai
course-editable-source-closure/1. Skema indeks lokasi yang didukung ialah
native-course-format-entry-locators/1 dan course-format-locator-index/1.
Format sumber lain memerlukan adaptor tersendiri; jangan sekadar mengganti
label berkas. Katalog unduhan mata kuliah inti bukan manifes masukan ini.

Adaptor programme-current-public-course-format-handoff/1 juga menerima paket
bersumber publik. Adaptor memeriksa ikatan bukti, identitas revisi sumber,
jumlah pelajaran/bacaan bersama dan catatan ZIP, lalu menerapkan pemeriksaan
PDF/EPUB/sumber yang sama. Berkas asli tidak diubah atau diberi label ulang;
izin penerbitan tidak disimpulkan. Tautan mata kuliah dan program daring
bersifat opsional, bukan dependensi luring.
Kategori pelajaran, bacaan bersama, bab prasyarat dan suplemen asli dihitung
serta ditampilkan terpisah; kategori itu tidak berarti seluruh mata kuliah lengkap.

Tanpa --reader dan --report, perintah hanya memeriksa tanpa menulis. Tujuan
keluaran baru belum boleh ada. Direktori bacaan harus terpisah dari direktori
pembuat sumber. Kegagalan tidak menghapus atau mengubah berkas pembuat sumber.
Keluaran baru yang belum lengkap akibat kegagalan baca/tulis bukan edisi yang
telah tervalidasi; periksa keluaran tersebut sebelum mencoba ulang.

Buka DIREKTORI_BACA_BARU/index.html. Antarmuka Inggris dan Indonesia memuat
unduhan langsung dengan urutan PDF, LaTeX kumulatif yang dapat disunting, ZIP
sumber lengkap, lalu EPUB. Setiap pelajaran memiliki tautan halaman PDF.
Lokasi berlabel dari sumber juga memiliki tautan tujuan PDF yang tepat dan
tautan halaman cadangan. Buka EPUB dengan aplikasi pembaca yang mendukungnya.
Lokasi berkas/fragmen internal EPUB dicantumkan, bukan diklaim sebagai tautan
langsung EPUB yang dapat dibuka peramban.

Penggantian bahasa hanya mengubah navigasi, bukan isi mata kuliah. Judul
pelajaran, atribusi, dan keterangan lisensi asli tetap dalam bahasa sumber
yang dinyatakan. Suplemen editorial dibedakan dari pelajaran. Keberhasilan
format tidak mengubah status draf, penerimaan mata kuliah, atau akses privat.

PEMERIKSAAN DAN BATASNYA
Alat memeriksa ukuran dan SHA-256, inventaris ZIP secara tepat, seluruh isi
sumber yang dinyatakan, kesamaan LaTeX langsung dengan isi arsip, halaman dan
tujuan bernama dalam PDF, bahasa/urutan baca/navigasi/fragmen EPUB, tautan
lokal, serta lokasi berlabel yang disediakan. Alat menolak jalur keluar arsip,
nama berkas ganda termasuk perbedaan huruf besar-kecil, entri bukan berkas
biasa, kunci JSON ganda, entitas XML, skrip, dan tautan berbahaya. Skrip sumber
dalam ZIP tidak diekstrak atau dijalankan. Pemeriksaan ini bukan lingkungan
pengamanan untuk sembarang kode yang dapat dijalankan.

Jika output/FORMULA_INDEX.json tersedia, anotasi rumus EPUB dibandingkan
menurut urutannya dengan catatan rumus tersebut; hanya spasi yang diabaikan.
Rumus judul yang diulang dalam daftar isi EPUB dihitung terpisah. Ini bukan
penguraian ulang rumus dari teks sumber ataupun pembuktian matematika mandiri.
Kelengkapan ZIP di sini berarti seluruh isi yang dinyatakan telah diverifikasi.
Pembuatan ulang, kebenaran matematika, dan aksesibilitas visual memerlukan
buktinya sendiri. Catatan hasil menyatakan pemeriksaan itu belum dijalankan.

PDF tanpa tag serta metadata judul PDF yang kosong dilaporkan. Lulusnya
pemeriksaan struktur EPUB tidak menjamin kinerja pembaca layar. Jalankan
EPUBCheck secara terpisah dan periksa tampilan PDF/EPUB sebelum menyatakan
edisi baru siap digunakan.

PENGUJIAN
python -B scripts/course-formats-v1/test_course_formats.py -v
python -B scripts/course-formats-v1/test_course_formats.py --intake PAKET_LOKAL -v

Pemeriksaan peramban opsional:
node scripts/course-formats-v1/check_reader.mjs DIREKTORI_BACA_BARU DIREKTORI_QA
Atur COURSE_PLAYWRIGHT_MODULE dan COURSE_CHROMIUM bila dependensi tidak berada
di jalur pencarian biasa. Pemeriksaan memakai peramban terpisah tanpa jendela,
memblokir permintaan jarak jauh, menguji kedua antarmuka pada lebar 1280/390/320
piksel, lalu menyimpan tangkapan layar dan catatan QA terbatas. Untuk skema
lokasi pertama, argumen ketiga/keempat opsional adalah EPUB yang sudah
diekstrak dengan aman dan FORMAT_ENTRY_LOCATORS.json. Untuk skema kedua,
gunakan entry_routes dari catatan hasil sebagai larik locators bila menyiapkan
masukan pemeriksaan geometri tersebut; jangan membuang pengenal sumber asli.

PRIVASI DAN PENGGUNAAN ULANG
Direktori bacaan dan catatan hasil mewarisi batas akses masukan. Mata kuliah
privat tetap lokal; penyalinan ke direktori baru bukan izin penerbitan.
Paket alat ini tidak memuat mata kuliah atau data masukan privat. Direktori
bacaan dapat dipindahkan ke hosting statis hanya bila penerbitan edisi tepat
itu telah diizinkan. Pemeriksaan lokal bukan verifikasi unduhan publik dan
tidak mengubah penghitungan penyelesaian program.
