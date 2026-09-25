import streamlit as st
from main import graph
import pandas as pd

st.set_page_config(layout="wide")  

# col_kiri, col_tengah, col_kanan = st.columns([1, 2, 1])


# with col_tengah:
st.title("Smart portfolio rebalancing")
with st.container(border=True):
    st.subheader("Portofolio kamu")

    # st.sidebar.selectbox("Choose a model", ["GPT-4", "Claude", "Gemini"])

    # Inisialisasi session state untuk menyimpan daftar saham
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = [
            {"ticker": "BBCA", "harga": 6000, "lot": 6500},
            {"ticker": "BBRI", "harga": 1000, "lot": 3500},
            {"ticker": "BMRI", "harga": 2000, "lot": 4460},
        ]

    # Header Tabel
    col_h1, col_h2, col_h3, col_h4 = st.columns([10, 10, 10, 1])
    col_h1.caption("Ticker")
    col_h2.caption("Harga rata-rata")
    col_h3.caption("Jumlah lot")

    # Render tiap baris input secara dinamis
    indices_to_delete = []
    for idx, item in enumerate(st.session_state.portfolio):
        col1, col2, col3, col4 = st.columns([10, 10, 10, 1])

        item["ticker"] = col1.text_input(
            f"Ticker {idx}",
            value=item["ticker"],
            key=f"ticker_{idx}",
            label_visibility="collapsed",
            
        )
        item["harga"] = col2.number_input(
            f"Harga {idx}",
            value=item["harga"],
            key=f"harga_{idx}",
            label_visibility="collapsed",
        )
        item["lot"] = col3.number_input(
            f"Lot {idx}",
            value=item["lot"],
            key=f"lot_{idx}",
            label_visibility="collapsed",
        )

        # Tombol hapus baris (Ikon tempat sampah)
        if col4.button("🗑️", key=f"del_{idx}"):
            indices_to_delete.append(idx)

    # Hapus data dari state jika ada tombol hapus yang diklik
    if indices_to_delete:
        for idx in sorted(indices_to_delete, reverse=True):
            st.session_state.portfolio.pop(idx)
        st.rerun()

    # Tombol Aksi di Bagian Bawah
    col_btn_left, col_btn_right = st.columns([1, 2.13])

    with col_btn_left:
        if st.button("+ Tambah saham", use_container_width=True):
            st.session_state.portfolio.append(
                {"ticker": "", "harga": 0, "lot": 0}
            )
            st.rerun()

    with col_btn_right:
        if st.button("Analyze & rebalance", type="primary", use_container_width=True):
            # Mapping struktur form ke struktur holdings yang dipahami PortfolioState
            holdings = [
                {
                    "ticker": item["ticker"].strip().upper(),
                    "harga_rata": item["harga"],
                    "jumlah": item["lot"],
                }
                for item in st.session_state.portfolio
                if item["ticker"].strip()  # skip baris kosong
            ]

            if not holdings:
                st.warning("Tambahkan minimal satu saham dulu.")
            else:
                with st.spinner("Menganalisis portofolio..."):
                    try:
                        result = graph.invoke(
                            {"holdings": holdings},
                            {"recursion_limit": 10},
                        )
                        st.session_state.analysis_result = result
                    except Exception as e:
                        st.session_state.analysis_result = None
                        st.error(f"Analisis gagal: {e}")
                            
if st.session_state.get("analysis_result"):
    result = st.session_state.analysis_result
    # with col_tengah:
    with st.container(border=True, width=2000):
        st.subheader("Alokasi & rekomendasi aksi")

        # Persentase konsentrasi -- dihitung manual, bukan dari LLM
        portfolio = st.session_state.portfolio
        nilai_per_saham = {
            item["ticker"]: item["harga"] * item["lot"]
            for item in portfolio if item["ticker"].strip()
        }
        total_nilai = sum(nilai_per_saham.values())

        # Petakan aksi per ticker dari structured output
        actions_map = {
            rec["ticker"]: rec for rec in result.get("structured_recommendations", [])
        }
        badge_color = {"Beli": "green", "Jual": "red", "Tahan": "orange"}

        for ticker, nilai in nilai_per_saham.items():
            persen = (nilai / total_nilai * 100) if total_nilai > 0 else 0
            rec = actions_map.get(ticker)

            col_a, col_b = st.columns([10, 1])
            with col_a:
                st.write(f"**{ticker}** — {persen:.1f}%")
                st.progress(min(persen / 100, 1.0))
            with col_b:
                if rec:
                    warna = badge_color.get(rec["action"], "gray")
                    st.markdown(f":{warna}[{rec['action']}]")
                else:
                    st.caption("N/A")
    with st.container(border=True, width=2000):
                    
        st.subheader("Hasil analisis")
        if result.get("concentration_risk"):
            st.warning(result["concentration_risk"])
        st.markdown(result.get("final_recommendation", "Belum ada rekomendasi."))