
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
TUBESDSP/
│
├── src_code/
│   └── root/
│       ├── main.py                       # Entry point aplikasi
│       ├── app.py                        # Inisialisasi dan pemanggilan GUI
│       ├── utils.py                      # Fungsi-fungsi utilitas umum
│       ├── signal_filter.py              # Implementasi filtering (median, savgol, bandpass)
│       ├── rppg_signal.py                # Ekstraksi sinyal rPPG (dahi)
│       ├── respirasi_signal.py           # Ekstraksi sinyal respirasi (bahu)
│
│       ├── core/                         # Paket internal (opsional: logika utama)
│       │   └── __init__.py
│
│       ├── modules/                      # Komponen modular (GUI dan logic)
│       │   ├── layout.py                 # Layout antarmuka (Tkinter)
│       │   ├── plotting.py               # Plotting matplotlib ke GUI
│       │   ├── recording.py              # Fungsi simpan sinyal dan grafik
│       │   ├── video_processing.py       # Proses kamera, ekstraksi frame & update sinyal
│       │   └── __init__.py
│
│       ├── saved_signals/               # Folder output data dan grafik
│       │   ├── sinyal_data_*.txt
│       │   ├── signal_analysis_*.png
│
├── .gitignore                           # Ignore file untuk Git
├── README.md                            # Dokumentasi proyek
├── requirements.txt                     # Dependensi Python

```

---

## ✅ Kebutuhan Sistem

- Python 3.10+
- Webcam internal/eksternal
- OS: Windows / Linux / macOS

---

## lOGbook
| Minggu Ke | Aktivitas                                                                                                                                              | Deskripsi                                                                                                                                                                                       |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1**     | Inisialisasi GitHub                                                                                                                                    | Membuat repository GitHub sebagai tempat penyimpanan dan kolaborasi kode proyek secara versi terkendali.                                                                                        |
| **3**     | Pembuatan GUI awal dan eksplorasi filter sinyal                                                                                                        | Mendesain antarmuka pengguna (GUI) dan melakukan eksperimen dengan berbagai filter (Median, SG, Butterworth) untuk sinyal rPPG.                                                                 |
| **4**     | - Integrasi model `blaze_face_short_range` & `pose_landmarker`<br>- Finalisasi desain GUI<br>- Refactor fungsi GUI<br>- Penyusunan laporan di Overleaf | Menggabungkan deteksi wajah dan bahu dengan model Blaze dan Pose Landmarker, menyempurnakan tampilan GUI, merapikan struktur fungsi GUI, serta mulai menyusun laporan akhir proyek di Overleaf. |

## 🏁 Penutup

Proyek ini merupakan hasil kerja tim sebagai bagian dari **Tugas Besar Pengolahan Sinyal Digital**.  
Terima kasih kepada dosen pengampu atas bimbingannya dalam memahami aplikasi nyata dari analisis sinyal fisiologis secara non-invasif.
