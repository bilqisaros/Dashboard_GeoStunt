import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils import (
    inject_css, render_section_header, render_insight, render_kpi_card,
    load_metrics, MODEL_COLORS,
)

st.set_page_config(
    page_title="Perbandingan Model - GeoStunt", layout="wide", initial_sidebar_state="expanded"
)
inject_css()

metrics = load_metrics()

render_section_header(
    "Perbandingan Model",
    "Mengapa Geographical Random Forest Dipilih?",
    "Sebelum memilih GRF, dilakukan pengujian bertahap untuk memastikan metode ini "
    "memang diperlukan -- bukan sekadar tren analisis spasial.",
)

# ------------------------------------------------------------ TAHAP 1: UJI ASUMSI
st.markdown('<div class="section-eyebrow">Tahap 1</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title" style="font-size:1.2rem;">Uji Asumsi pada Model Regresi Dasar (OLS)</div>',
    unsafe_allow_html=True,
)

asumsi = metrics["uji_asumsi"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card(
        "Multikolinearitas (VIF)",
        f"{asumsi['vif_max']:.2f}",
        note=asumsi["vif_keterangan"],
        accent="slate",
    )
with col2:
    render_kpi_card(
        "Normalitas Residual",
        asumsi["normalitas"],
        note=f"Shapiro-Wilk p = {asumsi['shapiro_p']:.3f}",
        accent=None,
    )
with col3:
    render_kpi_card(
        "Heteroskedastisitas",
        asumsi["heteroskedastisitas"],
        note=f"Breusch-Pagan p = {asumsi['breusch_pagan_p']:.3f}",
        delta_positive=False,
        accent="terracotta",
    )
with col4:
    render_kpi_card(
        "Autokorelasi Spasial",
        asumsi["autokorelasi_spasial"],
        note=f"Moran's I = {asumsi['moran_ols_I']:.3f}, p = {asumsi['moran_ols_p']:.3f}",
        delta_positive=False,
        accent="terracotta",
    )

render_insight(
    "<strong>Temuan kunci:</strong> Residual model regresi global (OLS) terbukti memiliki "
    "autokorelasi spasial yang signifikan (Moran's I = 0,364; p = 0,001) dan bersifat "
    "heteroskedastis. Ini berarti model global gagal menangkap pola yang bervariasi "
    "secara spasial -- menjadi dasar kuat untuk beralih ke model yang memperhitungkan "
    "lokasi geografis seperti GRF."
)

st.markdown("---")

# ------------------------------------------------------------ TAHAP 2: PERBANDINGAN PERFORMA
st.markdown('<div class="section-eyebrow">Tahap 2</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title" style="font-size:1.2rem;">Perbandingan Performa: OLS vs Random Forest vs GRF</div>',
    unsafe_allow_html=True,
)

perf = metrics["model_performance"]
models = list(perf.keys())

fig = make_subplots(rows=1, cols=3, subplot_titles=("R² (lebih tinggi lebih baik)", "MAE (lebih rendah lebih baik)", "RMSE (lebih rendah lebih baik)"))

for i, metric_key in enumerate(["R2", "MAE", "RMSE"], start=1):
    values = [perf[m][metric_key] for m in models]
    colors = [MODEL_COLORS[m] for m in models]
    fig.add_trace(
        go.Bar(
            x=models, y=values,
            marker=dict(color=colors, line=dict(color="white", width=1.5)),
            text=[f"{v:.3f}" for v in values], textposition="outside",
            textfont=dict(size=13, family="Inter, sans-serif"),
            showlegend=False,
        ),
        row=1, col=i,
    )

fig.update_layout(
    height=400,
    margin=dict(l=10, r=10, t=50, b=10),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", size=13, color="#16302A"),
)
fig.update_yaxes(showgrid=True, gridcolor="#EDE4C8")
fig.update_xaxes(showgrid=False, tickfont=dict(size=12, family="Inter, sans-serif"))
fig.update_annotations(font=dict(size=13, family="Inter, sans-serif", color="#16302A"))
st.plotly_chart(fig, use_container_width=True)

render_insight(
    "GRF konsisten mengungguli OLS dan Random Forest global pada ketiga metrik evaluasi. "
    "Peningkatan R² dari 0,146 (OLS) menjadi 0,203 (GRF) menunjukkan model GRF mampu "
    "menjelaskan variasi stunting antarwilayah secara lebih baik dengan memperhitungkan "
    "konteks spasial tiap kabupaten/kota."
)

st.markdown("---")

# ------------------------------------------------------------ TAHAP 3: MORAN'S I RESIDUAL
st.markdown('<div class="section-eyebrow">Tahap 3</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-title" style="font-size:1.2rem;">Autokorelasi Spasial Residual: Sebelum vs Sesudah GRF</div>',
    unsafe_allow_html=True,
)

moran_res = metrics["moran_residual"]

col_m1, col_m2 = st.columns(2)
with col_m1:
    fig2 = go.Figure(go.Bar(
        x=["Residual OLS", "Residual GRF"],
        y=[moran_res["OLS"]["I"], moran_res["GRF"]["I"]],
        marker_color=["#9CA39B", "#2D6A4F"],
        text=[f"{moran_res['OLS']['I']:.3f}", f"{moran_res['GRF']['I']:.3f}"],
        textposition="outside",
    ))
    fig2.update_layout(
        height=320,
        title="Moran's I pada Residual Model",
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#1B3A2B"),
        yaxis=dict(showgrid=True, gridcolor="#EAE7DC", title="Moran's I"),
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_m2:
    st.markdown("<br>", unsafe_allow_html=True)
    penurunan = (1 - moran_res["GRF"]["I"] / moran_res["OLS"]["I"]) * 100
    render_kpi_card(
        "Penurunan Autokorelasi Spasial",
        f"{penurunan:.0f}%",
        delta=f"{moran_res['OLS']['I']:.3f} -> {moran_res['GRF']['I']:.3f}",
        delta_positive=True,
        note="GRF berhasil menyerap sebagian besar pola spasial yang tidak tertangkap OLS",
    )
    st.markdown(
        """
        <div class="insight-box" style="margin-top:0.8rem;">
        Moran's I yang lebih rendah pada residual GRF membuktikan bahwa pendekatan
        lokal (sub-model per wilayah) lebih berhasil menjelaskan keragaman spasial
        dibanding pendekatan global, walaupun residual belum sepenuhnya bebas
        dari pola spasial (p masih signifikan).
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ------------------------------------------------------------ PARAMETER GRF
render_section_header(
    "Parameter Model GRF yang Digunakan",
    "Konfigurasi akhir setelah optimasi",
    None,
)

params = metrics["grf_params"]
col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
with col_p1:
    render_kpi_card("Bandwidth", str(params["bandwidth"]), note="Jumlah tetangga terdekat", accent="slate")
with col_p2:
    render_kpi_card("Local Weight", f"{params['local_weight']:.3f}", note="Hasil optimasi ISA", accent="gold")
with col_p3:
    render_kpi_card("Jumlah Pohon", str(params["n_estimators"]), note="Per sub-model RF", accent="terracotta")
with col_p4:
    render_kpi_card("Validasi", f"{params['n_folds']}-Fold", note="Cross validation", accent="plum")
with col_p5:
    render_kpi_card("Observasi", str(params["n_obs"]), note="Kabupaten/kota", accent=None)

st.caption(
    "Bandwidth dan local weight ditentukan otomatis melalui metode Incremental Spatial "
    "Autocorrelation (ISA) mengikuti Sun et al. (2024), bukan trial-and-error manual."
)
