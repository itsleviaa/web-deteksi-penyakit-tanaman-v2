import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import cv2
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import os
import tensorflow as tf
from disease_db import CLASS_NAMES, get_disease_detail

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS EKSTERNAL
# ==========================================
st.set_page_config(
    page_title="LeafGuard AI Pro — Multi-Crop Diagnostics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css(file_name: str):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# Inisialisasi Session State
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "history" not in st.session_state:
    st.session_state.history = []

# ==========================================
# 2. SIDEBAR: PENGATURAN TEMA & NAVIGASI
# ==========================================
with st.sidebar:
    st.markdown("## 🌿 LeafGuard AI Pro")
    st.caption("Sistem Diagnosis Penyakit Cabai, Tomat, Padi & Jagung")
    st.divider()

    # Toggle Tema Terang / Gelap
    dark_toggle = st.toggle("🌙 Mode Gelap (Forest Dark)", value=st.session_state.dark_mode)
    st.session_state.dark_mode = dark_toggle

    # Terapkan class dark-theme ke tag <body> via JavaScript ringan
    if st.session_state.dark_mode:
        components.html(
            "<script>window.parent.document.body.classList.add('dark-theme');</script>",
            height=0,
        )
    else:
        components.html(
            "<script>window.parent.document.body.classList.remove('dark-theme');</script>",
            height=0,
        )

    st.divider()

    # Filter Jenis Tanaman (Two-Step Prediction)
    selected_crop = st.selectbox(
        "🌱 Filter Jenis Tanaman",
        ["Deteksi Otomatis (Semua)", "Cabai", "Tomat", "Padi", "Jagung"],
        help="Pilih jenis tanaman spesifik untuk meningkatkan akurasi prediksi dan mencegah salah klasifikasi antarspesies."
    )

    # Pilihan Metode Input Gambar
    input_method = st.radio(
        "📸 Sumber Gambar Daun",
        ["Unggah Foto (Galeri)", "Ambil Foto Langsung (Kamera)"]
    )

    st.divider()
    st.markdown("### 📊 Statistik Sesi")
    st.metric("Total Daun Dianalisis", f"{len(st.session_state.history)} Sampel")

# ==========================================
# 3. LOAD MODEL & FUNGSI GRAD-CAM
# ==========================================
@st.cache_resource
def load_cnn_model():
    model_path = "model_leafguard.h5"
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path)
    return None

model = load_cnn_model()

def generate_gradcam_overlay(img_array: np.ndarray, loaded_model, pred_index: int):
    """Menghasilkan heatmap Grad-CAM untuk menyoroti area bercak penyakit."""
    if loaded_model is None:
        # Simulasi visual heatmap berbasis deteksi area kuning/cokelat jika model belum diload
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        # Masking warna kuning/cokelat khas bercak penyakit
        lower_spot = np.array([10, 40, 40])
        upper_spot = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, lower_spot, upper_spot)
        heatmap = cv2.GaussianBlur(mask, (31, 31), 0)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
        return cv2.addWeighted(img_array, 0.6, heatmap_color, 0.4, 0)

    # Jika model H5 asli tersedia, cari layer Conv2D terakhir
    last_conv_layer = None
    for layer in reversed(loaded_model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            last_conv_layer = layer.name
            break

    if last_conv_layer is None:
        return img_array

    grad_model = tf.keras.models.Model(
        [loaded_model.inputs],
        [loaded_model.get_layer(last_conv_layer).output, loaded_model.output]
    )

    img_tensor = np.expand_dims(img_array / 255.0, axis=0)
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_tensor)
        loss = predictions[:, pred_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-8)
    heatmap = cv2.resize(heatmap.numpy(), (img_array.shape[1], img_array.shape[0]))
    heatmap = np.uint8(255 * heatmap)
    heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)
    return cv2.addWeighted(img_array, 0.6, heatmap_color, 0.4, 0)

def predict_disease(pil_img: Image.Image, crop_filter: str):
    img_resized = pil_img.resize((224, 224))
    img_array = np.array(img_resized)

    if model is not None:
        preds = model.predict(np.expand_dims(img_array / 255.0, axis=0))[0]
    else:
        # Mode Demo Otomatis jika file .h5 belum ditaruh di folder
        np.random.seed(int(np.mean(img_array) * 100))
        preds = np.random.dirichlet(np.ones(len(CLASS_NAMES)) * 0.3)

    # Terapkan filter jenis tanaman jika pengguna memilih spesifik
    filtered_indices = [
        i for i, name in enumerate(CLASS_NAMES)
        if crop_filter == "Deteksi Otomatis (Semua)" or name.startswith(crop_filter)
    ]

    filtered_probs = np.zeros_like(preds)
    for idx in filtered_indices:
        filtered_probs[idx] = preds[idx]

    # Normalisasi ulang probabilitas setelah difilter
    if filtered_probs.sum() > 0:
        filtered_probs = filtered_probs / filtered_probs.sum()

    top3_idx = np.argsort(filtered_probs)[::-1][:3]
    top3_results = [(CLASS_NAMES[i], float(filtered_probs[i] * 100)) for i in top3_idx]
    gradcam_img = generate_gradcam_overlay(img_array, model, top3_idx[0])

    return top3_results, gradcam_img

def export_history_pdf(history_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Laporan Diagnosis Penyakit Tanaman - LeafGuard AI", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Dicetak pada: {datetime.now().strftime('%d-%m-%Y %H:%M')}", ln=True, align="C")
    pdf.ln(8)

    for idx, item in enumerate(history_list, 1):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"{idx}. {item['hasil']} ({item['akurasi']:.1f}%)", ln=True)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 6, f"Waktu: {item['waktu']} | Filter Tanaman: {item['filter']}", ln=True)
        pdf.multi_cell(0, 6, f"Saran Penanganan: {item['saran']}")
        pdf.ln(4)

    return bytes(pdf.output())

# ==========================================
# 4. HERO BANNER UTAMA
# ==========================================
st.markdown("""
<div class="hero-banner">
    <h1>🌿 LeafGuard AI — Multi-Crop Diagnostics</h1>
    <p>Deteksi dini penyakit daun pada <b>Cabai, Tomat, Padi, dan Jagung</b> lengkap dengan visualisasi area infeksi & kalkulator dosis penanganan.</p>
</div>
""", unsafe_allow_html=True)

if model is None:
    st.info("ℹ️ **Info Sistem:** File `model_leafguard.h5` belum ditemukan di direktori. Aplikasi berjalan dalam **Mode Simulasi UI** agar kamu tetap bisa menguji tampilan, Grad-CAM, kalkulator dosis, dan ekspor PDF.")

# ==========================================
# 5. NAVIGASI TAB UTAMA
# ==========================================
tab_scan, tab_history, tab_guide = st.tabs([
    "🔍 Diagnosis Daun",
    "📋 Riwayat & Laporan PDF",
    "📖 Panduan Pengambilan Foto"
])

with tab_scan:
    col_input, col_result = st.columns([1, 1.35], gap="large")

    with col_input:
        st.markdown('<div class="leaf-card">', unsafe_allow_html=True)
        st.subheader("1. Input Citra Daun")

        uploaded_image = None
        if input_method == "Unggah Foto (Galeri)":
            file = st.file_uploader("Pilih gambar daun (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
            if file:
                uploaded_image = Image.open(file).convert("RGB")
        else:
            cam_file = st.camera_input("Arahkan kamera ke permukaan daun")
            if cam_file:
                uploaded_image = Image.open(cam_file).convert("RGB")

        if uploaded_image is not None:
            st.image(uploaded_image, caption="Citra Asli yang Diunggah", use_container_width=True)
            analyze_btn = st.button("🔬 Analisis Penyakit Sekarang")
        else:
            analyze_btn = False
            st.caption("Silakan unggah atau ambil foto daun untuk memulai analisis.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_result:
        if uploaded_image is not None and analyze_btn:
            with st.spinner("Menganalisis pola bercak dan menghasilkan Grad-CAM..."):
                top3, gradcam_overlay = predict_disease(uploaded_image, selected_crop)
                best_label, best_conf = top3[0]
                detail = get_disease_detail(best_label)

                # Simpan ke riwayat sesi
                st.session_state.history.insert(0, {
                    "waktu": datetime.now().strftime("%H:%M:%S"),
                    "filter": selected_crop,
                    "hasil": best_label,
                    "akurasi": best_conf,
                    "saran": detail["kimiawi"] if detail["status"] == "Sakit" else detail["organik"]
                })

            # Kartu Hasil Diagnosis Utama
            st.markdown('<div class="leaf-card">', unsafe_allow_html=True)
            st.markdown(f'<span class="plant-badge">Komoditas: {detail["tanaman"]}</span>', unsafe_allow_html=True)
            st.subheader(f"Hasil: {best_label}")

            if best_conf < 60.0:
                st.markdown(
                    '<div class="warning-box">⚠️ <b>Tingkat Keyakinan Rendah (<60%):</b> Gambar kurang fokus atau pencahayaan terlalu gelap. Disarankan mengambil ulang foto lebih dekat ke daun.</div>',
                    unsafe_allow_html=True
                )

            # Tampilan Side-by-Side: Asli vs Grad-CAM Heatmap
            img_c1, img_c2 = st.columns(2)
            with img_c1:
                st.image(uploaded_image.resize((224, 224)), caption="Input Diproses (224x224)", use_container_width=True)
            with img_c2:
                st.image(gradcam_overlay, caption="Grad-CAM (Fokus Bercak AI)", use_container_width=True)

            # Top-3 Confidence Score
            st.markdown("#### 📊 Top-3 Kemungkinan Diagnosis")
            for label_item, prob_item in top3:
                st.write(f"**{label_item}** — `{prob_item:.1f}%`")
                st.progress(min(int(prob_item), 100))
            st.markdown('</div>', unsafe_allow_html=True)

            # Kartu Rekomendasi Penanganan & Kalkulator Dosis
            st.markdown('<div class="leaf-card">', unsafe_allow_html=True)
            st.subheader("🩺 Rekomendasi Penanganan & Dosis")

            t_gejala, t_solusi, t_dosis = st.tabs(["Gejala Khas", "Penanganan Organik & Kimiawi", "🧮 Kalkulator Dosis"])
            with t_gejala:
                st.write(f"**Ciri Visual:** {detail['gejala']}")
                st.write(f"**Pencegahan:** {detail['pencegahan']}")

            with t_solusi:
                st.success(f"**🌱 Penanganan Organik / Hayati:**\n\n{detail['organik']}")
                st.info(f"**🧪 Penanganan Kimiawi:**\n\n{detail['kimiawi']}")

            with t_dosis:
                if detail["status"] == "Sehat":
                    st.write("Tanaman terdeteksi sehat, tidak diperlukan takaran obat/fungisida.")
                else:
                    luas_lahan = st.number_input("Masukkan Luas Lahan Terdampak (m²):", min_value=1, max_value=10000, value=100, step=10)
                    total_air = luas_lahan * detail["air_liter_per_m2"]
                    total_obat = total_air * detail["dosis_ml_per_liter"]

                    m1, m2 = st.columns(2)
                    m1.metric("Kebutuhan Air Pelarut", f"{total_air:.1f} Liter")
                    m2.metric("Takaran Obat / Fungisida", f"{total_obat:.1f} ml")
                    st.caption(f"*Estimasi berdasarkan dosis standar {detail['dosis_ml_per_liter']} ml/liter air.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="leaf-card" style="text-align:center; padding: 3.5rem 1.5rem;">
                <h3>Menunggu Sampel Daun 🍃</h3>
                <p>Hasil diagnosis, heatmap Grad-CAM, skor keyakinan Top-3, serta kalkulator dosis penanganan akan muncul di panel ini.</p>
            </div>
            """, unsafe_allow_html=True)

with tab_history:
    st.markdown('<div class="leaf-card">', unsafe_allow_html=True)
    st.subheader("📋 Riwayat Diagnosis Sesi Ini")

    if len(st.session_state.history) == 0:
        st.info("Belum ada daun yang dianalisis pada sesi ini.")
    else:
        df_hist = pd.DataFrame(st.session_state.history)
        st.dataframe(df_hist, use_container_width=True)

        c_dl, c_clr = st.columns([2, 1])
        with c_dl:
            pdf_bytes = export_history_pdf(st.session_state.history)
            st.download_button(
                label="📄 Unduh Laporan Diagnosis Lengkap (PDF)",
                data=pdf_bytes,
                file_name=f"Laporan_LeafGuard_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
        with c_clr:
            if st.button("🗑️ Bersihkan Riwayat"):
                st.session_state.history = []
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with tab_guide:
    st.markdown('<div class="leaf-card">', unsafe_allow_html=True)
    st.subheader("📸 Tips Mengambil Foto Daun agar Akurasi Maksimal")
    st.markdown("""
    1. **Fokus pada Satu Helai Daun:** Pastikan daun yang memiliki gejala bercak berada di tengah bingkai dan memenuhi sekitar 70% area foto.
    2. **Pencahayaan Alami:** Ambil foto di bawah cahaya matahari pagi/sore yang merata. Hindari bayangan tangan menutupi daun.
    3. **Latar Belakang Kontras:** Jika memungkinkan, gunakan latar belakang polos (tanah gelap atau kertas) agar model CNN tidak bingung membedakan daun sakit dengan daun di belakangnya.
    4. **Gunakan Filter Tanaman:** Pilih jenis tanaman (**Cabai, Tomat, Padi, atau Jagung**) di sidebar kiri sebelum menekan tombol analisis.
    """)
    st.markdown('</div>', unsafe_allow_html=True)