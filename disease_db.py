# Daftar lengkap kelas untuk 4 jenis tanaman: Cabai, Tomat, Padi, Jagung
CLASS_NAMES = [
    "Cabai - Bercak Daun Bakteri (Bacterial Spot)",
    "Cabai - Sehat (Healthy)",
    "Jagung - Bercak Daun Abu-abu (Gray Leaf Spot)",
    "Jagung - Hawar Daun (Northern Leaf Blight)",
    "Jagung - Karat Daun (Common Rust)",
    "Jagung - Sehat (Healthy)",
    "Padi - Bercak Cokelat (Brown Spot)",
    "Padi - Blas Daun (Leaf Blast)",
    "Padi - Hawar Daun Bakteri (Bacterial Leaf Blight)",
    "Tomat - Bercak Kering (Early Blight)",
    "Tomat - Busuk Daun (Late Blight)",
    "Tomat - Sehat (Healthy)",
    "Tomat - Virus Kuning Keriting (Yellow Leaf Curl Virus)"
]
DISEASE_INFO = {
    "Cabai - Bercak Daun Bakteri (Bacterial Spot)": {
        "tanaman": "Cabai",
        "status": "Sakit",
        "gejala": "Bercak kecil berair pada daun yang berubah menjadi cokelat tua hingga hitam dengan tepi kuning. Daun mudah rontok.",
        "organik": "Semprotkan ekstrak bawang putih atau bakterisida nabati berbahan Pseudomonas fluorescens.",
        "kimiawi": "Gunakan bakterisida berbahan aktif Tembaga Hidroksida atau Streptomisin Sulfat.",
        "pencegahan": "Gunakan benih sehat, hindari penyiraman dari atas (overhead), dan lakukan rotasi tanaman.",
        "dosis_ml_per_liter": 2.0,  # ml obat per liter air
        "air_liter_per_m2": 0.05    # kebutuhan larutan semprot per m2
    },
    "Jagung - Hawar Daun (Northern Leaf Blight)": {
        "tanaman": "Jagung",
        "status": "Sakit",
        "gejala": "Bercak memanjang berbentuk seperti cerutu berwarna abu-abu kehijauan hingga cokelat pada daun bagian bawah.",
        "organik": "Aplikasi agen hayati Trichoderma sp. pada pangkal batang dan pemangkasan daun bawah yang terinfeksi.",
        "kimiawi": "Semprotkan fungisida berbahan aktif Mankozeb atau Azoksistrobin saat gejala awal muncul.",
        "pencegahan": "Tanam varietas tahan hawar dan bersihkan sisa jerami jagung pascapanen.",
        "dosis_ml_per_liter": 2.5,
        "air_liter_per_m2": 0.06
    },
    "Jagung - Karat Daun (Common Rust)": {
        "tanaman": "Jagung",
        "status": "Sakit",
        "gejala": "Muncul bintik-bintik kecil menonjol (pustul) berwarna cokelat kemerahan seperti karat di kedua permukaan daun.",
        "organik": "Semprot larutan bubur Bordeaux organik atau minyak mimba (Neem Oil) 5 ml/liter.",
        "kimiawi": "Gunakan fungisida berbahan aktif Propikonazol atau Difenokonazol.",
        "pencegahan": "Atur jarak tanam agar sirkulasi udara lancar dan kelembapan tidak terlalu tinggi.",
        "dosis_ml_per_liter": 1.5,
        "air_liter_per_m2": 0.06
    },
    "Padi - Blas Daun (Leaf Blast)": {
        "tanaman": "Padi",
        "status": "Sakit",
        "gejala": "Bercak berbentuk belah ketupat dengan ujung meruncing, bagian tengah berwarna abu-abu keputihan dan tepi cokelat.",
        "organik": "Semprotkan agensia hayati Corynebacterium atau ekstrak daun sirih hutan.",
        "kimiawi": "Aplikasikan fungisida sistemik berbahan aktif Trisiklazol atau Isoprotiolan.",
        "pencegahan": "Hindari pemupukan Nitrogen (Urea) berlebihan dan jaga genangan air sawah tetap stabil.",
        "dosis_ml_per_liter": 2.0,
        "air_liter_per_m2": 0.05
    },
    "Padi - Hawar Daun Bakteri (Bacterial Leaf Blight)": {
        "tanaman": "Padi",
        "status": "Sakit",
        "gejala": "Garis basah kekuningan dimulai dari tepi atau ujung daun yang meluas hingga daun mengering (kresek).",
        "organik": "Gunakan pupuk hayati pembenah tanah dan semprot Paenibacillus polymyxa.",
        "kimiawi": "Semprotkan bakterisida berbahan aktif Tembaga Oksiklorida atau Asam Oksolinik.",
        "pencegahan": "Keringkan lahan secara berkala (intermittent irrigation) dan kurangi pupuk N saat musim hujan.",
        "dosis_ml_per_liter": 2.5,
        "air_liter_per_m2": 0.05
    },
    "Tomat - Bercak Kering (Early Blight)": {
        "tanaman": "Tomat",
        "status": "Sakit",
        "gejala": "Bercak cokelat tua melingkar konsentris seperti papan target pada daun tua bagian bawah.",
        "organik": "Pangkas daun terinfeksi dan semprotkan fungisida hayati Bacillus subtilis.",
        "kimiawi": "Gunakan fungisida berbahan aktif Klorotalonil atau Mankozeb secara bergantian.",
        "pencegahan": "Pasang mulsa plastik perak-hitam untuk mencegah percikan spora dari tanah ke daun.",
        "dosis_ml_per_liter": 2.0,
        "air_liter_per_m2": 0.05
    },
    "Tomat - Busuk Daun (Late Blight)": {
        "tanaman": "Tomat",
        "status": "Sakit",
        "gejala": "Bercak basah berwarna hijau gelap hingga cokelat kehitaman yang menyebar sangat cepat, sering disertai jamur putih di bawah daun.",
        "organik": "Segera musnahkan tanaman yang terinfeksi parah agar tidak menular ke seluruh kebun.",
        "kimiawi": "Gunakan fungisida berbahan aktif Simoksanil atau Dimetomorf.",
        "pencegahan": "Perbaiki drainase bedengan dan hindari penyiraman pada sore/malam hari.",
        "dosis_ml_per_liter": 2.5,
        "air_liter_per_m2": 0.05
    }
}

def get_disease_detail(label: str):
    if "Sehat" in label:
        tanaman = label.split(" - ")[0]
        return {
            "tanaman": tanaman,
            "status": "Sehat",
            "gejala": f"Daun {tanaman.lower()} tampak hijau segar, tidak ditemukan bercak nekrotik, pustul jamur, maupun perubahan warna abnormal.",
            "organik": "Lanjutkan pemupukan organik cair (POC) rutin setiap 10-14 hari sekali.",
            "kimiawi": "Tidak diperlukan penyemprotan pestisida/fungisida kimia.",
            "pencegahan": "Pertahankan sanitasi kebun, penyiraman teratur, dan pemantauan rutin.",
            "dosis_ml_per_liter": 0.0,
            "air_liter_per_m2": 0.0
        }
    return DISEASE_INFO.get(label, {
        "tanaman": label.split(" - ")[0],
        "status": "Sakit",
        "gejala": "Terdeteksi anomali bercak/perubahan warna pada jaringan daun.",
        "organik": "Pisahkan daun terdampak dan aplikasikan fungisida/bakterisida nabati.",
        "kimiawi": "Konsultasikan dengan penyuluh pertanian setempat untuk aplikasi fungisida spesifik.",
        "pencegahan": "Jaga kebersihan lahan dan atur kelembapan mikro tanaman.",
        "dosis_ml_per_liter": 2.0,
        "air_liter_per_m2": 0.05
    })
