# Tugas Besar Mata Kuliah Pengolahan Sinyal Digital (IF3024)
## Dosen Pengampu: Martin Clinton Tosima Manullang, S.T.,M.T


## (Belum FInall)


## Deskripsi

Program ini merupakan implementasi pemantauan sinyal biologis non-kontak secara real-time, yang bertujuan untuk mengekstraksi dan menampilkan:

* **Sinyal pernapasan (Respirasi)**
* **Sinyal detak jantung berbasis video (rPPG)**

...langsung dari input **kamera webcam**, dengan antarmuka grafis (GUI) interaktif berbasis **Tkinter + Matplotlib**.

Program ini dikembangkan sebagai bagian dari **Tugas Akhir Mata Kuliah Pengolahan Sinyal Digital (IF3024)**.

---

## Fitur Utama

* Realtime **video feed** dari webcam
* Deteksi **landmark bahu** menggunakan **MediaPipe Pose**
* Deteksi **wajah dan ROI dahi** menggunakan **MediaPipe FaceMesh**
* Ekstraksi **sinyal rPPG** dari kanal **Green (G)** wajah
* Ekstraksi **sinyal respirasi** dari pergerakan vertikal bahu
* **Visualisasi grafik sinyal** rPPG dan respirasi
* Estimasi **Heart Rate (HR)** dan **Respiration Rate (RR)** dalam satuan BPM dan Breath/min
* **Tombol START, STOP, dan SIMPAN** data sinyal ke file `.txt`
* **Antarmuka GUI responsif**, dengan gaya gelap (dark mode)

---

## Instalasi

1. **Clone repository** atau salin folder proyek
2. Buat environment Conda (opsional tapi disarankan):

   ```bash
   conda create -n respirasi_rppg_env python=3.10
   conda activate respirasi_rppg_env
   ```
3. Install dependensi:

   ```bash
   pip install -r requirements.txt
   ```

---

## Cara Menjalankan

```bash
python main.py
```

### Alur Penggunaan:

* Tekan tombol **START** untuk memulai feed kamera dan pemrosesan sinyal
* Tekan **STOP** untuk menjeda feed dan analisis
* Tekan **SIMPAN** untuk menyimpan data sinyal ke file `sinyal_data.txt`

---

## Metode dan Teknik

* **Respirasi**: Pergerakan bahu (landmark Y) → filtering → sinyal respirasi
* **rPPG**: Rata-rata warna hijau di dahi → filtering → sinyal detak jantung
* **Filtering**: Menggunakan **bandpass filter**

  * HR: 0.7–3.0 Hz
  * RR: 0.1–0.5 Hz
* **Estimasi HR/RR**: Menghitung puncak sinyal dalam jendela waktu

