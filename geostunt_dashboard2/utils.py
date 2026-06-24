"""
Utilitas pemuatan data dan fungsi bantu untuk dashboard GeoStunt.
Semua nilai metrik mengikuti hasil analisis terbaru pada notebook GRF
(SEC_GWRF_hasil_analisis_terbaru.ipynb) — 10-fold cross validation,
bandwidth=90, local_weight=0.1901, n=490 kab/kota (setelah imputasi
rerata provinsi dari 514 observasi awal).
"""

import json
import html as _html
import streamlit as st
import pandas as pd
import geopandas as gpd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

VAR_COLS = [
    "melahirkan_tidak_difaskes",
    "kemiskinan",
    "konsumsi_protein_per_kapita",
    "pangan_hewani",
    "rls",
]

VAR_LABELS = {
    "melahirkan_tidak_difaskes": "Melahirkan Tidak di Faskes",
    "kemiskinan": "Kemiskinan",
    "konsumsi_protein_per_kapita": "Konsumsi Protein",
    "pangan_hewani": "Pangan Hewani",
    "rls": "RLS",
}

VAR_UNITS = {
    "melahirkan_tidak_difaskes": "proporsi (0–1)",
    "kemiskinan": "%",
    "konsumsi_protein_per_kapita": "gram/kapita/hari",
    "pangan_hewani": "gram/kapita/hari",
    "rls": "tahun",
}

FACTOR_COLORS = {
    "Kemiskinan": "#E63946",
    "Pangan Hewani": "#2A9D8F",
    "RLS": "#E9C46A",
    "Konsumsi Protein": "#457B9D",
    "Melahirkan Tidak di Faskes": "#9D6FB0",
    "Tidak ada data": "#D4D2C8",
}

MODEL_COLORS = {
    "OLS": "#B8B2A0",
    "Random Forest": "#457B9D",
    "GRF": "#E76F51",
}


@st.cache_data
def load_master_data():
    return pd.read_csv(DATA_DIR / "master_data.csv")

@st.cache_data
def load_geo_data():
    gdf = gpd.read_file(DATA_DIR / "kabupaten_full.geojson")
    gdf["faktor_dominan"] = gdf["faktor_dominan"].fillna("Tidak ada data")
    return gdf

@st.cache_data
def load_metrics():
    with open(DATA_DIR / "metrics_summary.json", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_local_importance():
    return pd.read_csv(DATA_DIR / "dominan_df.csv")


def format_number(x, decimals=1):
    return f"{x:,.{decimals}f}".replace(",", ".")


def inject_css():
    css_path = BASE_DIR / "assets" / "style.css"

    with open(css_path, encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )


def render_hero(title, subtitle, badges):
    badge_html = "".join([f'<span class="geostunt-badge">{b}</span>' for b in badges])
    html = (
        f'<div class="geostunt-hero">'
        f'<div class="geostunt-eyebrow">Dashboard Analitik Kebijakan Stunting</div>'
        f'<div class="geostunt-title">{title}</div>'
        f'<div class="geostunt-subtitle">{subtitle}</div>'
        f'<div class="geostunt-badge-row">{badge_html}</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_section_header(eyebrow, title, desc=None):
    st.markdown(f'<div class="section-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if desc:
        st.markdown(f'<div class="section-desc">{desc}</div>', unsafe_allow_html=True)


def render_kpi_card(label, value, note=None, delta=None, delta_positive=True, accent=None):
    delta_html = ""
    if delta:
        cls = "kpi-delta-up" if delta_positive else "kpi-delta-down"
        delta_html = f'<div class="{cls}">{delta}</div>'
    note_html = f'<div class="kpi-note">{note}</div>' if note else ""
    accent_cls = f" accent-{accent}" if accent else ""
    if isinstance(value, (dict, list)):
        json_str = json.dumps(value, ensure_ascii=False, indent=2)
        value_html = f'<pre class="kpi-value" style="white-space:pre-wrap;">{_html.escape(json_str)}</pre>'
    else:
        value_html = f'<div class="kpi-value">{value}</div>'

    parts = [
        f'<div class="kpi-card{accent_cls}">',
        f'<div class="kpi-label">{label}</div>',
        value_html,
    ]
    if delta_html:
        parts.append(delta_html)
    if note_html:
        parts.append(note_html)
    parts.append('</div>')

    st.markdown('\n'.join(parts), unsafe_allow_html=True)


def render_insight(text):
    st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)


def render_warning(text):
    st.markdown(f'<div class="warning-box">{text}</div>', unsafe_allow_html=True)
