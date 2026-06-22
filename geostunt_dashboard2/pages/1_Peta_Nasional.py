import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json

from utils import (
    inject_css, render_section_header, render_insight, render_warning,
    load_geo_data, load_master_data, VAR_COLS, VAR_LABELS, VAR_UNITS,
    FACTOR_COLORS,
)

st.set_page_config(
    page_title="Peta Nasional - GeoStunt", layout="wide", initial_sidebar_state="expanded"
)
inject_css()

render_section_header(
    "Peta Nasional",
    "Sebaran Stunting dan Faktor Dominan per Kabupaten/Kota",
    "Peta mencakup seluruh 522 kabupaten/kota di Indonesia. Wilayah berwarna abu-abu "
    "menandakan data SSGI 2024 untuk wilayah tersebut tidak tersedia atau tidak lengkap "
    "sehingga tidak diikutkan dalam analisis GRF.",
)

gdf = load_geo_data()
df = load_master_data()

# ------------------------------------------------------------ KONTROL
col_ctrl1, col_ctrl2 = st.columns([1, 2])
with col_ctrl1:
    peta_pilihan = st.radio(
        "Pilih tampilan peta",
        ["Faktor Dominan", "Prevalensi Stunting", "Local Importance per Variabel"],
        index=0,
    )

geojson_dict = json.loads(gdf.to_json())

# ------------------------------------------------------------ PETA: FAKTOR DOMINAN
if peta_pilihan == "Faktor Dominan":

    color_map = FACTOR_COLORS

    fig = px.choropleth(
        gdf,
        geojson=geojson_dict,
        locations=gdf.index,
        color="faktor_dominan",
        color_discrete_map=color_map,
        hover_name="kab_kota",
        hover_data={"provinsi": True, "stunting": ":.1f"},
        category_orders={"faktor_dominan": list(color_map.keys())},
    )
    fig.update_geos(
        fitbounds="locations", visible=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        height=560,
        margin=dict(l=0, r=0, t=10, b=0),
        legend_title_text="Faktor Dominan",
        font=dict(family="Inter, sans-serif", size=12, color="#1B3A2B"),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(marker_line_width=0.3, marker_line_color="white")
    st.plotly_chart(fig, use_container_width=True)

    render_insight(
        "<strong>Cara membaca peta:</strong> Setiap warna menunjukkan faktor yang paling "
        "berkontribusi terhadap prevalensi stunting di kabupaten/kota tersebut, berdasarkan "
        "nilai local feature importance dari model GRF. Wilayah dengan warna yang sama "
        "tidak berarti memiliki tingkat stunting yang sama -- hanya berarti faktor "
        "penyebab utamanya serupa."
    )

# ------------------------------------------------------------ PETA: STUNTING
elif peta_pilihan == "Prevalensi Stunting":

    fig = px.choropleth(
        gdf,
        geojson=geojson_dict,
        locations=gdf.index,
        color="stunting",
        color_continuous_scale=[
            [0, "#F4F1E8"], [0.3, "#E9C46A"], [0.6, "#E76F51"], [1, "#9D2B1F"]
        ],
        hover_name="kab_kota",
        hover_data={"provinsi": True, "stunting": ":.1f"},
        range_color=(df["stunting"].min(), df["stunting"].max()),
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        height=560,
        margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_colorbar=dict(title="Stunting (%)"),
        font=dict(family="Inter, sans-serif", size=12, color="#1B3A2B"),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(marker_line_width=0.3, marker_line_color="white")
    st.plotly_chart(fig, use_container_width=True)

    target_nasional = 14
    above_target = (df["stunting"] > target_nasional).sum()
    render_warning(
        f"<strong>{above_target} dari {len(df)} kabupaten/kota ({above_target/len(df)*100:.0f}%)</strong> "
        f"masih berada di atas target RPJMN sebesar {target_nasional}%. Wilayah dengan warna "
        "lebih gelap menunjukkan prevalensi yang lebih tinggi dan memerlukan perhatian lebih."
    )

# ------------------------------------------------------------ PETA: LOCAL IMPORTANCE PER VARIABEL
else:
    var_pilihan = st.selectbox(
        "Pilih variabel",
        VAR_COLS,
        format_func=lambda x: VAR_LABELS[x],
    )
    var_label = VAR_LABELS[var_pilihan]

    # Kolom local importance disimpan dengan nama label (lihat dominan_df.csv)
    col_importance = var_label

    fig = px.choropleth(
        gdf,
        geojson=geojson_dict,
        locations=gdf.index,
        color=col_importance,
        color_continuous_scale=[
            [0, "#F4F1E8"], [0.5, "#74A892"], [1, "#1B3A2B"]
        ],
        hover_name="kab_kota",
        hover_data={"provinsi": True},
    )
    fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(
        height=560,
        margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_colorbar=dict(title="Local Importance"),
        font=dict(family="Inter, sans-serif", size=12, color="#1B3A2B"),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(marker_line_width=0.3, marker_line_color="white")
    st.plotly_chart(fig, use_container_width=True)

    render_insight(
        f"Semakin gelap warna kabupaten/kota, semakin besar peran <strong>{var_label}</strong> "
        "dalam menjelaskan tingkat stunting di wilayah tersebut menurut model GRF -- "
        "terlepas dari apakah variabel ini menjadi faktor paling dominan atau bukan."
    )

st.markdown("---")

# ------------------------------------------------------------ LEGENDA & TABEL RINGKAS
col_a, col_b = st.columns([1, 1])

with col_a:
    render_section_header(
        "Legenda Faktor Dominan",
        "Distribusi wilayah per faktor",
        None,
    )
    dist = df["faktor_dominan"].value_counts()
    for factor, count in dist.items():
        color = FACTOR_COLORS.get(factor, "#999")
        st.markdown(
            f"""
            <div class="legend-chip">
                <span class="legend-dot" style="background:{color}"></span>
                {factor} &mdash; {count} kab/kota
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_b:
    render_section_header(
        "Cari Kabupaten/Kota",
        "Lihat faktor dominan secara spesifik",
        None,
    )
    search = st.selectbox(
        "Ketik nama kabupaten/kota",
        sorted(df["kab_kota"].unique()),
        index=None,
        placeholder="Contoh: Lebak, Sumba Timur, Jayawijaya...",
    )
    if search:
        row = df[df["kab_kota"] == search].iloc[0]
        color = FACTOR_COLORS.get(row["faktor_dominan"], "#999")
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-label">{row['provinsi']}</div>
                <div class="kpi-value" style="font-size:1.3rem;">{search}</div>
                <div style="margin-top:0.5rem;">
                    <span class="legend-chip">
                        <span class="legend-dot" style="background:{color}"></span>
                        Faktor dominan: {row['faktor_dominan']}
                    </span>
                </div>
                <div class="kpi-note" style="margin-top:0.5rem;">
                    Prevalensi stunting: {row['stunting']:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Lihat detail lengkap di halaman **Profil Kabupaten/Kota**.")
