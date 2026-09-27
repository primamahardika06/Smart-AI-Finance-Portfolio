# 📊 Smart Portfolio Rebalancing Assistant

Aplikasi berbasis AI yang membantu investor ritel mengevaluasi dan merestrukturisasi portofolio saham Indonesia (IDX) mereka  dibangun untuk **Sectors Hackathon 2026**.

## Latar Belakang

Banyak investor ritel terjebak bias psikologis (seperti *loss aversion*) atau tidak punya waktu menganalisis fundamental portofolio mereka secara mendalam. Aplikasi ini memberikan opini pihak ketiga yang rasional dan berbasis data murni **tanpa** melakukan auto-trading. Keputusan jual/beli akhir tetap di tangan pengguna (konsep **Copilot, bukan Autopilot**).

## Fitur Utama

- **Input Portofolio Interaktif** - form tabel untuk menambah/menghapus saham (ticker, harga rata-rata, jumlah lot), lengkap dengan kalkulasi nilai live dan quick-add ticker populer.
- **Analisis Risiko Konsentrasi Sektor** - mendeteksi dan memperingatkan jika satu sektor mendominasi >40% portofolio.
- **Analisis Valuasi Peer** - membandingkan PE Ratio, PBV, ROE, dan pertumbuhan pendapatan tiap saham terhadap data fundamental terkini.
- **Rekomendasi Rebalancing** - saran Beli/Jual/Tahan per saham beserta alasannya, disajikan dalam narasi lengkap (Executive Summary, Fundamental Analysis, Risk Factors, Kesimpulan) maupun kartu ringkas berwarna.
- **Laporan Excel** - hasil analisis dapat diunduh sebagai file `.xlsx` yang rapi.
- **Mode Development Hemat Kredit** - `MODE=TESTING` menggunakan data mock lokal yang dapat disesuaikan jika ingin melakukan testing, `MODE=PRODUCTION` menarik data langsung dari Sectors API.

## Teknologi yang Digunakan

| Kategori | Teknologi |
|---|---|
| Frontend | [Streamlit](https://streamlit.io/) |
| Agent Orchestration | [LangGraph](https://www.langchain.com/langgraph) |
| LLM (Reasoning Engine) | Gemini API via `langchain-google-genai` |
| Sumber Data | [Sectors API](https://sectors.app/) (eksklusif  tidak menggunakan sumber data lain) |
| Structured Output | Pydantic |
| Laporan Excel | openpyxl |
| Lainnya | `requirements.txt`(bisa dilihat pada file ini) |

## Arsitektur

Sistem mengadopsi pola *agentic workflow* berbasis `StateGraph` (LangGraph):

```
START → Data Fetcher → Risk Assessor → Peer Analyzer → Adviser → END
                                        ↘ Structured Recommender ↗
```

- **Data Fetcher**  - menarik data fundamental per ticker dari Sectors API (atau mock data saat testing).
- **Risk Assessor** - mengevaluasi konsentrasi risiko sektoral.
- **Peer Analyzer** - mengevaluasi valuasi saham terhadap peer/industri.
- **Adviser** - menyusun narasi rekomendasi lengkap berbasis Markdown.
- **Structured Recommender** - menghasilkan rekomendasi aksi terstruktur (Beli/Jual/Tahan) per saham secara paralel, untuk ditampilkan sebagai kartu visual di UI.

LLM berperan murni sebagai *reasoning engine*  seluruh data diambil secara deterministik oleh kode Python, bukan oleh keputusan LLM sendiri.

## Cara Menjalankan

### 1. Clone & install dependency

```bash
git clone <repo-url>
cd smart-portfolio-rebalancing-assistant
pip install -r requirements.txt
```

### 2. Konfigurasi environment

Buat file `.env` di root project:

```
SECTOR_API_KEY=your_sectors_api_key
GOOGLE_API_KEY=your_gemini_api_key
MODE=TESTING
```

Gunakan `MODE=TESTING` untuk development sehari-hari (memakai data mock di `data/mock-sector.json`, hemat kredit API), dan `MODE=PRODUCTION` untuk menarik data real dari Sectors API.

### 3. Jalankan aplikasi

```bash
streamlit run streamlit_tes.py
```

Buka `http://localhost:8501` di browser.

## Cara Penggunaan

1. Isi portofolio kamu di tabel (ticker, harga rata-rata beli, jumlah lot)  atau gunakan quick-add untuk ticker populer.
2. Klik **Analyze & rebalance**.
3. Tunggu beberapa detik hingga analisis selesai.
4. Lihat hasil: alokasi portofolio, peringatan risiko sektor, kartu rekomendasi aksi per saham, dan laporan lengkap.
5. Unduh laporan lengkap dalam format Excel jika diperlukan.

## Batasan & Catatan

- Analisis difokuskan murni pada **fundamental & sektoral**, tidak mencakup analisis teknikal.
- Sistem tidak terhubung ke broker manapun  seluruh output bersifat panduan tekstual, bukan eksekusi transaksi otomatis.
- Target alokasi rebalancing disajikan secara **kualitatif** (Beli/Jual/Tahan), bukan angka target persentase pasti  ini keputusan desain yang disengaja agar tidak memberi ilusi presisi dari estimasi LLM.
- Disclaimer: analisis ini bersifat informasi/edukasi dan bukan merupakan saran keuangan langsung.

## Struktur Project

```
├── main.py                  # PortfolioState, node-node LangGraph, graph pipeline
├── streamlit_tes.py         # UI Streamlit
├── data/
│   └── mock-sector.json     # Data mock untuk MODE=TESTING
├── requirements.txt
└── .env                     # API keys & MODE (tidak di-commit)
```