# Program Matematika Indonesia v0.54.0

## Mulai belajar

**Situs untuk pelajar:**
<https://kokunoyumeto.github.io/program-matematika-indonesia/>

Pilih titik mulai, ikuti prasyarat dan petunjuk **Lanjut ke**, lalu buka
pembaca HTML atau PDF dari kartu mata kuliah. Zenodo menampilkan
`00_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.54.0.pdf` sebagai lembar
mulai-belajar manusia. Salinan HTML mandiri adalah
`01_MULAI_BELAJAR_PROGRAM_MATEMATIKA_INDONESIA_v0.54.0.html`.

## Perubahan

- Mengganti `docs/courses.js` sebagai sumber kebenaran dengan otoritas
  kurikulum berversi. Berkas UI itu sekarang selalu dihasilkan ulang dan
  diverifikasi byte demi byte.
- Menambahkan model-baca pelajar deterministik yang menghubungkan 40 peran
  kurikulum ke 34 dataset dan 126 permukaan federasi, lalu menghasilkan kartu,
  graf prasyarat 82-sisi, aksi belajar, dan arah **Lanjut ke**.
- Mempertahankan backend native setiap edisi sebagai kanon. Adapter reversibel
  membentuk backend bersama v1; federasi v2 menghubungkan identitas dan
  permukaan; model-baca menjadi proyeksi khusus situs, bukan backend pengganti.
- Menambahkan schema publik untuk otoritas kurikulum dan model-baca serta
  endpoint mesin sekunder di bawah situs belajar. Halaman HTML tetap menjadi
  pintu depan; JSON tidak menjadi aksi utama pelajar.
- Memisahkan keadaan publik yang berasal dari rekaman federasi dari bukti
  readback efektif. Dua PDF yang sebelumnya hanya berlabel
  `catalog_declared` kini memperoleh overlay readback anonim yang terikat hash,
  tanpa menulis ulang bukti historis federasi.
- Menambahkan replay A/B, validasi schema, pemeriksaan kebocoran locator
  internal, pemeriksaan tautan utama non-JSON, salinan schema publik, dan build
  situs sebagai satu rantai validasi rilis.

Koordinasi, rekayasa backend, validasi, dan penerbitan dilakukan oleh OpenAI
Codex gpt-5.6-sol, Ultra atas instruksi pengguna. Kredit sumber dan kontributor
tetap melekat pada setiap komponen.
