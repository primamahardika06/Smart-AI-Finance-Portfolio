import streamlit as st
from main import graph, build_report, render_colored_bar
import uuid


st.title("💰Smart portfolio rebalancing")

css = """
<style>
    div[class*="st-key-bg_Beli"] {
        background-color: #d4edda; /* Hijau muda */
        padding: 15px; border-radius: 8px; margin-bottom: 10px;
    }
    div[class*="st-key-bg_Tahan"] {
        background-color: #fff3cd; /* Kuning muda */
        padding: 15px; border-radius: 8px; margin-bottom: 10px;
    }
    div[class*="st-key-bg_Jual"] {
        background-color: #f8d7da; /* Merah muda */
        padding: 15px; border-radius: 8px; margin-bottom: 10px;
    }
    div[class*="st-key-bg_N_A"] {
        background-color: #f1f3f4; /* Abu-abu muda jika tidak ada aksi */
        padding: 15px; border-radius: 8px; margin-bottom: 10px;
    }
</style>
"""
st.html(css)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        "<h3 style='text-align: center;'>📋</h3>", unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center;'><b>1. Isi portofolio</b></p>",
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        "<h3 style='text-align: center;'>🔍</h3>", unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center;'><b>2. Analisis otomatis</b></p>",
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        "<h3 style='text-align: center;'>⏱️</h3>", unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center;'><b>3. Dapat rekomendasi</b></p>",
        unsafe_allow_html=True,
    )

st.set_page_config(layout="wide")  


with st.container(border=True):

    st.subheader("Portofolio kamu")

    # Inisialisasi session state untuk menyimpan daftar saham
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = [
            {"id": str(uuid.uuid4()), "ticker": "BBCA", "harga": 6000, "lot": 500},
            {"id": str(uuid.uuid4()), "ticker": "BBRI", "harga": 3000, "lot": 500},
            {"id": str(uuid.uuid4()), "ticker": "BMRI", "harga": 4000, "lot": 460},
        ]

    # Header Tabel
    with st.container(border=True):
        col_h1, col_h2, col_h3, col_h4 = st.columns([5, 5, 5, 1])
        col_h1.caption("Ticker")
        col_h2.caption("Harga rata-rata")
        col_h3.caption("Jumlah lot")
        col_h4.caption("Nilai")

    # Render tiap baris input secara dinamis
        indices_to_delete = []
        for idx, item in enumerate(st.session_state.portfolio):
            st.divider()
            
            row_id = item["id"]
            col1, col2, col3, col4 = st.columns([5, 5, 5, 1])

            item["ticker"] = col1.text_input(
                f"Ticker {idx}",
                value=item["ticker"],
                key=f"ticker_{row_id}",
                label_visibility="collapsed",
                
            )
            item["harga"] = col2.number_input(
                f"Harga {row_id}",
                value=item["harga"],
                key=f"harga_{row_id}",
                label_visibility="collapsed",
            )
            item["lot"] = col3.number_input(
                f"Lot {row_id}",
                value=item["lot"],
                key=f"lot_{row_id}",
                label_visibility="collapsed",
            )
            
            if col4.button("🗑️", key=f"del_{row_id}"):
                st.write()
                indices_to_delete.append(idx)

    # Hapus data dari state jika ada tombol hapus yang diklik
        if indices_to_delete:
            for idx in sorted(indices_to_delete, reverse=True):
                st.session_state.portfolio.pop(idx)
            st.rerun()

        # Tombol Aksi di Bagian Bawah
        col_btn_left, col_btn_right = st.columns([3, 3])

        with col_btn_left:
            if st.button("+ Tambah saham", use_container_width=True):
                st.session_state.portfolio.append({"id": str(uuid.uuid4()), "ticker": "", "harga": 0, "lot": 0})
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
                    with st.spinner("LLM sedang menganalisis portofolio anda..."):
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
    with st.container(border=True):
        st.subheader("Alokasi & rekomendasi aksi")

        portfolio = st.session_state.portfolio
        nilai_per_saham = {
            item["ticker"]: item["harga"] * item["lot"]
            for item in portfolio if item["ticker"].strip()
        }
        total_nilai = sum(nilai_per_saham.values())

        actions_map = {rec["ticker"]: rec for rec in result.get("structured_recommendations", [])}
        badge_color = {"Beli": "green", "Jual": "red", "Tahan": "orange"}

        st.caption("Alokasi saat ini")
        for ticker, nilai in nilai_per_saham.items():
            persen = (nilai / total_nilai * 100) if total_nilai > 0 else 0
            render_colored_bar(ticker, persen)

        st.divider()
        
        st.caption("Rekomendasi aksi")
        
        for ticker, nilai in nilai_per_saham.items():
            rec = actions_map.get(ticker)
            action_name = rec["action"] if rec else "N_A"
            with st.container(key=f"bg_{action_name}_{ticker}"):
                col_a, col_b = st.columns([10, 1])
                with col_a:
                    st.write(f"**{ticker}**")
                    if rec:
                        st.caption(rec.get("alasan_singkat", ""))
                with col_b:
                    if rec:
                        if rec["action"] == "Beli":
                            warna = badge_color.get(rec["action"], "green")
                        elif rec["action"] == "Tahan":
                            warna = badge_color.get(rec["action"], "yellow")
                        else:
                            warna = badge_color.get(rec["action"], "red") 
                        st.markdown(f":{warna}[{rec['action']}]")
                    else:
                        st.caption("N/A")
                        
                        
    with st.expander("📄 Laporan lengkap (Executive Summary, Risk Factors, dst)"):                      
        with st.container(border=True):
                        
            st.subheader("Hasil analisis")
            if result.get("concentration_risk"):
                st.warning(result["concentration_risk"])
            st.markdown(result.get("final_recommendation", "Belum ada rekomendasi."))

            report_bytes = build_report(result)

            st.download_button(
                label="Download report",
                data=report_bytes,
                file_name="portfolio_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
            )