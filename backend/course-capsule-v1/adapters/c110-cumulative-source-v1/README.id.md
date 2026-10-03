# Sumber LaTeX kumulatif untuk Analisis Numerik

Ini adalah sumber lengkap yang dirakit dari edisi Bahasa Indonesia
*Tea Time Numerical Analysis*, edisi ketiga, karya Leon Q. Brin,
rilis `3.0-id.2-r1`. Isi buku tidak diterjemahkan ulang atau disunting.

## Berkas satu edisi

1. [PDF pembaca, 387 halaman](https://github.com/KokunoYumeto/tea-time-numerical-analysis-id/releases/download/v3.0-id.2-r1/Tea-Time-Numerical-Analysis-id-ID.pdf).
2. [LaTeX kumulatif langsung](https://github.com/KokunoYumeto/tea-time-numerical-analysis-id/releases/download/v3.0-id.2-r1/TeaTimeNumericalAnalysis-id-ID.tex).
3. [ZIP sumber lengkap, gambar, bibliografi, gaya dan backend](https://github.com/KokunoYumeto/tea-time-numerical-analysis-id/releases/download/v3.0-id.2-r1/Tea-Time-Numerical-Analysis-id-ID-v3.0-id.2-r1-source-backend.zip).

LaTeX kumulatif memuat seluruh teks, termasuk pengantar, bab, latihan, solusi
dan jawaban. Gambar, bibliografi dan gaya tetap tersedia dalam ZIP; berkas
LaTeX ini bukan paket mandiri tanpa dependensi. Struktur sumber asli di dalam
ZIP tidak diubah. Baca lisensi dan asal-usul komponen dalam ZIP tersebut.

## Menghasilkan PDF yang sama

Ekstrak ZIP. Salin folder `source/latex-id-ID/` ke folder kerja baru, lalu
letakkan LaTeX kumulatif di dalam folder kerja tersebut dengan nama
`TeaTimeNumericalAnalysis-id-ID.tex`. Jalankan dari folder kerja, menggunakan
instalasi TeX, `latexmk`, BibTeX, MakeIndex dan paket yang diperlukan:

```powershell
$env:SOURCE_DATE_EPOCH = '1787356800'
$env:FORCE_SOURCE_DATE = '1'
latexmk -pdf -interaction=nonstopmode -file-line-error -halt-on-error '-pdflatex=pdflatex -no-shell-escape %O %S' TeaTimeNumericalAnalysis-id-ID.tex
```

Di ruang kerja program ini, kompilasi wajib memakai mutex bersama
`Global\InterlanguageTeXSlotV1`; skrip
`scripts/verify-c110-cumulative-build-v1.ps1` menerapkannya. Contoh di atas
ditujukan untuk instalasi pembaca sendiri, bukan untuk melewati aturan ruang kerja.

Pada pemeriksaan 3 Oktober 2026, seluruh 895 berkas arsip dan 289 input build
cocok dengan inventaris rilis. Tiga puluh berkas teks disisipkan dalam urutan
aslinya, dengan setiap byte teks dipertahankan. Batas `include` mempertahankan
pemisahan halaman. Build dari sumber kumulatif menghasilkan PDF byte-identik
dengan PDF publik: 8.202.487 byte, SHA-256
`d573b7233d0baa07381e2052a749757885db3a31fbfe695c5a4851ea42d91b6d`.
Ini bukti kesetiaan perakitan dan kompilasi, bukan peninjauan baru atas seluruh
matematika atau mutu terjemahan. Keterbatasan edisi asal tetap berlaku.

## Kredit dan hak

Leon Q. Brin adalah penulis karya asal. Prosa, gambar buku dan adaptasi:
CC-BY-SA-4.0; kode: GPL-3.0-or-later; aset Heun: Public Domain Mark 1.0;
dependensi `cprotect`: LPPL-1.3c+. Tidak ada pelisensian ulang komponen.

Metadata rilis asli mencatat dukungan QA terminologi, produksi dan penyiapan
teknis oleh OpenAI Codex gpt-5.6-sol, Ultra, tanpa menyatakan identitas
penerjemah yang tidak tercatat. Perakitan sumber kumulatif, pemeriksaan build
dan integrasi unduhan pada 3 Oktober 2026 dilakukan oleh OpenAI Codex -
GPT-6 Astra, Ultra effort. Tidak ada klaim penyuntingan atau peninjauan manusia.
