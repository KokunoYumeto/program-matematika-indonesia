export const courses = [
  {
    id: 'A00', ownerLane: 'R001', level: 'A', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Praaljabar dan Fondasi Kuantitatif', prerequisites: [],
    purpose: 'Bilangan bulat, pecahan, desimal, persen, rasio, pengukuran, dan persamaan dasar dengan jalur diagnosis yang dapat dilewati.',
    outcome: 'Mengolah representasi numerik dengan andal dan mengenali apakah kesalahan berikutnya bersifat aritmetis atau konseptual.',
    corpus: 'OpenStax Prealgebra 2e', note: 'Korpus terpilih; edisi Bahasa Indonesia sedang diproduksi.'
  },
  {
    id: 'A10', ownerLane: 'OPENSTAX-ELEMENTARY', level: 'A', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Aljabar Dasar', prerequisites: ['A00'],
    purpose: 'Persamaan dan pertidaksamaan linear, grafik, sistem, eksponen, polinom, faktorisasi, bentuk rasional, dan akar.',
    outcome: 'Menerjemahkan hubungan kuantitatif ke bentuk aljabar dan menyelesaikannya dengan langkah yang dapat dijelaskan.',
    corpus: 'OpenStax Elementary Algebra 2e — 82 modul', note: 'Korpus terpilih; produksi masih pada tahap awal.'
  },
  {
    id: 'A20', ownerLane: 'OPENSTAX-INTERMEDIATE', level: 'A', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Aljabar Menengah', prerequisites: ['A10'],
    purpose: 'Fungsi, model kuadrat dan rasional, akar, bilangan kompleks, eksponensial, logaritma, irisan kerucut, dan barisan.',
    outcome: 'Memasuki prakalkulus dengan kefasihan simbolik dan pemahaman fungsi yang stabil.',
    corpus: 'OpenStax Intermediate Algebra 2e — 83 modul', note: 'Korpus terpilih; satu modul telah mencapai batas produksi.'
  },
  {
    id: 'A30', ownerLane: 'R002', level: 'A', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Prakalkulus dan Trigonometri', prerequisites: ['A20'],
    purpose: 'Transformasi fungsi, model polinom, rasional, eksponensial dan logaritmik, trigonometri, geometri analitik, sistem, barisan, dan limit awal.',
    outcome: 'Memodelkan dengan fungsi elementer dan memulai kalkulus tanpa menyembunyikan kebutuhan perbaikan aljabar.',
    corpus: 'OpenStax Precalculus 2e', note: 'Korpus terpilih; fondasi modular enam modul sudah lolos audit byte.'
  },
  {
    id: 'B10', ownerLane: 'R004', level: 'B', topic: 'Diskrit & Logika', state: 'published',
    title: 'Pembuktian, Logika, dan Struktur Diskrit', prerequisites: ['A30'],
    purpose: 'Logika proposisional dan predikat, himpunan, fungsi, relasi, teknik bukti, teori graf, pencacahan, dan barisan.',
    outcome: 'Membaca, menyusun, dan mengkritik bukti elementer sebelum memasuki teori tingkat lanjut.',
    corpus: 'Discrete Mathematics: An Open Introduction 4', note: 'Edisi Bahasa Indonesia selesai dan rilis preservasi 2026.08.22 telah diverifikasi publik.',
    edition: 'https://zenodo.org/records/22060439/files/00_MATEMATIKA_DISKRET_EDISI_KEEMPAT_BAHASA_INDONESIA_READER.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/discrete-mathematics-open-introduction-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22060439'
  },
  {
    id: 'B20', ownerLane: 'R003', level: 'B', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Kalkulus Diferensial', prerequisites: ['A30'],
    purpose: 'Limit, kontinuitas, turunan, pendekatan, optimisasi, dan pemodelan dengan masalah terpecahkan yang terintegrasi.',
    outcome: 'Menggunakan turunan secara komputasional dan konseptual serta menjelaskan hipotesis yang dipakai.',
    corpus: 'CLP Calculus — kalkulus diferensial', note: 'Korpus terpilih; pemetaan latihan dan backend sedang dibangun.',
    edition: 'https://github.com/KokunoYumeto/clp1-differential-calculus-id'
  },
  {
    id: 'B30', ownerLane: 'R003', level: 'B', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Kalkulus Integral', prerequisites: ['B20'],
    purpose: 'Integral, teorema dasar kalkulus, teknik integrasi, penerapan, barisan, deret, dan persamaan diferensial awal.',
    outcome: 'Memilih dan membenarkan metode integral atau deret serta menghubungkan akumulasi dengan laju lokal.',
    corpus: 'CLP Calculus — kalkulus integral', note: 'Korpus terpilih dalam jalur produksi CLP bersama.'
  },
  {
    id: 'B40', ownerLane: 'R005', level: 'B', topic: 'Aljabar', state: 'near',
    title: 'Aljabar Linear', prerequisites: ['A30', 'B10'],
    purpose: 'Sistem linear, ruang vektor, pemetaan linear, matriks, determinan, nilai dan vektor eigen, serta penerapan.',
    outcome: 'Berpindah dengan lancar antara perhitungan, struktur, dan pembuktian dalam matematika berdimensi hingga.',
    corpus: 'Hefferon — Linear Algebra lengkap', note: 'Teks dan 1.037 tautan jawaban tertutup; build dan rilis akhir masih berlangsung.'
  },
  {
    id: 'B50', ownerLane: 'R003', level: 'B', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Kalkulus Multivariabel', prerequisites: ['B30', 'B40'],
    purpose: 'Geometri beberapa variabel, turunan parsial, integral lipat, optimisasi berkendala, dan sistem koordinat.',
    outcome: 'Menganalisis fungsi skalar multivariabel dan menghubungkan linearisasi lokal dengan geometri.',
    corpus: 'CLP Calculus — kalkulus multivariabel', note: 'Korpus terpilih dalam jalur produksi CLP bersama.'
  },
  {
    id: 'B60', ownerLane: 'R003', level: 'B', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Kalkulus Vektor', prerequisites: ['B50'],
    purpose: 'Medan vektor, integral garis dan permukaan, serta teorema Green, Stokes, dan divergensi.',
    outcome: 'Menafsirkan teorema integral utama yang menghubungkan struktur diferensial lokal dengan besaran global.',
    corpus: 'CLP Calculus — kalkulus vektor', note: 'Korpus terpilih dalam jalur produksi CLP bersama.'
  },
  {
    id: 'B70', ownerLane: 'R006-R008', level: 'B', topic: 'Fondasi & Kalkulus', state: 'production',
    title: 'Persamaan Diferensial Biasa dan Sistem Dinamika Pengantar', prerequisites: ['B30', 'B40'],
    purpose: 'Persamaan orde satu, persamaan linear orde tinggi, sistem, transformasi, deret, bidang fase nonlinear, dan pengantar Fourier/PDP.',
    outcome: 'Merumuskan, menganalisis, mendekati, dan mengomunikasikan solusi model PDB standar.',
    corpus: 'Korpus keluarga Lebl', note: 'Korpus terpilih; produksi berjalan dalam jalur Lebl bersama.'
  },
  {
    id: 'B80', ownerLane: 'O002', level: 'B', topic: 'Komputasi & Optimisasi', state: 'published',
    title: 'Komputasi Matematis dan Eksperimen Reprodusibel', prerequisites: ['A30'],
    purpose: 'Python, SageMath, SymPy, NumPy/SciPy, komputasi eksak dan floating, visualisasi, pengujian, notebook literat, serta eksperimen reprodusibel.',
    outcome: 'Menerapkan objek dan eksperimen matematis sambil membedakan komputasi, bukti pendukung, dan pembuktian.',
    corpus: 'Rangka asli lengkap: P01/P02 + 12 unit, SciPy, SageMath, visualisasi, lingkungan, dan penguasaan',
    note: 'Edisi B80 lengkap dan terverifikasi publik: 14 unit, 75 latihan, 177 uji lulus, pembaca PDF 159 halaman, serta HTML, EPUB, sumber editabel, dan paket luring.',
    edition: 'https://zenodo.org/records/22053905/files/Komputasi-Matematis-dan-Eksperimen-yang-Dapat-Direproduksi.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/mathematical-computing-reproducible-experiments-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22053905'
  },
  {
    id: 'B90', ownerLane: 'R010', level: 'B', topic: 'Peluang & Statistika', state: 'published',
    title: 'Probabilitas Berbasis Kalkulus', prerequisites: ['B30'],
    purpose: 'Probabilitas diskrit dan kontinu, probabilitas bersyarat, peubah acak, harapan, limit, simulasi, jalan acak, dan rantai Markov.',
    outcome: 'Membangun dan menganalisis model peluang serta menghubungkan hasil analitik dengan simulasi.',
    corpus: 'Grinstead–Snell', note: 'Edisi 554 halaman selesai; backend modular berada dalam edisi kursus yang sama.',
    edition: 'https://zenodo.org/records/22062144/files/PENGANTAR_PELUANG_GRINSTEAD_SNELL_ID.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/introduction-to-probability-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22062144'
  },
  {
    id: 'B95', ownerLane: 'R011', level: 'B', topic: 'Peluang & Statistika', state: 'production',
    title: 'Statistika Terapan dan Analisis Data', prerequisites: ['A30', 'B90'],
    purpose: 'Pengumpulan data, deskripsi, ketidakpastian, inferensi, eksperimen, regresi, dan analisis reprodusibel dengan perangkat lunak terbuka.',
    outcome: 'Mengkritik proses pembentukan data dan melakukan analisis statistik awal secara transparan.',
    corpus: 'OpenIntro Statistics', note: 'Korpus terpilih; Bab 1 telah diakui dengan 716 rekaman bertipe.'
  },
  {
    id: 'C10', ownerLane: 'R006-R008', level: 'C', topic: 'Analisis', state: 'production',
    title: 'Analisis Real I', prerequisites: ['B10', 'B30'],
    purpose: 'Bilangan real, barisan, deret, kontinuitas, diferensiasi, dan integrasi Riemann dengan penekanan pada bukti.',
    outcome: 'Mengendalikan kuantor dan menyusun argumen rigor tentang limit, kontinuitas, turunan, dan integral.',
    corpus: 'Lebl — Analysis Volume I', note: 'Korpus terpilih; produksi berjalan dalam jalur Lebl bersama.'
  },
  {
    id: 'C20', ownerLane: 'R006-R008', level: 'C', topic: 'Analisis', state: 'production',
    title: 'Analisis Real II', prerequisites: ['C10', 'B50'],
    purpose: 'Barisan fungsi, ruang metrik, diferensiasi dan integrasi multivariabel, serta konstruksi limit.',
    outcome: 'Bekerja fasih dengan abstraksi ruang metrik dan bukti analitik multivariabel.',
    corpus: 'Lebl — Analysis Volume II', note: 'Korpus terpilih; materi invers dan implisit telah masuk produksi.'
  },
  {
    id: 'C30', ownerLane: 'R009', level: 'C', topic: 'Aljabar', state: 'published',
    title: 'Aljabar Abstrak I', prerequisites: ['B10', 'B40'],
    purpose: 'Grup, subgrup, homomorfisme, struktur hasil bagi, aksi grup, dan penerapan simetri.',
    outcome: 'Bernalar secara struktural dengan objek aljabar dan membuktikan hasil dari aksioma.',
    corpus: 'Judson — Abstract Algebra: Theory and Applications', note: 'Edisi Bahasa Indonesia selesai dan tersedia untuk umum.',
    edition: 'https://zenodo.org/records/22062449/files/ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.22.2.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/abstract-algebra-theory-and-applications-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22062449'
  },
  {
    id: 'C40', ownerLane: 'R009', level: 'C', topic: 'Aljabar', state: 'published',
    title: 'Aljabar Abstrak II', prerequisites: ['C30'],
    purpose: 'Gelanggang, ideal, gelanggang hasil bagi, domain integral, polinom, medan, perluasan, dan teori Galois awal.',
    outcome: 'Menggunakan struktur aljabar untuk menganalisis persamaan, faktorisasi, dan perluasan medan.',
    corpus: 'Judson — Abstract Algebra: Theory and Applications', note: 'Selesai dalam edisi Judson Bahasa Indonesia yang sama.',
    edition: 'https://zenodo.org/records/22062449/files/ALJABAR_ABSTRAK_TEORI_DAN_PENERAPAN_ID_2026.08.22.2.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/abstract-algebra-theory-and-applications-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22062449'
  },
  {
    id: 'C50', ownerLane: 'R006-R008', level: 'C', topic: 'Analisis', state: 'production',
    title: 'Analisis Kompleks', prerequisites: ['C20'],
    purpose: 'Fungsi holomorf, integrasi kontur, teori Cauchy, residu, keluarga normal, pemetaan konformal, fungsi harmonik, dan kelanjutan analitik.',
    outcome: 'Membaca dan menghasilkan pembuktian analisis kompleks pada tingkat masuk pascasarjana.',
    corpus: 'Korpus analisis kompleks Lebl', note: 'Korpus terpilih; produksi berjalan dalam jalur Lebl bersama.'
  },
  {
    id: 'C60', ownerLane: 'R014', level: 'C', topic: 'Diskrit & Logika', state: 'published',
    title: 'Teori Bilangan dan Kriptologi', prerequisites: ['B10', 'C30'],
    purpose: 'Keterbagian, kongruensi, bilangan prima, fungsi aritmetika, masalah Diophantus, dan konstruksi kriptografi kunci publik.',
    outcome: 'Membuktikan hasil teori bilangan elementer dan menganalisis asumsi matematika di balik kriptosistem dasar.',
    corpus: 'Jonathan Poritz — Yet Another Introductory Number Theory Textbook',
    note: 'Edisi Bahasa Indonesia lengkap dan terverifikasi publik: 138 halaman, 5.272 rekaman native, dan cakupan hingga kriptografi kunci publik. Pendamping penguasaan tetap merupakan penutupan terpilih untuk keterbatasan solusi sumber dan dilacak terpisah dari selesainya terjemahan buku.',
    edition: 'https://github.com/KokunoYumeto/yet-another-introductory-number-theory-textbook-id/releases/tag/v1.0.0',
    repository: 'https://github.com/KokunoYumeto/yet-another-introductory-number-theory-textbook-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22052196'
  },
  {
    id: 'C70', ownerLane: 'R012', level: 'C', topic: 'Diskrit & Logika', state: 'published',
    title: 'Kombinatorika Terapan', prerequisites: ['B10'],
    purpose: 'Pencacahan lanjut, rekurensi, fungsi pembangkit, teori graf, himpunan terurut sebagian, dan metode ekstremal.',
    outcome: 'Memilih dan membenarkan model serta teknik pembuktian kombinatorial untuk berbagai masalah diskrit.',
    corpus: 'Keller–Trotter — Applied Combinatorics', note: 'Edisi Bahasa Indonesia lengkap dan terverifikasi publik: pembaca 350 halaman, 19.048 rekaman native, 19.049 rekaman backend bersama termasuk satu jangkar prasyarat eksternal B10, HTML luring, sumber koresponding, dan tiga mirror preservasi.',
    edition: 'https://zenodo.org/records/22062005/files/00_KOMBINATORIKA_TERAPAN_ID-ID_COMPLETE_LINKED_READER_2026.08.22.2.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/applied-combinatorics-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22062005'
  },
  {
    id: 'C80', ownerLane: 'R013', level: 'C', topic: 'Diskrit & Logika', state: 'published',
    title: 'Logika Matematis, Teori Himpunan, dan Komputabilitas', prerequisites: ['B10'],
    purpose: 'Bahasa dan semantik formal, sistem bukti, ketaklengkapan, fondasi komputabilitas, teori himpunan aksiomatik, dan teori model awal.',
    outcome: 'Memahami batas formal dan kerangka fondasional dalam praktik matematika biasa.',
    corpus: 'Open Logic Project — OLP-0722, 722/722 modul', note: 'Edisi Bahasa Indonesia lengkap dan diterbitkan dengan lisensi CC BY 4.0.',
    edition: 'https://zenodo.org/records/21932787/files/00_OPENLOGIC_id_COMPLETE_LINKED_READER_OLP-0722.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/OpenLogic-id',
    zenodo: 'https://doi.org/10.5281/zenodo.21932787'
  },
  {
    id: 'C90', ownerLane: 'O003', level: 'C', topic: 'Geometri & Topologi', state: 'production',
    title: 'Topologi Himpunan-Titik', prerequisites: ['B10', 'C10'],
    purpose: 'Ruang topologis, basis, kontinuitas, produk dan hasil bagi, kekompakan, keterhubungan, aksioma pemisahan, keterhitungan, metrisasi, dan ruang fungsi.',
    outcome: 'Menggunakan invarian dan konstruksi topologis sebagai bahasa bersama analisis, geometri, dan aljabar.',
    corpus: 'GVSU Topology lengkap + pendamping PreTeXt asli', note: 'Korpus terpilih dan diserahkan; pembaca kumulatif Bab 1–3 berada pada batas build dan QA yang dapat direproduksi.',
    edition: 'https://github.com/KokunoYumeto/topology-an-inquiry-based-approach-id'
  },
  {
    id: 'C100', ownerLane: 'O004', level: 'C', topic: 'Geometri & Topologi', state: 'production',
    title: 'Geometri: Euklides, Afin, Projektif, dan Non-Euklides', prerequisites: ['B10', 'B40', 'B60'],
    purpose: 'Geometri aksiomatik dan transformasional, metode afin dan projektif, geometri hiperbolik dan sferis, permukaan, dan konstruksi.',
    outcome: 'Membandingkan geometri melalui aksioma, transformasi, dan invarian, bukan sebagai satu konvensi tunggal.',
    corpus: 'Petrunin 20 bab + pendamping Transformasi, Invarian, dan Permukaan Model + volume penguasaan',
    note: 'Korpus terpilih; repositori dan arsip tetap privat/terbatas sesuai instruksi.'
  },
  {
    id: 'C110', ownerLane: 'R015', level: 'C', topic: 'Komputasi & Optimisasi', state: 'published',
    title: 'Analisis Numerik', prerequisites: ['B30', 'B40', 'B80', 'C10'],
    purpose: 'Galat floating-point, pencarian akar, interpolasi, pendekatan, diferensiasi dan integrasi numerik, serta aljabar linear numerik.',
    outcome: 'Menurunkan, menerapkan, dan menilai algoritma numerik dengan alasan stabilitas dan galat yang eksplisit.',
    corpus: 'Tea Time Numerical Analysis — edisi Bahasa Indonesia lengkap',
    note: 'Selesai dan terverifikasi publik: 31/31 unit, pembaca 387 halaman, 28.172 rekaman backend, 17.614 relasi, dan 20/20 uji akhir. Arsip Zenodo tetap publik; akses akun GitHub telah dipulihkan dan sinkronisasi mirror kembali dimungkinkan.',
    edition: 'https://zenodo.org/records/22054086/files/Tea-Time-Numerical-Analysis-id-ID.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/tea-time-numerical-analysis-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22054086'
  },
  {
    id: 'C120', ownerLane: 'O005', level: 'C', topic: 'Komputasi & Optimisasi', state: 'production',
    title: 'Pemodelan Matematis dan Dinamika Nonlinear', prerequisites: ['B70', 'B80', 'C10'],
    purpose: 'Analisis dimensi, konstruksi dan validasi model, sistem dinamis diskrit/kontinu, bifurkasi, chaos, dan studi kasus.',
    outcome: 'Bergerak iteratif antara asumsi, struktur matematika, komputasi, data, dan kritik model.',
    corpus: 'Lega v1.01', note: 'Korpus terpilih; Bab 6 sudah publik dan terverifikasi, lalu produksi bergerak ke Bab 7 tentang epidemiologi.',
    edition: 'https://github.com/KokunoYumeto/mathematical-modeling-nonlinear-dynamics-id'
  },
  {
    id: 'C130', ownerLane: 'O018', level: 'C', topic: 'Komputasi & Optimisasi', state: 'production',
    title: 'Optimisasi Linear dan Integer / Riset Operasi', prerequisites: ['B40', 'B80', 'C70'],
    purpose: 'Program linear, dualitas, konsep simpleks/interior, jaringan, program integer, kompleksitas, pemodelan, dan implementasi dengan solver bebas.',
    outcome: 'Merumuskan, menyelesaikan, dan mengkritik model optimisasi tanpa bergantung pada solver proprieter.',
    corpus: 'Open Optimization + adaptasi solver terbuka O018', note: 'Korpus terpilih; produksi aktif dan tiga cacat rilis Bab 5 yang teridentifikasi sedang diperbaiki sebelum penerimaan backend.'
  },
  {
    id: 'C140', ownerLane: 'O006', level: 'C', topic: 'Peluang & Statistika', state: 'production',
    title: 'Statistika Matematis', prerequisites: ['B90', 'B95', 'B40', 'C10'],
    purpose: 'Distribusi sampling, kecukupan, estimasi, likelihood, interval kepercayaan, uji hipotesis, perbandingan Bayes, regresi, dan asimtotik.',
    outcome: 'Menurunkan dan menilai prosedur statistik, bukan sekadar menerapkannya sebagai kotak hitam.',
    corpus: 'Penn State STAT 415 lengkap + satu unit Random tentang kecukupan/kelengkapan + pendamping rigor dan penguasaan asli',
    note: 'Korpus terpilih dan diterima pemilik produksi; checkpoint Random enam halaman sudah publik dan edisi Random penuh tetap proyek terpisah.'
  },
  {
    id: 'D10', ownerLane: 'O007', level: 'D', topic: 'Analisis', state: 'production',
    title: 'Ukuran dan Integrasi', prerequisites: ['C20', 'C90'],
    purpose: 'Sigma-aljabar, ukuran, fungsi terukur, integral Lebesgue, teorema konvergensi, ukuran produk, Radon–Nikodym, dan ruang Lp.',
    outcome: 'Menggunakan teori integrasi modern sebagai dasar peluang, analisis fungsional, dan PDP.',
    corpus: 'Fremlin — Measure Theory Jilid 1–2', note: 'Korpus terpilih; unit S114 telah lolos perbaikan browser dan sedang dikemas ulang secara deterministik.',
    edition: 'https://github.com/KokunoYumeto/fremlin-measure-theory-id'
  },
  {
    id: 'D20', ownerLane: 'O008', level: 'D', topic: 'Analisis', state: 'production',
    title: 'Analisis Fungsional', prerequisites: ['D10', 'B40'],
    purpose: 'Ruang bernorma, Banach dan Hilbert; operator terbatas; Hahn–Banach; boundedness seragam; pemetaan terbuka; dualitas; teori kompak dan spektral.',
    outcome: 'Bernalar dengan ruang dan operator berdimensi tak hingga pada tingkat pascasarjana awal.',
    corpus: 'Erdman — Functional Analysis', note: 'Korpus terpilih; PDF kumulatif Bab 4 sepanjang 75 halaman sudah identik dalam dua build dan memasuki inspeksi akhir.',
    edition: 'https://github.com/KokunoYumeto/functional-analysis-erdman-id'
  },
  {
    id: 'D30', ownerLane: 'O009', level: 'D', topic: 'Peluang & Statistika', state: 'production',
    title: 'Probabilitas Teoretis-Ukuran dan Proses Stokastik', prerequisites: ['D10', 'B90', 'C140'],
    purpose: 'Ruang peluang, modus konvergensi, hukum bilangan besar, limit pusat, harapan bersyarat, martingal, proses Markov/Poisson, dan gerak Brown.',
    outcome: 'Membaca literatur peluang modern dan proses stokastik dengan kefasihan teori ukuran.',
    corpus: '27 halaman semantik Random + QuantEcon — Continuous Time Markov Chains (100 hlm.) + 2 irisan laboratorium Žitković + penutupan asli',
    note: 'Arsitektur dibekukan tanpa teori renewal sebagai syarat kelulusan. Edisi publik sementara telah memuat 14 unit teori dan satu laboratorium; unit Markov berikutnya sedang menjalani QA. Korpus belum selesai.',
    edition: 'https://github.com/KokunoYumeto/measure-theoretic-probability-stochastic-processes-id'
  },
  {
    id: 'D40', ownerLane: 'O010', level: 'D', topic: 'Analisis', state: 'production',
    title: 'Persamaan Diferensial Parsial', prerequisites: ['B70', 'C110', 'D10', 'D20'],
    purpose: 'Persamaan orde satu dan dua klasik, distribusi, ruang Sobolev, solusi lemah, metode energi dan Fourier, serta titik kontak numerik.',
    outcome: 'Mengenali tipe PDP, membuktikan hasil dasar, dan membedakan solusi klasik, lemah, serta numerik.',
    corpus: 'Dionne — Partial Differential Equations lengkap + 7 simpul laboratorium FEniCSx + penutupan soal, asesmen, dan laboratorium asli',
    note: 'Arsitektur dibekukan. Dionne menjadi rangka teori wajib; FEniCSx menghubungkan formulasi lemah dengan komputasi. Enam unit Ivrii yang sudah diterima dipertahankan sebagai pembaca klasik opsional yang terpisah. Produksi belum selesai.'
  },
  {
    id: 'D50', ownerLane: 'O011', level: 'D', topic: 'Geometri & Topologi', state: 'production',
    title: 'Lipatan Mulus dan Geometri Diferensial', prerequisites: ['C90', 'B60', 'C30'],
    purpose: 'Lipatan, struktur tangen dan kotangen, bentuk diferensial, integrasi dan Stokes, grup Lie, metrik Riemann, koneksi, dan kelengkungan.',
    outcome: 'Menggunakan bahasa geometri bebas koordinat dan membuktikan hasil dasar tentang lipatan serta kelengkungan.',
    corpus: 'Brenner lengkap — 29 kuliah + 29 lembar kerja; dua jembatan asli grup Lie/de Rham; bank 10 ujian resmi',
    note: 'Arsitektur dipilih. Pembaca terpusat Unit 1–3 berjumlah 56 halaman dan telah lolos QA lokal; akses akun GitHub telah dipulihkan. Produksi berlanjut dari Unit 4, lalu dua jembatan CC BY-SA dan penutupan asesmen 38 butir.'
  },
  {
    id: 'D60', ownerLane: 'O012', level: 'D', topic: 'Geometri & Topologi', state: 'production',
    title: 'Topologi Aljabar', prerequisites: ['C90', 'C30'],
    purpose: 'Grup fundamental, ruang penutup, homologi simplisial/seluler, kohomologi, barisan eksak, derajat, dan metode homotopi terpilih.',
    outcome: 'Menerjemahkan pertanyaan geometri menjadi invarian aljabar yang dapat dihitung dan merekonstruksi bukti standar.',
    corpus: 'Roberts lengkap (30 kuliah) + jembatan homologi Fomberg §§1.1–1.13 + penutupan bukti, solusi, dan laboratorium asli',
    note: 'Arsitektur dibekukan. Edisi Roberts lengkap tetap 30 unit; jalur belajar 14 unit memetakannya ke jembatan homologi tanpa menghapus atau menomori ulang unit. Produksi Roberts sedang berjalan; setelah itu masuk jembatan Fomberg terbatas dan penutupan 108 soal tersolusi serta empat laboratorium.'
  },
  {
    id: 'D70', ownerLane: 'O013', level: 'D', topic: 'Aljabar', state: 'production',
    title: 'Aljabar Pascasarjana', prerequisites: ['C40', 'B40'],
    purpose: 'Modul, hasil kali tensor, barisan eksak, teori medan/Galois lanjut, aljabar komutatif, teori representasi, dan struktur untuk geometri/topologi.',
    outcome: 'Memasuki literatur aljabar pascasarjana dengan penguasaan konstruksi universal dan bukti struktural.',
    corpus: 'Li Jilid 1 lengkap + MIT OCW 18.712 lengkap + enam rentang CRing persis', note: 'Korpus terpilih dan digunakan oleh pemilik produksi.',
    edition: 'https://github.com/KokunoYumeto/metode-aljabar-jilid-1-id'
  },
  {
    id: 'D80', ownerLane: 'O014', level: 'D', topic: 'Aljabar', state: 'production',
    title: 'Teori Kategori dan Metode Homologis', prerequisites: ['C30', 'C80'],
    purpose: 'Kategori, funktor, transformasi natural, limit/kolimit, adjungsi, representabilitas, kategori abelian, kompleks rantai, funktor turunan, dan orientasi barisan spektral.',
    outcome: 'Menggunakan bahasa kategoris sebagai matematika kerja, bukan hiasan abstrak.',
    corpus: 'Li — Methods of Algebra Volume 2 lengkap', note: 'Korpus terpilih dan diakui; produksi unit sedang berjalan.'
  },
  {
    id: 'D90', ownerLane: 'O015', level: 'D', topic: 'Komputasi & Optimisasi', state: 'production',
    title: 'Optimisasi Lanjut dan Analisis Konveks', prerequisites: ['C110', 'C130', 'D20'],
    purpose: 'Himpunan dan fungsi konveks, separasi, dualitas, KKT, algoritma, metode nonsmooth, optimisasi stokastik, dan sudut pandang variasional.',
    outcome: 'Menganalisis masalah optimisasi kontinu dan algoritma modern melampaui program linear/integer.',
    corpus: 'MIT OCW 6.253 lengkap (395 halaman) + Royer Stochastic Gradient lengkap (45 halaman) + empat unit jembatan, empat laboratorium, dan penutupan solusi asli',
    note: 'Arsitektur dipilih. Pilot rekonstruksi semantik MIT wajib mendahului produksi massal; target penutupan sedikitnya 70 butir bersolusi lengkap. Edisi Penn–Habring yang sudah dihasilkan dipertahankan sebagai pendamping opsional, bukan dihitung ulang sebagai inti D90.',
    zenodo: 'https://doi.org/10.5281/zenodo.22059742'
  },
  {
    id: 'D100', ownerLane: 'O016', level: 'D', topic: 'Geometri & Topologi', state: 'production',
    title: 'Jembatan Geometri Aljabar', prerequisites: ['D70', 'D80', 'C90', 'D60'],
    purpose: 'Varietas afin/projektif, gelanggang koordinat, skema, sheaf, morfisme, dimensi, orientasi kohomologis, dan penggunaan terpandu Stacks Project.',
    outcome: 'Berpindah dari aljabar pascasarjana ke geometri aljabar tingkat sumber dan menavigasi korpus rujukan hidup.',
    corpus: 'Brenner Algebraische Kurven lengkap (337 halaman) + Bündel, Garben und Kohomologie lengkap (265 halaman) + penutupan penguasaan dan integrasi asli',
    note: 'Arsitektur dipilih. Unit 1–5 volume klasik sudah publik dalam pembaca 96 halaman. Seluruh dua volume diterjemahkan; jalur belajar menyorot 19 unit skema/kohomologi, sementara Stacks tetap rujukan hilir terpandu dan Napkin hanya donor penjelasan opsional.',
    zenodo: 'https://doi.org/10.5281/zenodo.22059687'
  },
  {
    id: 'D110', ownerLane: 'LEAN', level: 'D', topic: 'Praktik Riset', state: 'published',
    title: 'Matematika Terformalisasi dalam Lean', prerequisites: ['B10', 'B40', 'C10', 'C30'],
    purpose: 'Sintaks dan taktik Lean, proposisi dan bukti, himpunan/fungsi, struktur aljabar, contoh topologi/analisis, dan navigasi pustaka.',
    outcome: 'Mengodekan dan memverifikasi matematika nontrivial serta menyumbangkan koreksi atau contoh berbatas.',
    corpus: 'Mathematics in Lean — korpus Lean 4 lengkap',
    note: 'Edisi Bahasa Indonesia v4.30.0-id.3 lengkap dan terverifikasi publik: 219 halaman, 10.978 rekaman backend, build Lean lulus, dan QA terminologi Indonesia berbasis arXiv tercatat.',
    edition: 'https://zenodo.org/records/22062017/files/matematika-dalam-lean-bahasa-indonesia.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/mathematics-in-lean-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22062017'
  },
  {
    id: 'D120', ownerLane: 'O017', level: 'D', topic: 'Praktik Riset', state: 'production',
    title: 'Membaca Riset, Eksposisi, dan Kerja Matematis Reprodusibel', prerequisites: ['C20', 'C40', 'B80'],
    purpose: 'Membaca artikel dan monograf, rekonstruksi sumber, sitasi, tulisan ekspositoris, catatan seminar, errata, komputasi reprodusibel, kritik sejawat, dan proyek kontribusi.',
    outcome: 'Berpartisipasi secara konstruktif dalam komunitas matematika sambil menyatakan dependensi, bukti, dan ketidakpastian secara tepat.',
    corpus: 'Kerja Matematika yang Dapat Ditelusuri — rangka asli sembilan unit + donor metodologis Turing Way/PyRSE yang dibekukan',
    note: 'Korpus dipilih dan edisi mandiri 128 halaman sudah publik. Lapisan autentik seminar, penelaahan independen, sumber nyata, kontribusi terbatas, serta backend asesmen masih harus diselesaikan; paketnya sudah dikirim ke pemilik yang sama.',
    edition: 'https://zenodo.org/records/22051978/files/kerja-matematika-yang-dapat-ditelusuri-id-2026.08.22.pdf?download=1',
    repository: 'https://github.com/KokunoYumeto/kerja-matematika-yang-dapat-ditelusuri-id',
    zenodo: 'https://doi.org/10.5281/zenodo.22051978'
  }
];

export const topics = [
  'Fondasi & Kalkulus',
  'Analisis',
  'Aljabar',
  'Geometri & Topologi',
  'Peluang & Statistika',
  'Diskrit & Logika',
  'Komputasi & Optimisasi',
  'Praktik Riset'
];

export const program = Object.freeze({
  id: 'program-matematika-indonesia',
  title: 'Program Matematika Indonesia — Peta Kurikulum Terbuka',
  language: 'id-ID',
  version: '0.45.0',
  snapshotDate: '2026-08-23',
  totalCourseRoles: 40,
  selectedCorpusRoles: 40,
  unresolvedRoleIds: [],
  completedPublicCourseRoleIds: ['B10', 'B80', 'B90', 'C30', 'C40', 'C60', 'C70', 'C80', 'C110', 'D110'],
  completedPublicRecordDois: [
    '10.5281/zenodo.22060439',
    '10.5281/zenodo.22053905',
    '10.5281/zenodo.22062144',
    '10.5281/zenodo.22062449',
    '10.5281/zenodo.22052196',
    '10.5281/zenodo.22062005',
    '10.5281/zenodo.21932787',
    '10.5281/zenodo.22054086',
    '10.5281/zenodo.22062017'
  ],
  zenodo: 'https://doi.org/10.5281/zenodo.22063205',
  zenodoConcept: 'https://doi.org/10.5281/zenodo.22059707',
  provenance: {
    model: 'OpenAI Codex gpt-5.6-sol, Ultra',
    role: 'Koordinasi, rekayasa backend, dan penerbitan snapshot pusat atas instruksi pengguna; kredit sumber dan kontributor tetap melekat pada setiap komponen.'
  },
  backend: {
    schemaVersion: '1.0.0',
    status: 'validated',
    centralRecordCount: 2122,
    completeCorpusMigrations: [
      {
        corpus: 'Discrete Mathematics: An Open Introduction 4 — Bahasa Indonesia',
        recordCount: 163583,
        result: 'lossless-zero-copy-pass'
      },
      {
        corpus: 'Komputasi Matematis dan Eksperimen yang Dapat Direproduksi — Bahasa Indonesia',
        recordCount: 339,
        result: 'lossless-zero-copy-one-to-one-native-catalog-adapter-pass'
      },
      {
        corpus: 'Open Logic Project — OLP-0722, Bahasa Indonesia',
        recordCount: 6522,
        result: 'deterministic-zero-copy-pass'
      },
      {
        corpus: 'Judson — Abstract Algebra: Theory and Applications, Bahasa Indonesia',
        recordCount: 36978,
        result: 'additive-zero-copy-pass'
      },
      {
        corpus: 'Yet Another Introductory Number Theory Textbook, Bahasa Indonesia',
        recordCount: 6967,
        result: 'lossless-additive-adapter-pass'
      },
      {
        corpus: 'Keller–Trotter — Applied Combinatorics, Bahasa Indonesia',
        recordCount: 19049,
        result: 'lossless-additive-one-common-record-per-native-record-pass'
      },
      {
        corpus: 'Mathematics in Lean — Bahasa Indonesia v4.30.0-id.3',
        recordCount: 10978,
        result: 'lossless-zero-copy-one-to-one-pass'
      }
    ],
    schema: 'https://zenodo.org/records/22063205/files/interlanguage-math-backend-v1.schema.json?download=1',
    sourceFormatProfile: 'https://zenodo.org/records/22063205/files/interlanguage-source-format-profile-v1.schema.json?download=1',
    package: 'https://zenodo.org/records/22063205/files/program-matematika-indonesia-backend-v1-v0.45.0.zip?download=1'
  },
  repositories: {
    github: {
      url: 'https://github.com/KokunoYumeto/program-matematika-indonesia',
      status: 'available',
      lastConfirmedAt: '2026-08-22'
    }
  },
  status: 'in-progress'
});
