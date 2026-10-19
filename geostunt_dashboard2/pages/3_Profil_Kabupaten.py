
import streamlit as st
import plotly.graph_objects as go

from utils import (
    inject_css, render_section_header, render_insight, render_kpi_card,
    load_master_data, load_local_importance,
    VAR_COLS, VAR_LABELS, VAR_UNITS, FACTOR_COLORS,
)

st.set_page_config(
    page_title="Profil Kabupaten/Kota - GeoStunt",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

df = load_master_data()
df_local = load_local_importance()

render_section_header(
    "Profil Kabupaten/Kota",
    "Telusuri Detail Faktor Dominan per Wilayah",
    "Pilih provinsi dan kabupaten/kota untuk melihat profil stunting, "
    "nilai variabel, dan kontribusi tiap faktor menurut model GRF.",
)

# ------------------------------------------------------------
# FILTER PROVINSI DAN KABUPATEN/KOTA
# ------------------------------------------------------------

col_f1, col_f2 = st.columns(2)

with col_f1:
    provinsi_list = sorted(df["provinsi"].dropna().unique())

    provinsi_pilihan = st.selectbox(
        "Provinsi",
        provinsi_list,
        index=None,
        placeholder="Pilih provinsi",
    )

with col_f2:
    if provinsi_pilihan:
        kab_list = sorted(
            df.loc[
                df["provinsi"] == provinsi_pilihan,
                "kab_kota",
            ].dropna().unique()
        )
    else:
        kab_list = sorted(df["kab_kota"].dropna().unique())

    kab_pilihan = st.selectbox(
        "Kabupaten/Kota",
        kab_list,
        index=None,
        placeholder="Pilih kabupaten/kota",
    )

# ------------------------------------------------------------
# TAMPILAN JIKA KABUPATEN/KOTA BELUM DIPILIH
# ------------------------------------------------------------

if not kab_pilihan:
    st.info(
        "Pilih kabupaten/kota di atas untuk menampilkan profil lengkap."
    )

    st.markdown("---")

    render_section_header(
        "Atau, Jelajahi Berdasarkan Peringkat",
        "Wilayah dengan Stunting Tertinggi",
        None,
    )

    top10 = df.nlargest(10, "stunting")[
        ["kab_kota", "provinsi", "stunting", "faktor_dominan"]
    ]

    top10 = top10.rename(
        columns={
            "kab_kota": "Kabupaten/Kota",
            "provinsi": "Provinsi",
            "stunting": "Stunting (%)",
            "faktor_dominan": "Faktor Dominan",
        }
    )

    st.dataframe(
        top10,
        use_container_width=True,
        hide_index=True,
    )

    st.stop()

# ------------------------------------------------------------
# DATA KABUPATEN/KOTA TERPILIH
# ------------------------------------------------------------

# Filter berdasarkan provinsi dan kabupaten/kota agar nama wilayah
# yang sama di provinsi berbeda tidak tertukar.
if provinsi_pilihan:
    wilayah_df = df[
        (df["provinsi"] == provinsi_pilihan)
        & (df["kab_kota"] == kab_pilihan)
    ]
else:
    wilayah_df = df[df["kab_kota"] == kab_pilihan]

if wilayah_df.empty:
    st.error("Data kabupaten/kota tidak ditemukan.")
    st.stop()

row = wilayah_df.iloc[0]

# Data seluruh kabupaten/kota dalam provinsi terpilih
prov_df_selected = df[
    df["provinsi"] == row["provinsi"]
]

# Ambil Local Feature Importance untuk wilayah terpilih
local_df_selected = df_local[
    df_local["kab_kota"] == kab_pilihan
]

# Jika tersedia kolom provinsi, gunakan juga untuk memastikan wilayah tepat
if "provinsi" in df_local.columns:
    local_df_selected = local_df_selected[
        local_df_selected["provinsi"] == row["provinsi"]
    ]

if local_df_selected.empty:
    st.error(
        "Data Local Feature Importance untuk wilayah ini tidak ditemukan."
    )
    st.stop()

row_local = local_df_selected.iloc[0]

color = FACTOR_COLORS.get(
    row_local["faktor_dominan"],
    "#999999",
)

st.markdown("---")

# ------------------------------------------------------------
# HEADER PROFIL
# ------------------------------------------------------------

col_h1, col_h2 = st.columns([2, 1])

with col_h1:
    st.markdown(
        f'<div class="kpi-card" style="padding:1.4rem 1.5rem;">'
        f'<div class="kpi-label">{row["provinsi"]}</div>'
        f'<div class="kpi-value" style="font-size:1.7rem;">'
        f'{kab_pilihan}</div>'
        f'<div style="margin-top:0.7rem;">'
        f'<span class="legend-chip" style="font-size:0.85rem;">'
        f'<span class="legend-dot" style="background:{color}"></span>'
        f'Faktor dominan: {row_local["faktor_dominan"]}'
        f'</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col_h2:
    # Rata-rata prevalensi stunting provinsi dan nasional
    provinsi_avg = prov_df_selected["stunting"].mean()
    nasional_avg = df["stunting"].mean()

    # Selisih wilayah terpilih terhadap rata-rata nasional
    selisih = row["stunting"] - nasional_avg

    delta_txt = (
        f"{'+' if selisih > 0 else ''}"
        f"{selisih:.1f} poin dari rata-rata nasional"
    )

    # Rata-rata provinsi dan nasional berada di satu kartu
    render_kpi_card(
        "Prevalensi Stunting",
        f"{row['stunting']:.1f}%",
        delta=delta_txt,
        delta_positive=(selisih < 0),
        note=(
            f"Rata-rata provinsi: {provinsi_avg:.1f}%"
            f"<br>Rata-rata nasional: {nasional_avg:.1f}%"
        ),
        accent="terracotta",
    )

st.markdown("")

# ------------------------------------------------------------
# DETAIL VARIABEL PENYEBAB
# ------------------------------------------------------------

render_section_header(
    "Nilai Variabel Penyebab",
    "Kondisi aktual di wilayah ini",
    None,
)

cols = st.columns(5)

accent_cycle = [
    "terracotta",
    "slate",
    "gold",
    "plum",
    None,
]

for i, var in enumerate(VAR_COLS):
    with cols[i]:
        # Nilai aktual kabupaten/kota
        val = row[var]

        unit = VAR_UNITS[var]
        label = VAR_LABELS[var]

        # Rata-rata nasional
        natl_avg = df[var].mean()

        # Rata-rata provinsi
        prov_avg = prov_df_selected[var].mean()

        render_kpi_card(
            label,
            f"{val:.1f}",
            note=(
                f"{unit}"
                f"<br>Rata-rata provinsi: {prov_avg:.1f}"
                f"<br>Rata-rata nasional: {natl_avg:.1f}"
            ),
            accent=accent_cycle[i],
        )

st.markdown("")

# ------------------------------------------------------------
# LOCAL FEATURE IMPORTANCE CHART
# ------------------------------------------------------------

render_section_header(
    "Kontribusi Tiap Faktor (Local Feature Importance)",
    f"Faktor Dominan di {kab_pilihan}",
    "Nilai ini menunjukkan seberapa besar peran tiap variabel "
    "dalam memprediksi stunting di wilayah ini menurut model GRF, "
    "bukan arah hubungan (naik/turun).",
)

# Ambil nilai Local Feature Importance
importance_vals = {
    label: row_local[label]
    for label in VAR_LABELS.values()
}

sorted_items = sorted(
    importance_vals.items(),
    key=lambda x: x[1],
)

labels_sorted = [item[0] for item in sorted_items]
values_sorted = [item[1] for item in sorted_items]

colors_sorted = [
    FACTOR_COLORS.get(label, "#999999")
    for label in labels_sorted
]

fig = go.Figure(
    go.Bar(
        x=values_sorted,
        y=labels_sorted,
        orientation="h",
        marker=dict(
            color=colors_sorted,
            line=dict(color="white", width=1.5),
        ),
        text=[f"{v:.3f}" for v in values_sorted],
        textposition="outside",
        textfont=dict(
            size=13,
            family="Inter, sans-serif",
        ),
    )
)

fig.update_layout(
    height=300,
    margin=dict(l=10, r=10, t=10, b=10),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(
        showgrid=True,
        gridcolor="#EDE4C8",
        title="Local Feature Importance",
    ),
    yaxis=dict(tickfont=dict(size=13)),
    font=dict(
        family="Inter, sans-serif",
        size=13,
        color="#16302A",
    ),
)

st.plotly_chart(fig, use_container_width=True)

render_insight(
    f"<strong>Rekomendasi arah intervensi:</strong> "
    f"Karena faktor dominan di {kab_pilihan} adalah "
    f"<strong>{row_local['faktor_dominan']}</strong>, "
    "program intervensi yang menyasar faktor ini berpotensi "
    "memberikan dampak lebih besar dibanding program yang seragam "
    "secara nasional. Nilai variabel lain tetap relevan sebagai "
    "faktor pendukung."
)

st.markdown("---")

# ------------------------------------------------------------
# PERBANDINGAN DENGAN KABUPATEN/KOTA LAIN DI PROVINSI YANG SAMA
# ------------------------------------------------------------

render_section_header(
    "Perbandingan dengan Kabupaten/Kota Lain di Provinsi yang Sama",
    f"Posisi {kab_pilihan} dalam {row['provinsi']}",
    None,
)

prov_df = prov_df_selected.sort_values(
    "stunting",
    ascending=False,
)

colors_compare = [
    "#E76F51" if k == kab_pilihan else "#CFC9B4"
    for k in prov_df["kab_kota"]
]

fig2 = go.Figure(
    go.Bar(
        x=prov_df["kab_kota"],
        y=prov_df["stunting"],
        marker=dict(
            color=colors_compare,
            line=dict(color="white", width=1),
        ),
        text=[f"{v:.1f}" for v in prov_df["stunting"]],
        textposition="outside",
        textfont=dict(size=11),
    )
)

fig2.update_layout(
    height=400,
    margin=dict(l=10, r=10, t=10, b=90),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(
        showgrid=True,
        gridcolor="#EDE4C8",
        title="Stunting (%)",
    ),
    xaxis=dict(tickangle=-45),
    font=dict(
        family="Inter, sans-serif",
        size=11,
        color="#16302A",
    ),
)

st.plotly_chart(fig2, use_container_width=True)
