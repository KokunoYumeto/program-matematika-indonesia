# Tinjauan dua pemakaian istilah peluang bersyarat

Tinjauan editorial retrospektif, 8 September 2026. Rekaman ini memeriksa dua
pemakaian dalam teks terjemahan, bukan hanya daftar istilah. Ini bukan
pengesahan seluruh B90, D30, atau semua sembilan konsep keluarga peluang.

## B90: pertahankan «peluang bersyarat»

Pada §4.1 Grinstead–Snell, kalimat definisi sebelum Contoh 4.3 mempertahankan
kejadian yang menjadi syarat, irisan kejadian, dan penyebut pada rumus
`P(F|E)=P(F∩E)/P(E)`. Asumsi `P(E)>0` tercantum dalam penurunan yang mendahuluinya.
Teks sumber dan terjemahan diperiksa bersama; rumus tampilan dalam bagian
terpilih identik. Definisi 1.13 ULM memakai istilah yang sama untuk konsep ini.
Karena itu, pemakaian ini dipertahankan. Alternatif «probabilitas bersyarat»
juga memiliki dukungan sumber; alternatif tersebut tidak dinyatakan salah.

## D30: pertahankan «probabilitas bersyarat»

Paragraf pertama *Contoh Dasar* pada materi nilai harapan bersyarat
menghubungkan teori umum dengan pengondisian pada kejadian berprobabilitas
positif. Pasangan sumber–terjemahan `segment.o009.random.expect.conditional2.0123`
mempertahankan `P(A)>0` dan `P(B|A)=P(A∩B)/P(A)`. Definisi 1.3 UAD mendukung
istilah tersebut untuk konsep yang sama. Perbedaan nama variabel tidak
mengubah kejadian yang menjadi syarat. Tinjauan ini tidak diperluas secara
otomatis ke probabilitas bersyarat reguler atau pengondisian pada aljabar-sigma.

Ada temuan terpisah: anotasi `\text{ for measurable }` masih berbahasa Inggris
dalam rumus kedua paragraf tersebut. Anotasi itu dikonfirmasi pada berkas sumber
publik dan halaman pembaca tanggal 8 September. Rumus tidak dinyatakan rusak,
tetapi paragraf ini belum dapat dinyatakan selesai ditinjau secara kebahasaan.
Perbaikannya harus menyasar bahasa anotasi sambil mempertahankan simbol,
hipotesis, dan hubungan matematis, lalu memperbarui artefak terkait.

## Bukti dan batas pemeriksaan

[Rekaman terstruktur](course-conditional-probability-occurrences-v1.json)
mengikat identitas segmen, lokasi bagian teks, hash sumber/terjemahan, istilah,
alasan, alternatif, keyakinan editorial beserta alasannya, dan temuan terbuka.
Bukti kanon berasal dari [ULM](ulm-probability-review-v1.md) dan
[UAD](uad-probability-review-v1.md). Halaman definisi asli diperiksa kembali;
catatan ULM yang menyamakan peluang nol dengan ketidakmungkinan tidak diadopsi.

Validator memeriksa kembali identitas, hubungan rekaman asli, rumus, dan
penautan bukti; pemeriksaan itu bukan penilaian makna otomatis. Bukti diperoleh
secara retrospektif, bukan klaim bahwa kanon telah dibaca saat penerjemahan
semula. Tidak ada penggantian istilah massal, perubahan teks produksi, atau
keharusan menunggu tanggapan manusia. Naskah lengkap dan bukti sumber tetap
berada pada penyedia masing-masing; rekaman ini tidak menyalin seluruh buku.

## English summary

Both selected event-conditioning occurrences are supported by their source
mathematics and independent Indonesian definitions. Retain the course-specific
terms. One English annotation remains separately open in D30; this terminology
decision does not certify the whole paragraph or either whole course.
