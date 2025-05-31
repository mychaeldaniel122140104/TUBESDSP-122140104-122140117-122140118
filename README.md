
# Tugas Besar Mata Kuliah Pengolahan Sinyal Digital (IF3024)
## Pemantauan Sinyal rPPG dan Respirasi Real-Time Berbasis Webcam
### Dosen Pengampu: Martin Clinton Tosima Manullang, S.T., M.T

---

### 👥 Anggota Tim:
- Fajrul Ramadhana Aqsa (122140118)  
- Michael Daniel N (122140104)  
- Ichsan Kuntadi Baskara (122140117)  

**Institusi**: Institut Teknologi Sumatera (ITERA)

---

## 🧠 Deskripsi

Program ini merupakan implementasi **pemantauan sinyal biologis non-kontak secara real-time**, yang bertujuan untuk mengekstraksi dan menampilkan:

- **Sinyal Respirasi (Pernapasan)**
- **Sinyal Detak Jantung berbasis rPPG (Remote Photoplethysmography)**

Pemrosesan dilakukan langsung melalui input **kamera webcam**, dengan antarmuka grafis (GUI) berbasis **Tkinter**, dan visualisasi sinyal menggunakan **Matplotlib**.

Program ini dikembangkan sebagai bagian dari **Tugas Besar Mata Kuliah Pengolahan Sinyal Digital (IF3024)**.

---

## 🚀 Fitur Utama

- Real-time **video feed** dari webcam  
- Deteksi **landmark bahu** via **MediaPipe Pose**  
- Deteksi **ROI dahi** via **MediaPipe FaceMesh**  
- Ekstraksi sinyal **rPPG** dari kanal **Green (G)** wajah  
- Ekstraksi sinyal **respirasi** dari pergerakan vertikal bahu  
- Estimasi **Heart Rate (HR)** dan **Respiration Rate (RR)**  
- **Visualisasi grafik interaktif** (Matplotlib embedded dalam GUI)  
- Tombol: **START**, **STOP**, **SIMPAN**  
- **Dark mode GUI** yang responsif  
- **Perekaman 30 detik** sinyal + ekspor gambar grafik `.png` dan data `.txt`

---

## ⚙️ Instalasi

1. **Clone repository** atau salin folder proyek  
2. Buat dan aktifkan environment virtual:

### 💻 Windows/Linux/macOS (Recommended - Conda)

```bash
conda create -n respirasi_rppg_env python=3.10
conda activate respirasi_rppg_env
```

**Atau dengan venv:**

```bash
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate        # Windows
```

3. Install semua dependensi:

```bash
pip install -r requirements.txt
```

---

## ▶️ Cara Menjalankan Program

Pastikan kamu berada di direktori utama (yang berisi `main.py`) : cd TUBESDSP-122140104-122140117-122140118\src_code\root>, lalu jalankan:

```bash
python main.py
```

### 📌 Alur Penggunaan Aplikasi:
1. Tekan tombol **START** → Memulai pemrosesan video dan sinyal
2. Tekan tombol **STOP** → Menghentikan proses dan kamera
3. Tekan tombol **SIMPAN** → Menyimpan hasil sinyal ke file `.txt` + grafik `.png`

---

## 🧪 Metodologi & Teknik yang Digunakan

| Komponen     | Teknik/Algoritma        | Deskripsi Singkat                                                 |
|--------------|--------------------------|--------------------------------------------------------------------|
| **Respirasi** | Y-axis bahu (Pose Landmark) | Diambil dari rata-rata posisi vertikal bahu kiri dan kanan         |
| **rPPG**      | ROI warna hijau wajah     | Rata-rata nilai kanal G (green) di area dahi                      |
| **Filtering** | Median → Savitzky-Golay → Butterworth Bandpass | Membersihkan noise & ekstraksi frekuensi jantung/pernapasan      |
| **Estimasi HR/RR** | Peak detection        | Menghitung jumlah puncak per durasi waktu (30 detik)              |

### 🧰 Rangkaian Filter:
1. **Median Filter** – menghapus noise lonjakan (spike)
2. **Savitzky-Golay Filter** – smoothing sinyal
3. **Butterworth Bandpass Filter** – seleksi frekuensi:
   - HR: 0.7–3.0 Hz (42–180 BPM)
   - RR: 0.1–0.5 Hz (6–30 BPM)

---

## 📁 Struktur Proyek

```
Tubes-PengolahanSinyal/
│
├── main.py
├── gui.py
├── signal_filter.py
├── rppg_signal.py
├── respirasi_signal.py
│
├── modules/
│   ├── plotting.py
│   ├── layout.py
│   ├── video_processing.py
│   └── recording.py
│
├── output/
│   ├── sinyal_data.txt
│   ├── plot_hr.png
│   └── plot_rr.png
│
├── requirements.txt
└── README.md
```

---

## ✅ Kebutuhan Sistem

- Python 3.10+
- Webcam internal/eksternal
- OS: Windows / Linux / macOS

---

## 🏁 Penutup

Proyek ini merupakan hasil kerja tim sebagai bagian dari **Tugas Besar Pengolahan Sinyal Digital**.  
Terima kasih kepada dosen pengampu atas bimbingannya dalam memahami aplikasi nyata dari analisis sinyal fisiologis secara non-invasif.
