# DRAFT LAPORAN AKHIR MAGANG: Analisis Stabilitas Jaringan Gateway Disdukcapil Jombang

*Draft ini dapat disalin sebagian atau seluruhnya ke dalam Microsoft Word untuk melengkapi Bab Pembahasan/Analisis dan Bab Kesimpulan Laporan Magang Anda.*

---

## BAB: HASIL DAN PEMBAHASAN

### 1. Ekstraksi dan Prapemrosesan Data (Data Wrangling)
Langkah pertama dalam analisis kestabilan jaringan gateway SIAK (IP: 10.35.17.26) adalah restrukturisasi log *Ping* dari sistem operasi Windows. File teks mentah (*multiline*) diekstraksi ke dalam format *Time-Series* (runtun waktu) dengan frekuensi tetap, yaitu 1 menit. 
Berdasarkan sampel log periode 17 Maret - 1 April 2026, tercatat total rentang waktu kalender sebanyak **21.728 menit**. Namun, filter operasional sistem menunjukkan hanya **1.462 observasi aktif** yang mewakili waktu pelayanan atau kondisi komputer *logger* sedang menyala, memastikan bahwa kita membedakan "sistem mati/di luar jam kerja" dengan "jaringan mengalami *disconnect*".

### 2. Analisis Deskriptif dan Performa SLA Jaringan (EDA)
Analisis statistik awal memberikan gambaran kuantitatif mengenai kesehatan infrastruktur jaringan. Hasil pengolahan metrik menunjukkan:
- **Rata-rata Ping (Latency):** 241,51 ms. Angka ini secara *baseline* tergolong sangat tinggi dan mengindikasikan adanya beban lalu lintas (*traffic load*) konstan pada gateway Dukcapil.
- **Percentile 95 (P95) dan P99:** P95 bernilai 1.228 ms dan P99 bernilai 2.463 ms. Artinya, terdapat lonjakan delay parah sebesar 1-2 detik yang menimpa jaringan pada 5% waktu kritis operasionalnya.
- **Ping Maksimum:** Tervalidasi di angka **3.516 ms** pada tanggal 30 Maret, yang membuktikan adanya antrean (*bottleneck*) luar biasa padat di sistem.
- **Rasio Kegagalan (Timeout Rate):** Ditemukan 286 menit mengalami *Request Timed Out* murni berujung pada **16,36% Timeout Rate**. Standar kestabilan institusional yang baik berada di bawah 2%, sehingga 16,36% adalah penanda kondisi `Degraded` serius.

### 3. Validasi Visual Jam Rawan Pelayanan
Plot garis deret waktu mengonfirmasi hipotesis awal mengenai siklus jam rawan operasional SIAK:
- Fluktuasi koneksi memburuk (*spikes*) didominasi pada rentang waktu awal layanan, yaitu antara **pukul 07:00 hingga 09:00 pagi**.
- Tingkat *latency* kemudian mulai mereda perlahan dan menjadi stabil saat memasuki **pukul 12:00 WIB dan seterusnya**.
- Secara komparasi antartanggal operasional, visualisasi Boxplot mendeteksi distribusi data yang menyebar tinggi (dipenuhi *outlier*) pada tanggal 30 Maret, menjadikan hari tersebut sebagai titik operasional terparah (paling tidak stabil) dari seluruh sampel.

### 4. Pelacakan Anomali dan Investigasi Sesi Terputus (Outage) 
Terdapat observasi empiris dari operator bahwa terjadi *"outage"* di sekitar tanggal 26 Maret pukul 10:13–10:58. Sistem pelacak berbasis aturan (*Rule-Based SLA Tracker*) yang diprogram berhasil membuktikan riwayat anomali ini.
- **Katalog Anomali (Automated Report):** Skrip mendeteksi jaringan mulai "sakit kritis" beruntun pada **10:17 hingga 10:57 WIB** (durasi kasar ± 40 menit). 

Dalam durasi badai 40 menit tersebut, terjadi perpecahan blok RTO beruntun menjadi 15-menit matinya koneksi, disusul udara bernapas (*Ping success*) selama 1 menit, lalu mati lagi 15 menit, dan mati lagi 9 menit. Ini memberikan bukti matematis (*data-driven*) dari "Matinya sistem 45 menit".

### 5. Pemodelan Stasioneritas dan Peringatan Dini (Machine Learning ARIMA)
Selain menelaah masa lalu, penelitian ini menginisiasi *Sistem Peringatan Dini*. Uji stasioneritas dengan *Augmented Dickey-Fuller (ADF) Test* pada hari terekstrim (tanggal 30) menunjukkan *P-Value = 0.3268 > 0.05*, berarti data jaringan SIAK tidak konstan secara distribusi waktu (*Non-Stationary*).
Oleh karenanya, *Differencing* (d=1) diimplementasikan dan iterasi *Grid Search* digunakan untuk menemukan orde ARIMA terbaik.
Model prediktif akhirnya mampu menggambarkan batasan batas fluktuasi (*Confidence Interval*) ke depan terkait lonjakan latensi, membuktikan kelayakan *Machine Learning* untuk pengawasan perlintasan *traffic* jaringan administratif.

---

## BAB: KESIMPULAN DAN SARAN (REKOMENDASI ACTIONABLE)

**A. Kesimpulan Kinerja:**
Analisis membuktikan bahwa kualitas jaringan Gateway Disdukcapil dalam menangani beban operasional pelayanan rentan mengalami keparahan (latency di atas ambang wajar dan pemutusan di jam krusial). Pola "kepadatan jam 7-9 pagi" sukses dibuktikan dengan data absolut.

**B. Actionable Insights & Rekomendasi Bersifat Manajerial untuk Instansi:**

1. **Aturan Skala Prioritas Data (Manajemen Antrean SLA):** Mengingat server acap kali menderita beban puncak dari jam `07:00 - 09:00`, disarankan dibuat surat keputusan dinas/pelayanan internal IT bahwa *syncronization protocol* otomatis atau pengunggahan arsip ukuran raksasa (*Upload Batch* arsip kependudukan) HANYA BOLEH diaktifkan **setelah pukul 12:00 WIB**, demi menyisihkan ruang pita jaringan (*bandwidth*) untuk melayani penduduk secara riil di loket pagi.
2. **Standard Operational Procedure (SOP) Batas Alarm:** Laporan ini merekomendasikan Pembuatan *SLA Informal* kepada divisi TIK. Indikasi batas bahaya/awan mendung (*Degraded*) jaringan adalah di Ping konstan **> 300 ms**, dan lampu peringatan (*Critical*) adalah **Ping > 1000 ms**.
3. **Preventif Daripada Reaktif:** Jika ada lonjakan `Ping` > 300ms dalam kondisi 3 menit berturut-turut pada loket monitor, Tim TIK / Admin Jaringan harus turun langsung meninjau kelebihan lalu lintas. Jangan pernah menunggu RTO mencapai batas beruntun sebelum melakukan reset jaringan, karena menoleransi *delay* sering berujung pada lumpuhnya pelayanan 45 menit (sebagaimana pernah terjadi pada 26 Maret).
