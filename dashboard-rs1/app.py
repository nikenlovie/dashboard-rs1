import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

# -----------------------------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Analitik Rekam Medis & RS",
    layout="wide"
)

st.title("📊 Dashboard Analitik Manajemen Rekam Medis & RS")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. FUNGSI PERHITUNGAN INDIKATOR EFISIENSI BANSET (BOR, LOS, TOI, BTO)
# -----------------------------------------------------------------------------
def hitung_indikator_bor(hari_perawatan, tempat_tidur, periode_hari):
    bor = (hari_perawatan / (tempat_tidur * periode_hari)) * 100
    los = hari_perawatan / jumlah_pasien_keluar if jumlah_pasien_keluar > 0 else 0
    toi = ((tempat_tidur * periode_hari) - hari_perawatan) / jumlah_pasien_keluar if jumlah_pasien_keluar > 0 else 0
    bto = jumlah_pasien_keluar / tempat_tidur if tempat_tidur > 0 else 0
    return bor, los, toi, bto

# -----------------------------------------------------------------------------
# 3. SIDEBAR & NAVIGASI
# -----------------------------------------------------------------------------
st.sidebar.header("Filter & Navigasi")
menu = st.sidebar.radio(
    "Pilih Modul Analisis:",
    [
        "Efisiensi Bangsal (BOR/LOS/TOI/BTO)",
        "Volume Kunjungan & Audit Berkas",
        "Peta Persebaran Pasien (Kecamatan)",
        "Abstraksi Koding Penyakit",
        "Insiden Keselamatan Pasien (IKP)"
    ]
)

# -----------------------------------------------------------------------------
# MODUL 1: INDIKATOR BOR, LOS, TOI, BTO
# -----------------------------------------------------------------------------
if menu == "Efisiensi Bangsal (BOR/LOS/TOI/BTO)":
    st.subheader("📈 Analisis Efisiensi Tempat Tidur (Barber Johnson Indicators)")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        tt = st.number_input("Jumlah Tempat Tidur (TT)", value=100)
    with col2:
        hp = st.number_input("Jumlah Hari Perawatan", value=2100)
    with col3:
        jumlah_pasien_keluar = st.number_input("Pasien Keluar (Hidup + Mati)", value=500)
    with col4:
        periode = st.number_input("Periode (Hari)", value=30)

    bor, los, toi, bto = hitung_indikator_bor(hp, tt, periode)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("BOR (Bed Occupancy Rate)", f"{bor:.2f} %", delta="Ideal: 60-85%")
    c2.metric("AVLOS (Average Length of Stay)", f"{los:.2f} Hari", delta="Ideal: 6-9 Hari")
    c3.metric("TOI (Turn Over Interval)", f"{toi:.2f} Hari", delta="Ideal: 1-3 Hari")
    c4.metric("BTO (Bed Turn Over)", f"{bto:.2f} Kali", delta="Ideal: 40-50 Kali/Thn")

# -----------------------------------------------------------------------------
# MODUL 2: VOLUME KUNJUNGAN & AUDIT KELENGKAPAN BERKAS
# -----------------------------------------------------------------------------
elif menu == "Volume Kunjungan & Audit Berkas":
    st.subheader("📑 Volume Berkas & Audit Kelengkapi BRM")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Jumlah Berkas RM")
        data_kunjungan = pd.DataFrame({
            "Jenis Pelayanan": ["Rawat Jalan", "Rawat Inap"],
            "Jumlah Berkas": [4500, 1200]
        })
        st.bar_chart(data_kunjungan.set_index("Jenis Pelayanan"))
        
    with col2:
        st.markdown("### Audit Kelengkapan Berkas RM")
        data_audit = pd.DataFrame({
            "Status": ["Lengkap", "Tidak Lengkap"],
            "Jumlah": [850, 150]
        })
        st.write(data_audit)
        st.caption("Presentase Kelengkapan: **85%**")

# -----------------------------------------------------------------------------
# MODUL 3: PETA PERSEBARAN PASIEN TINGKAT KECAMATAN
# -----------------------------------------------------------------------------
elif menu == "Peta Persebaran Pasien (Kecamatan)":
    st.subheader("🗺️ Peta Distribusi Asal Pasien per Kecamatan")
    
    # Dummy koordinat contoh wilayah (misal: area Jakarta Pusat/sekitar)
    data_pasien_kec = pd.DataFrame({
        "Kecamatan": ["Kecamatan A", "Kecamatan B", "Kecamatan C"],
        "lat": [-6.1751, -6.2000, -6.1600],
        "lon": [106.8650, 106.8166, 106.8300],
        "Jumlah_Pasien": [350, 210, 120]
    })
    
    m = folium.Map(location=[-6.1751, 106.8650], zoom_start=12)
    for idx, row in data_pasien_kec.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=row["Jumlah_Pasien"] / 20,
            popup=f"{row['Kecamatan']}: {row['Jumlah_Pasien']} Pasien",
            color="crimson",
            fill=True,
            fill_color="crimson"
        ).add_to(m)
        
    st_folium(m, width=800, height=450)

# -----------------------------------------------------------------------------
# MODUL 4: ABSTRAKSI KODING PENYAKIT
# -----------------------------------------------------------------------------
elif menu == "Abstraksi Koding Penyakit":
    st.subheader("🏷️ Abstraksi & Retrospektif Koding Diagnosa (ICD-10)")
    
    search_icd = st.text_input("Cari ICD-10 atau Nama Diagnosa:", "Diabetes")
    
    data_koding = pd.DataFrame({
        "No RM": ["102030", "102031", "102032"],
        "Diagnosa Utama": ["Diabetes Mellitus Type 2", "Essential Hypertension", "Diabetes Mellitus Type 1"],
        "Kode ICD-10": ["E11.9", "I10", "E10.9"],
        "Tindakan (ICD-9-CM)": ["99.18", "88.72", "99.18"]
    })
    
    filtered_data = data_koding[data_koding["Diagnosa Utama"].str.contains(search_icd, case=False)]
    st.dataframe(filtered_data, use_container_width=True)

# -----------------------------------------------------------------------------
# MODUL 5: INSIDEN KESELAMATAN PASIEN (IKP)
# -----------------------------------------------------------------------------
elif menu == "Insiden Keselamatan Pasien (IKP)":
    st.subheader("🚨 Laporan Insiden Keselamatan Pasien (Beberapa Bulan Terakhir)")
    
    data_ikp = pd.DataFrame({
        "Tanggal": ["2026-07-10", "2026-08-02", "2026-08-15", "2026-09-01"],
        "Jenis Insiden": ["KTD (Kejadian Tidak Diharapkan)", "KNC (Nyaris Cedera)", "KTC (Tidak Cedera)", "KTD"],
        "Unit Pelapor": ["Farmasi", "Rawat Inap A", "Laboratorium", "IGD"],
        "Grading Risiko": ["Kuning", "Hijau", "Rendah", "Merah"]
    })
    
    st.dataframe(data_ikp, use_container_width=True)
    st.area_chart(data_ikp["Jenis Insiden"].value_counts())