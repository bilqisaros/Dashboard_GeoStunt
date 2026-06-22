import streamlit as st
from utils import (
    inject_css, render_hero, render_section_header, render_kpi_card,
    render_insight, load_master_data, load_metrics, format_number,
    FACTOR_COLORS,
)

st.set_page_config(
    page_title="GeoStunt - Dashboard Analitik Spasial Stunting",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

df = load_master_data()
metrics = load_metrics()

# ---------------------------------------------------------------- HERO
render_hero(
    title="GeoStunt: Dashboard Analitik Spasial Faktor Dominan Stunting",
    subtitle=(
        "Pemetaan faktor dominan penyebab stunting di tiap kabupaten/kota Indonesia "
        "menggunakan Geographical Random Forest (GRF), sebagai dasar perancangan "
        "intervensi presisi yang disesuaikan dengan karakteristik tiap wilayah."
    ),
    badges=[
        "Metode: Geographical Random Forest",
        f"{len(df)} Kabupaten/Kota",
        "Sumber: SSGI 2024, BPS, BAPANAS",
    ],
)

# ---------------------------------------------------------------- SIDEBAR NOTE
with st.sidebar:
    st.markdown("### Tentang GeoStunt")
    st.markdown(
        """
        Dashboard ini disusun untuk mendukung argumen bahwa program penurunan
        stunting nasional perlu disesuaikan dengan faktor dominan di setiap
        wilayah, bukan diterapkan secara seragam.

        Gunakan menu di sebelah kiri untuk menjelajahi:

        - **Beranda** - ringkasan temuan utama
        - **Peta Nasional** - sebaran stunting & faktor dominan
        - **Perbandingan Model** - mengapa GRF dipilih
        - **Profil Kabupaten/Kota** - detail per wilayah
        - **Tentang Metode** - dasar metodologi & data
        """
    )
    st.markdown("---")
    st.caption(
        "Data dianalisis dari 404 kabupaten/kota dengan data SSGI 2024 lengkap, "
        "dari total 522 kabupaten/kota di Indonesia."
    )

# ---------------------------------------------------------------- KPI ROW
render_section_header(
    "Ringkasan Eksekutif",
    "Apa yang ditemukan analisis ini?",
    "Empat indikator kunci yang menjadi dasar argumen kebijakan dalam dashboard ini.",
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    render_kpi_card(
        "Rata-Rata Stunting Nasional",
        f"{format_number(df['stunting'].mean())}%",
        note=f"Rentang {format_number(df['stunting'].min())}% - {format_number(df['stunting'].max())}% antar kabupaten/kota",
        accent="terracotta",
    )

with col2:
    moran_ols = metrics["uji_asumsi"]["moran_ols_I"]
    render_kpi_card(
        "Autokorelasi Spasial Residual OLS",
        f"{moran_ols:.3f}",
        delta="Signifikan (p < 0.01)",
        delta_positive=False,
        note="Model global gagal menangkap variasi antarwilayah",
        accent="slate",
    )

with col3:
    r2_ols = metrics["model_performance"]["OLS"]["R2"]
    r2_grf = metrics["model_performance"]["GRF"]["R2"]
    improvement = ((r2_grf - r2_ols) / r2_ols) * 100
    render_kpi_card(
        "Peningkatan R² (OLS -> GRF)",
        f"+{improvement:.0f}%",
        delta=f"{r2_ols:.3f} -> {r2_grf:.3f}",
        delta_positive=True,
        note="GRF lebih akurat menjelaskan variasi stunting",
        accent=None,
    )

with col4:
    top_factor = max(metrics["faktor_dominan_distribusi"], key=metrics["faktor_dominan_distribusi"].get)
    top_count = metrics["faktor_dominan_distribusi"][top_factor]
    pct = top_count / sum(metrics["faktor_dominan_distribusi"].values()) * 100
    render_kpi_card(
        "Faktor Dominan Tersering",
        top_factor,
        delta=f"{top_count} dari 404 kab/kota ({pct:.0f}%)",
        delta_positive=True,
        note="Namun bukan dominan di seluruh wilayah",
        accent="gold",
    )

st.markdown("")

# ---------------------------------------------------------------- INSIGHT UTAMA
render_insight(
    "<strong>Temuan utama:</strong> Faktor dominan penyebab stunting berbeda-beda "
    "antar wilayah. RLS (pendidikan ibu) dominan di sebagian besar wilayah Jawa dan "
    "Sumatra, kemiskinan dominan di wilayah Indonesia timur, sementara konsumsi pangan "
    "hewani dominan di sebagian Nusa Tenggara dan Sulawesi. Hal ini menunjukkan bahwa "
    "program intervensi yang seragam secara nasional berisiko tidak optimal karena "
    "tidak menyasar akar masalah yang sesungguhnya di tiap wilayah."
)

st.markdown("")

# ---------------------------------------------------------------- DISTRIBUSI FAKTOR (preview)
render_section_header(
    "Sebaran Faktor Dominan",
    "Lima faktor, peran yang tidak setara di setiap wilayah",
    "Setiap batang menunjukkan jumlah kabupaten/kota di mana faktor tersebut menjadi "
    "penyumbang tertinggi terhadap prevalensi stunting, berdasarkan local feature "
    "importance dari model GRF.",
)

import plotly.graph_objects as go

dist = metrics["faktor_dominan_distribusi"]
items = sorted(dist.items(), key=lambda x: x[1])
labels = [i[0] for i in items]
values = [i[1] for i in items]
colors = [FACTOR_COLORS.get(l, "#999") for l in labels]

col_chart1, col_chart2 = st.columns([3, 2])

with col_chart1:
    fig = go.Figure(go.Bar(
        x=values, y=labels, orientation="h",
        marker=dict(color=colors, line=dict(color="white", width=1.5)),
        text=[f"{v} kab/kota" for v in values],
        textposition="outside",
        textfont=dict(size=13, family="Inter, sans-serif"),
    ))
    fig.update_layout(
        height=340,
        margin=dict(l=10, r=60, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=True, gridcolor="#EDE4C8", title="Jumlah Kabupaten/Kota"),
        yaxis=dict(showgrid=False, tickfont=dict(size=13)),
        font=dict(family="Inter, sans-serif", size=13, color="#16302A"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_chart2:
    items_desc = sorted(dist.items(), key=lambda x: -x[1])
    labels_d = [i[0] for i in items_desc]
    values_d = [i[1] for i in items_desc]
    colors_d = [FACTOR_COLORS.get(l, "#999") for l in labels_d]

    fig_donut = go.Figure(go.Pie(
        labels=labels_d, values=values_d, hole=0.58,
        marker=dict(colors=colors_d, line=dict(color="#FBF7EE", width=2)),
        textinfo="percent", textfont=dict(size=12, color="white", family="Inter, sans-serif"),
        showlegend=False,
    ))
    fig_donut.add_annotation(
        text=f"<b>{sum(values_d)}</b><br>kab/kota",
        showarrow=False, font=dict(size=15, family="Fraunces, serif", color="#16302A"),
    )
    fig_donut.update_layout(
        height=340,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

st.caption(
    "Selengkapnya mengenai persebaran spasial faktor-faktor ini dapat dilihat pada "
    "halaman **Peta Nasional**."
)

st.markdown("---")

# ---------------------------------------------------------------- PREVIEW PETA
render_section_header(
    "Pratinjau Peta Nasional",
    "Faktor dominan stunting di seluruh Indonesia",
    "Setiap warna mewakili faktor yang paling berkontribusi terhadap stunting di "
    "kabupaten/kota tersebut. Wilayah abu-abu menandakan data SSGI 2024 tidak tersedia.",
)

import json
import plotly.express as px
from utils import load_geo_data

gdf_preview = load_geo_data()
geojson_preview = json.loads(gdf_preview.to_json())

fig_map = px.choropleth(
    gdf_preview,
    geojson=geojson_preview,
    locations=gdf_preview.index,
    color="faktor_dominan",
    color_discrete_map=FACTOR_COLORS,
    hover_name="kab_kota",
    category_orders={"faktor_dominan": list(FACTOR_COLORS.keys())},
)
fig_map.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
fig_map.update_layout(
    height=420,
    margin=dict(l=0, r=0, t=0, b=0),
    legend_title_text="Faktor Dominan",
    legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    font=dict(family="Inter, sans-serif", size=12, color="#16302A"),
    paper_bgcolor="rgba(0,0,0,0)",
)
fig_map.update_traces(marker_line_width=0.3, marker_line_color="white")
st.plotly_chart(fig_map, use_container_width=True)

st.caption("Buka halaman **Peta Nasional** untuk eksplorasi penuh, termasuk filter per variabel.")

# ---------------------------------------------------------------- FOOTER
st.markdown(
    """
    <div class="geostunt-footer">
        GeoStunt &mdash; Dashboard Analitik Spasial Stunting Indonesia<br>
        Disusun untuk kompetisi Satria Data &middot; Metode: Geographical Random Forest (Georganos et al., 2019; Georganos &amp; Kalogirou, 2022; Sun et al., 2024)<br>
        Sumber data: SSGI 2024, Badan Pusat Statistik, Badan Pangan Nasional
    </div>
    """,
    unsafe_allow_html=True,
)
