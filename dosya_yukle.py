import streamlit as st
import pandas as pd
from analiz import veriyi_isle
# Türkçe karakter içermeyen dosyadan fonksiyonları çağırıyoruz
from veritabani import veritabani_hazirla, kullanici_ekle, giris_kontrol

st.set_page_config(page_title="YouTube Analiz Giriş", page_icon="🔑", layout="wide")

# Veritabanı altyapısını arkada otomatik tetikle
veritabani_hazirla()

if 'giris_yapildi' not in st.session_state:
    st.session_state['giris_yapildi'] = False
if 'aktif_kullanici' not in st.session_state:
    st.session_state['aktif_kullanici'] = None

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1 { color: #1e3a8a; font-family: 'Helvetica Neue', sans-serif; }
    h2, h3 { color: #0f172a; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 🛑 DURUM 1: GİRİŞ YAPILMAMIŞSA (AUTH PANELS)
# ==========================================
if not st.session_state['giris_yapildi']:
    st.title("🔐 YouTube Veri Analiz Platformu")
    st.markdown("Kişisel analiz odanıza erişmek için giriş yapın veya ücretsiz kayıt olun.")
    st.write("---")
    
    sekme_giris, sekme_kayit = st.tabs(["🔑 Giriş Yap", "📝 Hesap Oluştur"])
    
    with sekme_giris:
        st.subheader("Hesabınıza Giriş Yapın")
        g_username = st.text_input("Kullanıcı Adı", key="login_user", placeholder="Kullanıcı adınız...")
        g_password = st.text_input("Şifre", type="password", key="login_pass", placeholder="Şifreniz...")
        
        if st.button("Sisteme Giriş Yap", key="btn_login"):
            if g_username and g_password:
                if giris_kontrol(g_username, g_password):
                    st.session_state['giris_yapildi'] = True
                    st.session_state['aktif_kullanici'] = g_username
                    st.success(f"🎉 Hoş geldin kral {g_username}! Giriş başarılı.")
                    st.rerun()
                else:
                    st.error("❌ Hatalı kullanıcı adı veya şifre girdiniz!")
            else:
                st.warning("⚠️ Lütfen tüm alanları doldurun.")
                
    with sekme_kayit:
        st.subheader("Yeni Bir Hesap Oluşturun")
        k_username = st.text_input("Kullanıcı Adı Seçin", key="register_user", placeholder="Yeni bir kullanıcı adı...")
        k_password = st.text_input("Şifre Seçin", type="password", key="register_pass", placeholder="Güçlü bir şifre...")
        
        if st.button("Kayıt Ol ve Hesap Aç", key="btn_register"):
            if k_username and k_password:
                if kullanici_ekle(k_username, k_password):
                    st.success("✅ Kayıt başarılı! 'Giriş Yap' sekmesinden hesabınıza giriş yapabilirsiniz.")
                else:
                    st.error("❌ Bu kullanıcı adı zaten alınmış! Başka bir ad deneyin.")
            else:
                st.warning("⚠️ Lütfen boş alan bırakmayın.")

# ==========================================
# 🎉 DURUM 2: GİRİŞ YAPILMIŞSA (ANALİZ MERKEZİ)
# ==========================================
else:
    kullanici = st.session_state['aktif_kullanici']
    
    c_sol, c_sag = st.columns([6, 1])
    with c_sol:
        st.title(f"👋 Selam Kral, {kullanici}!")
    with c_sag:
        st.write("")
        if st.button("🚪 Güvenli Çıkış"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
    st.markdown(f"**{kullanici}** hesabına özel yükleme alanı. Verileriniz çıkış yapana kadar hafızada kilitli kalır.")
    st.write("---")

    col1, col2 = st.columns(2)

    # --- 1. İZLEME GEÇMİŞİ ---
    with col1:
        st.subheader("🎬 1. İzleme Geçmişi Yükleme")
        if 'video_df' in st.session_state and st.session_state['video_df'] is not None:
            st.success("🔒 **İzleme Geçmişi Hafızaya Kilitlendi!**")
            if st.button("🔓 İzleme Dosyasını Kaldır", key="sil_video"):
                del st.session_state['video_df']
                st.rerun()
        else:
            video_file = st.file_uploader("izleme geçmişi.json dosyasını bırakın:", type=["json"], key="video_uploader")
            if video_file is not None:
                with st.spinner("İzleme geçmişi işleniyor..."):
                    st.session_state['video_df'] = veriyi_isle(video_file)
                st.rerun()

    # --- 2. ARAMA GEÇMİŞİ ---
    with col2:
        st.subheader("🔍 2. Arama Geçmişi Yükleme")
        if 'arama_df' in st.session_state and st.session_state['arama_df'] is not None:
            st.success("🔒 **Arama Geçmişi Hafızaya Kilitlendi!**")
            if st.button("🔓 Arama Dosyasını Kaldır", key="sil_arama"):
                del st.session_state['arama_df']
                st.rerun()
        else:
            arama_file = st.file_uploader("arama geçmişi.json dosyasını bırakın:", type=["json"], key="arama_uploader")
            if arama_file is not None:
                with st.spinner("Arama dosyası hafızaya alınıyor..."):
                    st.session_state['arama_df'] = pd.read_json(arama_file)
                st.rerun()