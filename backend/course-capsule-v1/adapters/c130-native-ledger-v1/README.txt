Catatan sumber, istilah dan koreksi C130 / C130 native records

Halaman ini mempertahankan 140 pilihan istilah, 128 identitas konsep dan
94 catatan koreksi dari backend asli. Semua identitas dan 21 komponen hak
dipertahankan. Hubungan konsep ke segmen bukan bukti kemunculan kata.
Teks buku tidak disalin ke proyeksi. Semua bidang yang tidak diproyeksikan
tetap tersedia di arsip backend asli dengan SHA-256 yang dicatat.

Buka site/ledger.html atau site/ledger.en.html. Pencarian berjalan luring.
Bangun ulang dari akar paket:
  python -B scripts/build-c130-native-ledger-v1.py

Untuk mengulangi pemeriksaan arsip asli, unduh tiga berkas yang tercatat
dalam input/source-lock.json lalu jalankan:
  python -B scripts/c130-native-ledger-v1.py --cache /path/to/cache

Status approved dan bukti istilah merupakan catatan asli. Pemeriksaan ini
tidak melakukan peninjauan kanon baru atau validasi semantik setiap koreksi.
Seluruh 5.186 catatan dengan teks target mempunyai rujukan yang cocok:
5.184 pada baris yang dinyatakan dan dua melalui penggabungan bagian asli.
Sebanyak 21 rujukan yang sebelumnya belum pasti diperbaiki tanpa mengubah
catatan asli. Buka bagian pemeriksaan rujukan pada halaman atau baca
location-review.json. input/location-review-baseline.json mempertahankan
identitas dan hasil lama. Penghitungan baris memakai LF, bukan setiap
karakter pemisah yang dikenali splitlines. Dua penggabungan memakai aturan
asli yang dicatat dalam backend/input/backend-input.json dan kode pembuatnya.
Satu dari dua berkas penggabungan berbeda dari SHA-256 berkas utuh yang
dicatat pembuat buku. Bagian teksnya cocok persis; seluruh berkas belum
terbukti sama. Pembangunan ulang buku dan persetujuan kanon tidak diklaim.

English: this view preserves native identities and claims with explicit
source-location checks. It does not certify terminology or mathematical
correctness. The full native archive retains every omitted field. Rebuild
the page with the command above; download the book separately. All 21 old
location gaps now have exact source-bound proofs; one of the two alignment
files retains an explicit whole-file hash mismatch. Exact segment alignment
does not establish whole-file equality, native build replay or canon approval.

Audit/projection: OpenAI Codex — gpt-6-astra, Ultra effort.
Page/integration refinements: OpenAI Codex — gpt-6.1-sol, Ultra effort.
