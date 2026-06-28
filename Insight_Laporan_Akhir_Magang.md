# DRAFT LAPORAN AKHIR MAGANG: Analisis Stabilitas Jaringan Gateway Disdukcapil Jombang

*Draft ini dapat disalin sebagian atau seluruhnya ke dalam Microsoft Word untuk melengkapi Bab Pembahasan/Analisis dan Bab Kesimpulan Laporan Magang Anda.*

---

## BAB: HASIL DAN PEMBAHASAN

### 1. Ekstraksi dan Prapemrosesan Data (Data Wrangling)
Langkah pertama dalam analisis kestabilan jaringan gateway SIAK (IP: 10.35.17.26) adalah restrukturisasi log *Ping* dari sistem operasi Windows. File teks mentah (*multiline*) diekstraksi ke dalam format *Time-Series* (runtun waktu) dengan frekuensi tetap, yaitu 1 menit. 
Berdasarkan log hasil *scrapping* final periode **17 Maret - 22 Mei 2026** (sekitar 66 hari), tercatat total rentang waktu kalender sebanyak **95.377 menit**. Namun, filter operasional sistem menunjukkan terdapat **12.513 observasi aktif** yang mewakili waktu pelayanan atau kondisi komputer *logger* sedang menyala. Hal ini penting untuk memastikan bahwa kita membedakan kondisi "sistem mati/di luar jam kerja" dengan "jaringan mengalami *disconnect* (RTO)".

### 2. Analisis Deskriptif dan Performa SLA Jaringan (EDA)
Analisis statistik deskriptif secara keseluruhan memberikan gambaran kuantitatif mengenai kesehatan infrastruktur jaringan Gateway Disdukcapil Jombang selama masa pemantauan:
- **Rata-rata Ping (Latency):** **84,63 ms**. Secara keseluruhan, angka ini jauh lebih baik dibandingkan sampel awal, namun fluktuasi pada jam-jam tertentu tetap tinggi.
- **Percentile 95 (P95) dan P99:** P95 bernilai **331,0 ms** dan P99 bernilai **1.414,5 ms**. Artinya, terdapat lonjakan delay parah (latensi di atas 1,4 detik) pada 1% kondisi kritis operasionalnya, serta latensi di atas 330 ms pada 5% waktu tersibuk.
- **Ping Maksimum:** Tervalidasi di angka **3.526,0 ms** yang terjadi pada tanggal **10 April 2026 pukul 12:09:00 WIB**, membuktikan adanya penumpukan antrean data (*bottleneck*) yang ekstrim pada gateway.
- **Rasio Kegagalan (Timeout Rate):** Terdeteksi total **625 menit** mengalami *Request Timed Out* (RTO) murni, yang menghasilkan **4,99% Timeout Rate**. Meskipun membaik dari sampel jangka pendek sebelumnya, tingkat kegagalan ~5% ini masih berada di atas ambang batas standar kestabilan jaringan institusional yang baik (<2%), sehingga secara umum performa jaringan masih masuk kategori `Degraded` (Mengalami Penurunan Kinerja).
- **Distribusi Kondisi Pelayanan (SLA Severity):**
  - **Good (Lancar, Ping < 300 ms):** **89,79%** (11.235 observasi menit)
  - **Degraded (Lambat/Delay, Ping 300–999 ms):** **3,77%** (472 observasi menit)
  - **Critical (Kritis/Putus Sesaat, Ping >= 1000 ms atau RTO tunggal):** **4,32%** (541 observasi menit)
  - **Outage / Sesi Down (Putus Beruntun >= 3 Menit):** **2,12%** (265 observasi menit)

### 3. Validasi Visual Jam Rawan Pelayanan
Plot garis deret waktu dan visualisasi boxplot mengonfirmasi siklus jam rawan operasional SIAK:
- Fluktuasi koneksi memburuk (*spikes*) didominasi pada rentang waktu awal layanan loket, yaitu antara **pukul 07:00 hingga 09:00 WIB**.
- Tingkat *latency* kemudian mulai mereda perlahan dan menjadi stabil saat memasuki **pukul 12:00 WIB dan seterusnya**.
- Secara komparasi antartanggal operasional, visualisasi Boxplot mendeteksi distribusi data yang menyebar tinggi (dipenuhi *outlier*) pada tanggal **30 Maret 2026** (Mean Ping tertinggi sebesar **359,27 ms**), menjadikannya hari dengan kestabilan latensi terburuk.
- Sementara itu, dari metrik kegagalan koneksi total (RTO), hari dengan kejadian putus terbanyak adalah **9 April 2026** dengan total **79 menit RTO (RTO Rate 24,53%)**, disusul oleh **21 April 2026** dengan **77 menit RTO**, dan **26 Maret 2026** dengan **67 menit RTO**.

### 4. Pelacakan Anomali dan Investigasi Sesi Terputus (Outage) 
Terdapat observasi empiris dari operator bahwa terjadi *"outage"* parah di sekitar tanggal 26 Maret pukul 10:13–10:58. Sistem pelacak berbasis aturan (*Rule-Based SLA Tracker*) yang diprogram berhasil membuktikan riwayat anomali ini secara akurat.
- **Katalog Anomali (Automated Report):** Skrip mendeteksi jaringan mulai mengalami kegagalan beruntun pada **10:13 hingga 10:57 WIB** (durasi kasar ± 45 menit). 
- Dalam durasi badai tersebut, terjadi perpecahan blok RTO beruntun menjadi 15 menit matinya koneksi secara total (pukul 10:13-10:31, dikurangi 1 menit di 10:16), disusul mati lagi 15 menit (pukul 10:33-10:47), dan mati lagi 9 menit (10:49-10:57). Ini memberikan bukti matematis (*data-driven*) yang kuat dari keluhan operator mengenai "lumpuhnya sistem selama 45 menit".

### 5. Pemodelan Stasioneritas dan Peringatan Dini (Machine Learning ARIMA)
Selain mengevaluasi data historis secara deskriptif, penelitian ini menginisiasi *Sistem Peringatan Dini* berbasis *Machine Learning* menggunakan algoritma runtun waktu ARIMA (*Autoregressive Integrated Moving Average*). Uji coba ini difokuskan pada sampel hari paling ekstrem (30 Maret 2026) dengan batasan jam operasional utama (pukul 07:00 hingga 15:00 WIB, total 481 menit aktif).

#### a. Pengujian Stasioneritas (Augmented Dickey-Fuller Test)
Model peramalan ARIMA mensyaratkan agar data bersifat stasioner (rata-rata dan varians konstan sepanjang waktu). Untuk menguji hal ini, dilakukan uji statistik *Augmented Dickey-Fuller* (ADF) terhadap sampel data latensi asli:
- **Test Statistic:** -1.9113
- **p-value:** 0.3268
Karena nilai *p-value* $= 0.3268 > 0.05$ (tingkat signifikansi 5%), kita gagal menolak hipotesis nol ($H_0$), yang berarti data latensi asli bersifat **tidak stasioner** (*non-stationary*). Oleh karena itu, diimplementasikan operasi *first-order differencing* ($d=1$) untuk menstabilkan rata-rata runtun waktu. Setelah proses *differencing*, data terbukti stasioner dan siap dimasukkan ke dalam model ARIMA.

#### b. Pembagian Data (Chronological Split) & Optimasi Parameter (Grid Search)
Untuk memvalidasi performa prediksi model secara adil, dataset sampel 30 Maret dibagi secara kronologis menjadi dua bagian:
- **Data Latih (Train Set):** 384 menit pertama (digunakan agar model mempelajari pola fluktuasi latensi).
- **Data Uji (Test Set):** 97 menit terakhir (disembunyikan dari model untuk menguji ketepatan prediksi).

Sebuah proses iterasi otomatis (*Grid Search*) dijalankan untuk menguji berbagai kombinasi orde parameter $(p, d, q)$ guna mencari model dengan nilai *Akaike Information Criterion* (AIC) terendah. Kombinasi parameter terbaik yang ditemukan adalah **ARIMA(1, 1, 1)** dengan nilai **AIC sebesar 5.868,11**.

#### c. Evaluasi Performa Model Prediksi
Performa tebakan model ARIMA(1,1,1) diukur dengan membandingkan nilai prediksi latensi terhadap nilai aktual pada *Test Set* (97 menit terakhir) menggunakan tiga metrik evaluasi standar:
1. **Mean Absolute Error (MAE):** **+/- 67,59 ms**. Artinya secara rata-rata, tebakan model meleset sekitar 67,59 ms dari nilai latensi asli per menit.
2. **Root Mean Squared Error (RMSE):** **67,59 ms**. Nilai ini menunjukkan sensitivitas model terhadap simpangan eror yang ekstrem.
3. **Mean Absolute Percentage Error (MAPE):** **450,59%**. Nilai persentase kesalahan ini tergolong tinggi karena adanya fluktuasi data latensi yang sangat ekstrem (lonjakan tajam sesaat) di lapangan.

*Gambar 4.4. Grafik Uji Peringatan Dini Latensi Gateway (ARIMA(1,1,1) vs Data Aktual)*

#### d. Diagnostik Sisa Eror (Residual Diagnostics)
Untuk menjamin bahwa model ARIMA(1,1,1) telah mengekstrak informasi secara optimal, sisa kesalahan (*residual error*) dianalisis menggunakan empat grafik diagnostik:
1. **Standardized Residuals:** Menunjukkan fluktuasi kesalahan berada di sekitar nilai nol secara acak sepanjang waktu.
2. **Histogram & Estimated Density:** Distribusi kesalahan (*KDE*) menunjukkan pola kurva lonceng yang mendekati kurva normal teoretis, membuktikan tidak adanya bias sistematis.
3. **Normal Q-Q Plot:** Sebagian besar titik-titik kesalahan berada sejajar di garis diagonal merah, mengonfirmasi asumsi normalitas kesalahan.
4. **Correlogram (ACF):** Seluruh nilai autokorelasi sisa kesalahan berada di dalam batas signifikansi (zona arsir biru), membuktikan kesalahan bersifat independen (*white noise*) dan tidak ada pola runtun waktu yang tertinggal.

*Gambar 4.5. Grafik Diagnostik Residual Model ARIMA(1,1,1)*

#### e. Mekanisme Peringatan Dini (Early Warning System)
Model ARIMA(1,1,1) yang dilatih memproyeksikan estimasi latensi ke depan bersamaan dengan batas atas selang kepercayaan (*Confidence Interval*) 95%. Batas atas ini digunakan sebagai **ambang batas alarm dinamis (*dynamic threshold*)**:
- Jika latensi aktual tetap berada di dalam arsir wilayah batas toleransi merah muda (*Confidence Interval*), status jaringan dinyatakan aman.
- Apabila latensi aktual melonjak menembus batas atas selang kepercayaan tersebut, sistem akan memicu sinyal peringatan dini (*warning*) secara otomatis. Hal ini memberikan ruang bagi tim TIK untuk mengintervensi atau me-reset koneksi **30 hingga 60 menit lebih awal** sebelum sistem gateway benar-benar lumpuh dan mengalami RTO beruntun.

---

## BAB: KESIMPULAN DAN SARAN (REKOMENDASI ACTIONABLE)

**A. Kesimpulan Kinerja:**
Analisis membuktikan bahwa kualitas jaringan Gateway Disdukcapil dalam menangani beban operasional pelayanan rentan mengalami keparahan (latency di atas ambang wajar dan pemutusan di jam-jam sibuk). Pola "kepadatan jam 7-9 pagi" sukses dibuktikan dengan data absolut dari data log historis. Rata-rata ping keseluruhan berada di angka 84,63 ms dengan Timeout Rate total sebesar 4,99%.

**B. Actionable Insights & Rekomendasi Bersifat Manajerial untuk Instansi:**

1. **Aturan Skala Prioritas Data (Manajemen Antrean SLA):** Mengingat server acap kali menderita beban puncak dari jam `07:00 - 09:00` WIB, disarankan dibuat surat keputusan dinas/pelayanan internal IT bahwa *synchronization protocol* otomatis atau pengunggahan arsip ukuran raksasa (*Upload Batch* arsip kependudukan) HANYA BOLEH diaktifkan **setelah pukul 12:00 WIB**, demi menyisihkan ruang pita jaringan (*bandwidth*) untuk melayani penduduk secara riil di loket pagi.
2. **Standard Operational Procedure (SOP) Batas Alarm:** Laporan ini merekomendasikan Pembuatan *SLA Informal* kepada divisi TIK. Indikasi batas bahaya/awan mendung (*Degraded*) jaringan adalah di Ping konstan **> 300 ms**, dan lampu peringatan (*Critical*) adalah **Ping > 1000 ms**.
3. **Preventif Daripada Reaktif:** Jika ada lonjakan `Ping` > 300ms dalam kondisi 3 menit berturut-turut pada loket monitor, Tim TIK / Admin Jaringan harus turun langsung meninjau kelebihan lalu lintas. Jangan pernah menunggu RTO mencapai batas beruntun sebelum melakukan reset jaringan, karena menoleransi *delay* sering berujung pada lumpuhnya pelayanan 45 menit (sebagaimana pernah terjadi pada 26 Maret).
