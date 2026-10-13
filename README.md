# Proyek Analisis Data: Bike Sharing Dataset

Analisis data penyewaan sepeda Capital Bikeshare (Washington D.C., 2011-2012) beserta dashboard interaktif Streamlit.

## Struktur Folder
```
submission
├── dashboard
│   ├── dashboard.py
│   ├── day_clean.csv
│   └── main_data.csv
├── data
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Setup Environment
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Di macOS/Linux, aktifkan environment dengan `source venv/bin/activate`.

## Menjalankan Dashboard
```
streamlit run dashboard/dashboard.py
```
Dashboard terbuka di http://localhost:8501.

## Menjalankan Notebook
Buka `notebook.ipynb` dari folder utama proyek (agar path `data/` dan `dashboard/` terbaca), lalu jalankan seluruh sel.

## Deploy ke Streamlit Community Cloud
1. Unggah folder proyek ke repositori GitHub publik. Pastikan `requirements.txt` berada di root repositori.
2. Masuk ke https://share.streamlit.io dengan akun GitHub, lalu klik **Create app**.
3. Pilih repositori, branch `main`, dan isi **Main file path** dengan `dashboard/dashboard.py`.
4. Klik **Deploy** dan tunggu proses instalasi selesai.
5. Salin tautan aplikasi (`https://<nama-app>.streamlit.app`) ke `url.txt`.
