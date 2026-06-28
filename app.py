import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman (Harus dilakukan pertama kali)
st.set_page_config(page_title="Dashboard Jaringan SIAK", page_icon="📡", layout="wide")

# Fungsi untuk menyematkan background image lokal
import base64
import os

def set_bg_image():
    bg_file = "backround.jpeg"
    if os.path.exists(bg_file):
        with open(bg_file, "rb") as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Membuat container utama semi-transparan agar konten mudah dibaca */
        [data-testid="stAppViewBlockContainer"] {{
            background-color: rgba(255, 255, 255, 0.92);
            padding: 2.5rem 3rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        
        /* Membuat sidebar semi-transparan */
        [data-testid="stSidebar"] > div:first-child {{
            background-color: rgba(240, 242, 246, 0.95);
        }}
        
        /* Membuat stHeader (bagian atas) transparan */
        [data-testid="stHeader"] {{
            background: rgba(0, 0, 0, 0);
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

# Panggil fungsi background
set_bg_image()

st.title("📡 Dashboard Stabilitas Jaringan Gateway Disdukcapil Jombang")
st.markdown("Aplikasi web ini memantau secara interaktif riwayat kestabilan jaringan pada IP `1*.**.**.*6`.")

# Load Data dengan Caching untuk optimasi
@st.cache_data
def load_data():
    # Load dataset hasil klasifikasi
    df = pd.read_csv("Laporan_Stabilitas_Jaringan_SIAK.csv")
    
    # Konversi kolom timestamp agar format waktu dikenali oleh grafik
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Ekstrak tanggal (date) untuk filter sidebar
    df['date'] = df['timestamp'].dt.date
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'Laporan_Stabilitas_Jaringan_SIAK.csv' tidak ditemukan di direktori saat ini.")
    st.stop()

# --- SIDEBAR (Filter Menu) ---
st.sidebar.header("Menu Filter")

# Pilihan Tanggal
tgl_list = ["Semua Tanggal"] + sorted(df['date'].unique().tolist())
tgl_pilihan = st.sidebar.selectbox("Pilih Rentang Laporan:", tgl_list)

# Melakukan filter data sesuai kalender yang dipilih
if tgl_pilihan == "Semua Tanggal":
    df_filtered = df.copy()
else:
    df_filtered = df[df['date'] == tgl_pilihan]

# --- KPI METRICS (Highlight Informasi) ---
st.subheader("📊 Indikator Kinerja Jaringan (SLA)")

col1, col2, col3, col4 = st.columns(4)

total_request = len(df_filtered)
avg_ping = df_filtered['ping_ms'].mean()
total_timeout = df_filtered['is_timeout'].sum()
timeout_rate = (total_timeout / total_request) * 100 if total_request > 0 else 0

col1.metric("Total Waktu Terekam", f"{total_request} mnt")
col2.metric("Rata-rata Latensi (Ping)", f"{avg_ping:.1f} ms" if pd.notna(avg_ping) else "N/A")
col3.metric("Total Timeout / Putus", f"{total_timeout} kali/menit")
col4.metric("Timeout Rate (RTO)", f"{timeout_rate:.2f} %")

# --- VISUALISASI UTAMA: TIME SERIES LINE CHART ---
st.markdown("---")
st.subheader("📈 Riwayat Pergerakan Latensi (Ping)")

# Menggunakan Plotly Line Chart untuk grafik interaktif
fig_ping = px.line(
    df_filtered, 
    x='timestamp', 
    y='ping_ms', 
    title=f"Grafik Fluktuasi Ping (ms) - {'Semua Tanggal' if tgl_pilihan == 'Semua Tanggal' else tgl_pilihan}",
    labels={"timestamp": "Waktu (Jam)", "ping_ms": "Ping (Mili Detik)"},
    markers=True
)

# Menambahkan garis batas (Ambang Batas)
fig_ping.add_hline(y=300, line_dash="dash", line_color="orange", annotation_text="Batas Rawan (>300ms)")
fig_ping.add_hline(y=1000, line_dash="dash", line_color="red", annotation_text="Batas Kritis (>1000ms)")

# Menyesuaikan tinggi grafik
fig_ping.update_layout(height=400)

st.plotly_chart(fig_ping, use_container_width=True)


# --- VISUALISASI KEDUA: DISTRIBUSI SEVERITY & TIMEOUT ---
st.markdown("---")
col_pie, col_bar = st.columns([1, 1])

with col_pie:
    st.subheader("🗂 Status Keparahan Jaringan")
    severity_counts = df_filtered['severity_label'].value_counts().reset_index()
    severity_counts.columns = ['Severity Label', 'Jumlah Menit']
    
    # Donut Chart Perbandingan Waktu Sehat vs Kritis
    fig_pie = px.pie(
        severity_counts, 
        names='Severity Label', 
        values='Jumlah Menit',
        hole=0.4,
        color='Severity Label',
        color_discrete_map={
            'Good': 'green',
            'Degraded': 'orange',
            'Critical': 'red',
            'Outage / Sesi Down': 'black'
        }
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    st.subheader("🔥 Kejadian Timeout (RTO) per Jam")
    # Jika hanya ada satu tanggal, ini terlihat jam ke jam. 
    # Jika 'Semua Tanggal', ini akan mengagregasi total timeout di jam operasional tersebut.
    timeout_per_hour = df_filtered.groupby('hour')['is_timeout'].sum().reset_index()
    
    # Bar chart distribusi Timeout
    fig_bar = px.bar(
        timeout_per_hour, 
        x='hour', 
        y='is_timeout', 
        labels={"hour": "Jam (24-H Format)", "is_timeout": "Total Menit Timeout"},
        color='is_timeout',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.subheader("⏱️ Median (Kondisi Tipikal Asli) Ping per Jam")
st.markdown("Kalkulasi ini menggunakan **Median** (Nilai Tengah), bukan Rata-Rata biasa (Mean). Tujuannya agar hitungan **kebal terhadap anomali sesaat (Outlier)**. \n> *Kasus: Jika 5 menit ping lancar 20ms tapi ada satu detik melonjak 3000ms lalu normal lagi, maka hitungan Rata-Rata biasa akan bias menjadi seolah seluruh jamnya rusak. Dengan menggunakan Median, angkanya akan tetap jujur menjabarkan kondisi jaringan SIAK yang sebenarnya (berkisar 20ms).*")

median_per_hour = df_filtered.groupby('hour')['ping_ms'].median().reset_index()

fig_median_bar = px.bar(
    median_per_hour,
    x='hour',
    y='ping_ms',
    labels={'hour': 'Jam Operasional (24-H Format)', 'ping_ms': 'Median Latensi (Mili Detik)'},
    color='ping_ms',
    color_continuous_scale='Teal'
)
st.plotly_chart(fig_median_bar, use_container_width=True)

st.markdown("---")
st.subheader("📦 Distribusi Variasi Latensi (Ping) per Jam")
st.markdown("Visualisasi *Boxplot* ini mengadaptasi hasil analisis di `code.ipynb`. Kotak yang lebih panjang menunjukkan bahwa pada jam tersebut, latensi jaringan lebih fluktuatif dan kurang stabil.")
# Menggunakan Plotly Boxplot
fig_box = px.box(
    df_filtered,
    x='hour',
    y='ping_ms',
    labels={"hour": "Jam Operasional (24-H Format)", "ping_ms": "Ping (Mili Detik)"},
    color="hour"
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)


if tgl_pilihan == "Semua Tanggal":
    st.markdown("---")
    st.subheader("🗓️ Heatmap Kepadatan Area Rawan (Timeout)")
    st.markdown("Memetakan secara spesifik relasi **Hari vs Jam** terjadinya *Timeout*. (Warna merah semakin pekat menandakan jam tersebut adalah daerah paling rawan *outage*).")
    
    # Agregasi data untuk pembuatan Heatmap
    heatmap_data = df_filtered.pivot_table(index='day_of_week', columns='hour', values='is_timeout', aggfunc='sum').fillna(0)
    
    # Konversi indeks (0-6) menjadi Nama Hari 
    day_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
    heatmap_data.index = heatmap_data.index.map(day_map)
    
    # Menggunakan Plotly Imshow (Heatmap)
    fig_heat = px.imshow(
        heatmap_data, 
        labels=dict(x="Jam Operasional", y="Hari", color="Total Menit Timeout"),
        x=heatmap_data.columns,
        y=heatmap_data.index,
        color_continuous_scale="Reds",
        aspect="auto"
    )
    st.plotly_chart(fig_heat, use_container_width=True)

st.caption("Dikembangkan sebagai Modul Tambahan Analisis Gateway Sistem SIAK - Disdukcapil Jombang.")
