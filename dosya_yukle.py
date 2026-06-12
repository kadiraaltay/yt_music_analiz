import streamlit as st
import pandas as pd
from analiz import veriyi_isle

st.set_page_config(page_title="YouTube Analiz Merkezi", page_icon="📥", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .stMetric { background-color: #1e3a8a !important; padding: 20px; border-radius: 15px; }
    .stMetric label { color: #dbeafe !important; font-weight: bold !important; }
    .stMetric div[data-testid="stMetricValue"] { color: #ffffff !important; }
    h1 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("📥 YouTube Veri Yükleme Merkezi")
st.markdown("Dosyalarınızı bir kez yükleyin, hafıza kilidi sayesinde siz silene kadar kesinlikle silinmez.")
st.write("---")

col1, col2 = st.columns(2)

# --- 1. İZLEME GEÇMİŞİ YÜKLEME ---
with col1:
    st.subheader("🎬 1. İzleme Geçmişi Yükleme")
    if 'video_df' in st.session_state and st.session_state['video_df'] is not None:
        st.success("🔒 **İzleme Geçmişi Hafızaya Kilitlendi!**")
        st.info(f"📋 Toplam {len(st.session_state['video_df'])} satır video verisi korunuyor.")
        if st.button("🔓 İzleme Dosyasını Kaldır", key="sil_video"):
            del st.session_state['video_df']
            st.rerun()
    else:
        video_file = st.file_uploader("izleme geçmişi.json dosyasını bırakın:", type=["json"], key="video_uploader")
        if video_file is not None:
            with st.spinner("İzleme geçmişi işleniyor..."):
                st.session_state['video_df'] = veriyi_isle(video_file)
            st.rerun()

# --- 2. ARAMA GEÇMİŞİ YÜKLEME (SIFIR VERİ KAYBI GARANTİLİ) ---
with col2:
    st.subheader("🔍 2. Arama Geçmişi Yükleme")
    if 'arama_df' in st.session_state and st.session_state['arama_df'] is not None:
        st.success("🔒 **Arama Geçmişi Hafızaya Kilitlendi!**")
        st.info(f"📋 Toplam {len(st.session_state['arama_df'])} satır ham veri havuzda bekliyor.")
        if st.button("🔓 Arama Dosyasını Kaldır", key="sil_arama"):
            del st.session_state['arama_df']
            st.rerun()
    else:
        arama_file = st.file_uploader("arama geçmişi.json dosyasını bırakın:", type=["json"], key="arama_uploader")
        if arama_file is not None:
            with st.spinner("Arama dosyası hafızaya alınıyor..."):
                # ANALİZ.PY'YE GİTMEDEN DİREKT HAM VERİYİ ALIYORUZ Kİ VERİ UÇMASIN
                st.session_state['arama_df'] = pd.read_json(arama_file)
            st.rerun()

st.write("---")

if 'video_df' in st.session_state or 'arama_df' in st.session_state:
    if st.button("🗑️ Tüm Sistem Hafızasını Tamamen Sıfırla"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()