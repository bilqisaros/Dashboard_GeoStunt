import streamlit as st

from utils import inject_css, render_section_header, render_insight, load_master_data

st.set_page_config(
    page_title="Tentang Metode - GeoStunt", layout="wide", initial_sidebar_state="expanded"
)
inject_css()

df = load_master_data()

render_section_header(
    "Tentang Metode",
    "Mengapa Geographical Random Forest?",
    "Penjelasan singkat metodologi GeoStunt untuk pembaca yang ingin memahami "
    "dasar analisis tanpa latar belakang statistik mendalam.",
)

# ------------------------------------------------------------ KONSEP DASAR
st.markdown("""
<div class="justify-text">
Stunting bukan masalah dengan satu sebab tunggal yang sama di seluruh Indonesia.
Sebuah daerah bisa mengalami stunting tinggi karena kemiskinan, sementara daerah lain
karena akses pangan hewani yang rendah, atau karena rendahnya tingkat pendidikan ibu.
Model statistik konvensional biasanya mengasumsikan satu hubungan yang sama berlaku
di seluruh wilayah — tetapi asumsi yang tidak realistis untuk negara seluas dan
sebervariasi Indonesia.
</div>
""", unsafe_allow_html=True)

cols = st.columns(4)
steps = [
    ("01", "Random Forest", "Algoritma machine learning yang menggabungkan ratusan pohon keputusan untuk memprediksi suatu nilai, dalam hal ini prevalensi stunting.", "#457B9D"),
    ("02", "Versi Geografis", "GRF membangun satu model Random Forest terpisah untuk setiap kabupaten/kota, hanya menggunakan data dari kabupaten/kota tetangga di sekitarnya.", "#2A9D8F"),
    ("03", "Hasil per Wilayah", "Setiap model lokal menghasilkan nilai kontribusi (importance) untuk tiap variabel, yang menunjukkan faktor mana yang paling berperan di wilayah tersebut.", "#E9C46A"),
    ("04", "Peta Faktor Dominan", "Hasil dari seluruh model lokal disatukan menjadi peta yang menunjukkan faktor dominan stunting di setiap kabupaten/kota di Indonesia.", "#E76F51"),
]
for col, (num, title, desc, color) in zip(cols, steps):
    with col:
        st.markdown(
            f'<div class="step-card" style="border-top:3px solid {color};">'
            f'<div class="step-number" style="color:{color};">{num}</div>'
            f'<div class="step-title">{title}</div>'
            f'<div class="step-desc">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("")

render_insight(
    "<strong>Analogi sederhana:</strong> Bayangkan model regresi biasa seperti dokter "
    "umum yang memberi resep yang sama untuk semua pasien demam. GRF lebih seperti "
    "tim dokter yang masing-masing memeriksa pasien di kecamatannya sendiri, sehingga "
    "diagnosisnya lebih sesuai dengan kondisi lokal, meski tetap mengacu pada ilmu "
    "kedokteran yang sama."
)

st.markdown("---")

# ------------------------------------------------------------ VARIABEL
render_section_header(
    "Variabel yang Digunakan",
    "Satu variabel target dan lima variabel penyebab",
    None
)

var_table = """
| Aspek | Variabel | Satuan | Sumber Data |
|---|---|---|---|
| Kesehatan | Persentase Stunting | Persen (%) | SSGI 2024, Kementerian Kesehatan RI |
| Fasilitas Kesehatan | Persentase Persalinan Tidak di Fasilitas Kesehatan | Proporsi (0–1) | Badan Pusat Statistik (BPS) |
| Kesejahteraan | Persentase Penduduk Miskin | Persen (%) | Badan Pusat Statistik (BPS) |
| Ketahanan Pangan | Konsumsi Protein per Kapita | Gram/Kapita/Hari | Badan Pangan Nasional (BAPANAS) |
| Ketahanan Pangan | Konsumsi Pangan Hewani | Gram/Kapita/Hari | Badan Pangan Nasional (BAPANAS) |
| Pendidikan | Rata-rata Lama Sekolah (RLS) | Tahun | Badan Pusat Statistik (BPS) |
"""
st.markdown(var_table)

st.caption(
    f"Analisis menggunakan data {len(df)} dari 522 kabupaten/kota di Indonesia. "
    "Data awal mencakup 513 kabupaten/kota; nilai yang hilang pada variabel stunting, "
    "melahirkan tidak di faskes, konsumsi protein, dan pangan hewani diimputasi "
    "menggunakan rerata kabupaten/kota lain dalam provinsi yang sama, "
    "sehingga diperoleh 489 observasi lengkap untuk pemodelan."
)

st.markdown("---")

# ------------------------------------------------------------ TAHAPAN ANALISIS
render_section_header("Tahapan Analisis", "Dari data mentah hingga peta faktor dominan", None)

st.markdown(
    """
    1. **Pembersihan data** : Menggabungkan enam sumber data resmi pemerintah berdasarkan nama kabupaten/kota,
       menyamakan format penulisan nama wilayah (30 nama diharmonisasi ke shapefile), dan mengimputasi
       nilai yang hilang menggunakan rerata per provinsi — pendekatan yang mempertahankan lebih banyak
       wilayah dibanding penghapusan baris.
    2. **Pencarian koordinat** : Menghitung titik tengah (centroid) tiap wilayah dari batas administrasi
       resmi (shapefile Batas Kabupaten 2024) untuk keperluan analisis spasial.
    3. **Uji model dasar** : Menjalankan regresi linear (OLS) sebagai pembanding, lalu menguji apakah
       residualnya menunjukkan pola spasial yang tidak tertangkap (Moran's I = 0,3152; p < 0,001).
    4. **Pembanding Random Forest global** : Menjalankan Random Forest tanpa komponen spasial sebagai
       tahap pembanding kedua (10-fold CV).
    5. **Pemodelan GRF** : Menjalankan Geographical Random Forest dengan parameter bandwidth=81 dan
       local_weight=0,1985 yang dioptimalkan secara otomatis melalui ISA, divalidasi dengan 10-fold
       cross validation.
    6. **Ekstraksi faktor dominan** : Mengambil nilai kontribusi (local feature importance) tiap
       variabel di setiap kabupaten/kota, merata-ratakannya lintas fold, lalu menentukan faktor
       dengan kontribusi tertinggi sebagai faktor dominan wilayah tersebut.
    """
)

st.markdown("---")

# ------------------------------------------------------------ REFERENSI
render_section_header("Referensi Metodologi", "Dasar ilmiah yang digunakan", None)

st.markdown(
    """
    - Georganos, S., Grippa, T., Gadiaga, A. N., Linard, C., Lennert, M., Vanhuysse, S., Mboga, N.,
      Wolff, E., & Kalogirou, S. (2021). Geographical random forests: a spatial extension of the
      random forest algorithm to address spatial heterogeneity in remote sensing and population
      modelling. *Geocarto International*, 36(2), 121-136.
    - Georganos, S., & Kalogirou, S. (2022). A Forest of Forests: A Spatially Weighted and
      Computationally Efficient Formulation of Geographical Random Forests. *ISPRS International
      Journal of Geo-Information*, 11(9), 471.
    - Sun, K., Zhou, R. Z., Kim, J., & Hu, Y. (2024). An improved Python Geographical Random Forest
      model and case studies in public health and natural disasters. *Transactions in GIS*.
    """
)

render_insight(
    "Penelitian ini menggunakan <strong>Geographical Random Forest (GRF)</strong>. "
    "GRF membangun sub-model Random Forest lokal"
    "di tiap titik observasi, diimplementasikan "
    "melalui package <strong>PyGRF</strong> (Sun et al., 2024)."
)
