import streamlit as st
import simpy
import random
import pandas as pd
import plotly.express as px

# ======================
# PARAMETER SISTEM
# ======================
JUMLAH_MEJA = 60
OMPRENG_PER_MEJA = 3
TOTAL_OMPRENG = JUMLAH_MEJA * OMPRENG_PER_MEJA

WAKTU_LAUK = (30, 60)
WAKTU_ANGKUT = (20, 60)
WAKTU_NASI = (30, 60)

# ======================
# PROSES SIMULASI
# ======================
def proses_ompreng(env, nama, petugas_lauk, petugas_angkut, petugas_nasi, data):
    mulai = env.now

    with petugas_lauk.request() as req:
        yield req
        waktu_lauk = random.randint(*WAKTU_LAUK)
        yield env.timeout(waktu_lauk)

    with petugas_angkut.request() as req:
        yield req
        waktu_angkut = random.randint(*WAKTU_ANGKUT)
        yield env.timeout(waktu_angkut)

    with petugas_nasi.request() as req:
        yield req
        waktu_nasi = random.randint(*WAKTU_NASI)
        yield env.timeout(waktu_nasi)

    selesai = env.now
    data.append([nama, waktu_lauk, waktu_angkut, waktu_nasi, selesai - mulai])

# ======================
# FUNGSI SIMULASI
# ======================
def jalankan_simulasi():
    env = simpy.Environment()

    petugas_lauk = simpy.Resource(env, capacity=2)
    petugas_angkut = simpy.Resource(env, capacity=2)
    petugas_nasi = simpy.Resource(env, capacity=3)

    data = []

    for i in range(TOTAL_OMPRENG):
        env.process(
            proses_ompreng(
                env,
                f"Ompreng-{i+1}",
                petugas_lauk,
                petugas_angkut,
                petugas_nasi,
                data
            )
        )

    env.run()
    return pd.DataFrame(
        data,
        columns=["Ompreng", "Waktu Lauk", "Waktu Angkut", "Waktu Nasi", "Total Waktu"]
    ), env.now

# ======================
# STREAMLIT UI
# ======================
st.title("📊 Dashboard Simulasi Sistem Piket IT Del")

st.write("""
Dashboard ini menampilkan hasil *simulasi Discrete Event Simulation*
untuk sistem piket mahasiswa IT Del.
""")

if st.button("▶️ Jalankan Simulasi"):
    df, total_waktu = jalankan_simulasi()

    st.success("Simulasi selesai!")

    # ======================
    # RINGKASAN
    # ======================
    jam = 7 + total_waktu // 3600
    menit = (total_waktu % 3600) // 60

    st.metric("Total Ompreng", TOTAL_OMPRENG)
    st.metric("Total Waktu (detik)", f"{total_waktu:.2f}")
    st.metric("Selesai Pukul", f"{int(jam):02d}:{int(menit):02d}")

    # ======================
    # TABEL DATA
    # ======================
    st.subheader("📋 Data Hasil Simulasi")
    st.dataframe(df)

    # ======================
    # GRAFIK
    # ======================
    st.subheader("📈 Rata-rata Waktu Proses")

    rata_rata = df[["Waktu Lauk", "Waktu Angkut", "Waktu Nasi"]].mean().reset_index()
    rata_rata.columns = ["Proses", "Waktu (detik)"]

    fig = px.bar(
        rata_rata,
        x="Proses",
        y="Waktu (detik)",
        title="Rata-rata Waktu Setiap Proses"
    )

    st.plotly_chart(fig, use_container_width=True)