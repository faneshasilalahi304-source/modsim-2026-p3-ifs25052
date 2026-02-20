import simpy
import random
import streamlit as st
import numpy as np

# ==========================
# PARAMETER DEFAULT
# ==========================
START_TIME = 7 * 60  # 07:00 dalam menit
TOTAL_MEJA = 60
MAHASISWA_PER_MEJA = 3
TOTAL_MAHASISWA = TOTAL_MEJA * MAHASISWA_PER_MEJA

# ==========================
# SIMULASI
# ==========================

def simulasi_piket(jumlah_petugas=7):

    env = simpy.Environment()

    # Resource (kita bagi 3 tahap)
    petugas_lauk = simpy.Resource(env, capacity=2)
    petugas_angkat = simpy.Resource(env, capacity=2)
    petugas_nasi = simpy.Resource(env, capacity=3)

    waktu_selesai = []

    def proses_mahasiswa(env, nama):

        # Tahap 1: Isi Lauk
        with petugas_lauk.request() as req:
            yield req
            yield env.timeout(random.uniform(0.5, 1))  # 30-60 detik

        # Tahap 2: Angkat (batch effect disederhanakan)
        with petugas_angkat.request() as req:
            yield req
            yield env.timeout(random.uniform(0.33, 1))  # 20-60 detik

        # Tahap 3: Tambah Nasi
        with petugas_nasi.request() as req:
            yield req
            yield env.timeout(random.uniform(0.5, 1))  # 30-60 detik

        waktu_selesai.append(env.now)

    # Generate mahasiswa (semua datang di awal)
    for i in range(TOTAL_MAHASISWA):
        env.process(proses_mahasiswa(env, f"Mhs-{i}"))

    env.run()

    selesai_terakhir = max(waktu_selesai)
    total_durasi = selesai_terakhir

    return total_durasi, waktu_selesai


# ==========================
# STREAMLIT APP
# ==========================

st.title("Simulasi Sistem Piket IT Del (Studi Kasus 2.1)")

st.write("Simulasi Discrete Event Simulation untuk sistem piket mahasiswa.")

jumlah_petugas = st.slider("Jumlah Total Petugas", 3, 10, 7)

if st.button("Jalankan Simulasi"):

    durasi, data_selesai = simulasi_piket(jumlah_petugas)

    jam_selesai = 7 + int(durasi // 60)
    menit_selesai = int(durasi % 60)

    st.success("Simulasi selesai!")

    st.metric("Total Mahasiswa", TOTAL_MAHASISWA)
    st.metric("Waktu Selesai Terakhir", f"{jam_selesai:02d}:{menit_selesai:02d}")
    st.metric("Total Durasi (menit)", round(durasi, 2))

    st.subheader("Distribusi Waktu Penyelesaian")
    st.bar_chart(np.histogram(data_selesai, bins=20)[0])