# Program Matematika Indonesia v0.46.0

Snapshot pusat ini tetap merupakan pekerjaan berjalan. Empat puluh dari empat
puluh peran kurikulum memiliki korpus terpilih atau spesifikasi asli yang
dibekukan, tetapi sebagian besar terjemahan dan edisi akhir masih diproduksi.

## C10 kini lengkap dan publik

v0.46.0 mengakui C10, *Analisis Real I*, sebagai peran mata kuliah lengkap.
Jilid I *Basic Analysis* karya Jiří Lebl telah diterjemahkan sepenuhnya ke
Bahasa Indonesia dan diterbitkan dalam checkpoint U227:

- pembaca lengkap 334 halaman;
- 2.870.909 byte;
- SHA-256
  `38743ea0e7ce52bdadf5233fc9d6e79e00717f9ba55a393f2bf46ea21c65ef56`;
- DOI versi `10.5281/zenodo.22063321`;
- lineage konsep `10.5281/zenodo.22059779`;
- repositori
  <https://github.com/KokunoYumeto/lebl-mathematics-family-id>.

Rekaman U227 memiliki delapan berkas dengan total 7.867.649 byte. Seluruh
ukuran dan MD5 API Zenodo cocok dengan unduhan anonim, dan ketujuh SHA-256 yang
dideklarasikan dalam `SHA256SUMS.txt` cocok dengan byte publik.

Program kini mencatat sebelas peran dengan edisi lengkap pada sepuluh rekaman
publik berbeda karena C30 dan C40 memakai satu edisi Judson yang sama.

## C20 tetap pekerjaan berjalan

Checkpoint U227 juga menerbitkan cuplikan C20, *Analisis Real II*, sepanjang
154 halaman sampai akhir bukti Teorema 10.7.2:

- 1.687.583 byte;
- SHA-256
  `b4da246e79fb30ea74e8fcf48ec0fa50aa2680f52585f6b89f66762d7f7876ed`.

Latihan Bagian 10.7 belum termasuk. Cuplikan ini ditautkan agar dapat digunakan
dan diperiksa, tetapi C20 tetap berstatus produksi. B70/ODE dan
C50/Analisis Kompleks juga tetap produksi;
checkpoint U227 tidak mengklaim kedua korpus itu telah diterjemahkan.

## Backend dan peta semantik tidak berubah

Tujuh bukti migrasi korpus lengkap tetap berada di bawah kontrak backend
bersama v1: DMOI, B80, Open Logic, Judson, Poritz/YAIN, Applied Combinatorics,
dan Mathematics in Lean. Jumlah target bukti migrasi tetap 244.416 rekaman,
sedangkan paket kurikulum pusat tetap terpisah dengan 2.122 rekaman.

Peta `ownerLane` tetap tepat: 40 peran, 40 ikatan semantik, nol ID hilang atau
ekstra, dan nol salah ikat. Validator v0.46.0 mengikat secara eksplisit sebelas
peran selesai, sepuluh DOI versi terkini, batas C20/B70/C50 yang belum selesai,
tujuh receipt migrasi, identitas skema katalog, commit sumber, inventaris rilis,
dan pemindaian privasi.

## Provenance

Koordinasi, rekayasa backend, validasi, dan penerbitan snapshot pusat dilakukan
oleh **OpenAI Codex gpt-5.6-sol, Ultra** atas instruksi pengguna. Kredit penulis,
penerjemah manusia, dan kontributor tetap dipertahankan pada setiap komponen.

## Preservasi

- DOI versi pusat: `10.5281/zenodo.22063396`
- DOI konsep pusat: `10.5281/zenodo.22059707`
- Repositori: <https://github.com/KokunoYumeto/program-matematika-indonesia>

Rilis dianggap selesai hanya setelah seluruh berkas dipublikasikan dan dibaca
kembali secara anonim dengan kecocokan nama, ukuran, dan SHA-256.
