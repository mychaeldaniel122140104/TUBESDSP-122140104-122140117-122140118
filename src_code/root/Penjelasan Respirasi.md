## Penjelasan Mengenai Parameter Filter yang dipilih dan Justifikasi 

---

Tugas Besar saya menggunakan pembersihan sinyal rPPG dan Respirasi Dengan melalui 3 proses tahapan. Terdapat tiga tahap preprocessing:

1. **Median Filter** 
    - Paramater : kernel_size = 5
    - Alasan memilih filter median bertujuan untuk menghilangkan noise impulsif atau Outlier tajam, jadi ibaratnya gelombang menjadi seperti gelombang tidak tajam kembali
    - Alasan memilih paramater ukuran kernel 5 karena kernel 5 cukup efektif untuk mengurangi noise tanpa mengubah bentuk sinyal utama. 
    - jika memilih kernel size 1 2 3 maka filtering tidak ada dilakukan 2 sama 3 masih bisa tapi terlalu kecil dan kernel ibarat jendela, jika kernel 1 maka dia memiliki jendela yang hampir tidak terlihat dan 
    - jika kernel 9 maka bisa menghilangkan detail penting sinya jika terlalu besar, mengubah bentuk asli sinyal

2. **Savitzky-Golay Filter**
    - Parameter : Window_length = 5-11 , poly_order = 3
    - Alasan memilih filter ialah karena filter yang cocok digunakan dengan alasan panjang jendela yang dapat disesuaikan secara dinamis  berdasarkan panjang sinyal (min 5, max 11), dengan orde polinomial 3 untuk fleksibilitas dalam mengikuti bentuk kurva sinyal.
    - alasan memilih parameter : Karena fleksibel dan menjaga keseimbangan antara smoothing dan detail.
    - poly order 3 : cukup untuk menangkap bentuk fisiologis seperti gelombang napas atau pulsa rPPG
    - jika terlalu kecil atau dibawah 5  maka noise tidak tersaring , sinyal terlalu kasar
    - jika lebih dari 11 maka sinyal terlalu harus dan menghapus detail penting 

3. **Bandpass Butterworth Filter**
    - Parameter : 
        - order = 5
        - rPPG : lowcut = 0.7 Hz, highcut = 3.0 Hz
        - Respirasi: lowcut = 0.1 Hz, highcut = 0.5 Hz
    - Alasan : 
    - Butterworth dipilih karena memiliki respons frekuensi halus tanpa ripples (gelombang kecil atau fluktuasi yang tidak diinginkan ), sehingga tidak menimbulkan distorsi tajam pada sinyal.
    - Orde 5 memberikan keseimbangan antara kemiringan transisi (roll-off) dan kestabilan filter.
    - Cutoff frekuensi ditentukan berdasarkan rentang fisiologis:
        - rPPG (detak jantung): 42–180 bpm → 0.7–3.0 Hz
        - Respirasi: 6–30 bpm → 0.1–0.5 Hz
   - Digunakan untuk mengambil frekuensi sinyal biologis yang relevan.
   Alasan memilih parameter : 
   - jika cut off terlalu kecil : dibawah 0.7 hz , maka Sinyal penting bisa hilang karena dianggap noise. Bagian awal atau gelombang lambat dari detak jantung atau respirasi bisa terpotong.
   - jika cutoff terlalu besar : diatas 3hz , maka Noise frekuensi tinggi mengakibatkan gangguan ikut masuk → sinyal jadi tidak stabil.
