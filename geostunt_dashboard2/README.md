# GeoStunt

**Dashboard Analitik Spasial Faktor Dominan Stunting Berbasis Geographical Random Forest
sebagai Pendukung Intervensi Presisi Kabupaten/Kota di Indonesia**

Dashboard ini menampilkan hasil analisis Geographical Random Forest (GRF) terhadap data
stunting 404 kabupaten/kota di Indonesia, untuk mendukung argumen bahwa intervensi
penurunan stunting perlu disesuaikan dengan faktor dominan di tiap wilayah, bukan
diterapkan secara seragam secara nasional.

## Struktur Proyek

```
geostunt_dashboard/
├── Beranda.py                   # Halaman utama (ringkasan eksekutif)
├── pages/
│   ├── 1_Peta_Nasional.py       # Peta choropleth interaktif
│   ├── 2_Perbandingan_Model.py  # OLS vs Random Forest vs GRF
│   ├── 3_Profil_Kabupaten.py    # Detail per kabupaten/kota
│   └── 4_Tentang_Metode.py      # Penjelasan metodologi
├── utils.py                     # Fungsi bantu & pemuatan data
├── assets/
│   └── style.css                # Styling kustom
├── data/
│   ├── master_data.csv           # Data 404 kab/kota + local importance
│   ├── kabupaten_full.geojson    # Geometri 522 kab/kota (termasuk tanpa data)
│   ├── dominan_df.csv            # Rata-rata local feature importance per kab/kota
│   └── metrics_summary.json      # Metrik performa model (OLS, RF, GRF)
├── .streamlit/
│   └── config.toml               # Tema warna aplikasi
└── requirements.txt
```

## Menjalankan Secara Lokal

```bash
pip install -r requirements.txt
streamlit run Beranda.py
```

## Deploy ke Streamlit Community Cloud

1. Push seluruh folder ini ke repository GitHub (publik atau privat).
2. Buka [share.streamlit.io](https://share.streamlit.io) dan login dengan akun GitHub.
3. Klik **New app**, pilih repository, branch, dan set **Main file path** ke `Beranda.py`.
4. Klik **Deploy**. Streamlit Cloud akan otomatis membaca `requirements.txt`.

Tidak ada secrets atau API key yang dibutuhkan -- seluruh data sudah disimpan statis
dalam folder `data/`.

## Sumber Data

- Prevalensi stunting: Survei Status Gizi Indonesia (SSGI) 2024
- Persentase penduduk miskin: Badan Pusat Statistik (BPS)
- Konsumsi pangan hewani & protein per kapita: Badan Pangan Nasional (BAPANAS)
- Rata-rata lama sekolah: Badan Pusat Statistik (BPS)
- Persalinan tidak di fasilitas kesehatan: Badan Pusat Statistik (BPS)
- Batas administrasi kabupaten/kota: LapakGIS 2024

## Metodologi

Analisis menggunakan Geographical Random Forest (GRF), bukan Geographically Weighted
Random Forest (GWRF). Implementasi menggunakan package PyGRF dengan parameter bandwidth
dan local weight yang dioptimalkan otomatis melalui Incremental Spatial Autocorrelation
(ISA), divalidasi dengan 10-fold cross validation.

Referensi utama:

- Georganos et al. (2019). *Geocarto International*, 36(2), 121-136.
- Georganos & Kalogirou (2022). *ISPRS International Journal of Geo-Information*, 11(9), 471.
- Sun et al. (2024). *Transactions in GIS*.
