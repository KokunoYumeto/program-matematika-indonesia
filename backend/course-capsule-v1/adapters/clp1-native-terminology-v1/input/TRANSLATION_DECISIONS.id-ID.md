# Keputusan terjemahan Bahasa Indonesia

Dokumen ini mencatat kebijakan yang berlaku untuk seluruh edisi. Diff lengkap
dan manifest byte menjadi bukti keputusan pada tingkat berkas.

## Ragam dan tujuan pembaca

- Ragam: Bahasa Indonesia baku yang dapat dibaca mandiri oleh mahasiswa dan
  pembelajar otodidak.
- Kalimat dipertahankan langsung dan pedagogis; kelancaran tidak boleh
  menghapus hipotesis, kuantor, tanda, arah implikasi, atau kasus batas.
- Titik desimal di dalam rumus dan kode dipertahankan ketika merupakan notasi
  sumber; prosa Indonesia dapat memakai koma desimal.
- Komentar TeX tidak aktif boleh tetap berbahasa Inggris. Permukaan aktif,
  termasuk teks dalam gambar, wajib dilokalkan atau dinyatakan sebagai nama,
  judul, kode, atau pengenal yang sengaja dipertahankan.

## Istilah inti

| Inggris | Bahasa Indonesia |
| --- | --- |
| limit | limit |
| derivative | turunan |
| differentiable | dapat didiferensialkan |
| differentiability | keterdiferensialan / sifat dapat didiferensialkan |
| tangent line | garis singgung |
| secant line | garis sekan |
| average rate of change | laju perubahan rata-rata |
| Mean Value Theorem | Teorema Nilai Rata-Rata (TNR) |
| Intermediate Value Theorem | Teorema Nilai Antara |
| product rule | aturan hasil kali (AHK) |
| quotient rule | aturan hasil bagi (AHB) |
| chain rule | aturan rantai |
| antiderivative | antiturunan |
| concave up/down | cekung ke atas/ke bawah |
| inflection point | titik belok |
| local/absolute maximum | maksimum lokal/absolut |
| reciprocal function | fungsi resiprokal |
| asymptote | asimtot |
| root-finding | pencarian akar |
| hint / answer / solution | petunjuk / jawaban / penyelesaian |

Notasi mnemonic yang telah dijelaskan sebagai notasi internasional dapat
dipertahankan. Singkatan pembaca yang dilokalkan, seperti TNR, AHK, dan AHB,
dipakai secara konsisten setelah audit visual menemukan residu MVT/PR/QR.

## Struktur dan matematika

- Urutan environment, label, referensi, item, dan pemanggilan aset diputar ulang
  terhadap sumber pada setiap tranche dan pada penutupan buku.
- Rumus dipertahankan secara struktural. Perbedaan matematika harus masuk salah
  satu dari dua kelas: koreksi sumber yang dicatat atau perbaikan tipografi yang
  tidak mengubah makna.
- Aset lokal memakai nama baru berakhiran `_id`; aset sumber tidak ditimpa.
- Penyelesaian yang memerlukan nilai mutlak, domain, kasus batas, atau asumsi
  keterdiferensialan eksplisit diperbaiki hanya ketika hasil sumber salah atau
  tidak terdefinisi tanpa perbaikan tersebut.

## Metadata peninjauan

Pemeriksaan independen berarti byte target dibaca oleh proses/agen lain yang
tidak menulis berkas yang dinilai. Metadata ini tidak menyatakan adanya
peninjauan penutur asli atau peer review manusia. Koreksi pascarilis diterima
sebagai versi baru yang mempertahankan hash dan provenance versi lama.
