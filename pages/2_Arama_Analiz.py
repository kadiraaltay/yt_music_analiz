import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Gelişmiş Arama Analizi", page_icon="🔍", layout="wide")

# Turkuaz/Mavi Merak Teması CSS
st.markdown("""
    <style>
    .main { background-color: #f0fdfa; }
    .stMetric { 
        background-color: #0d9488 !important; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1); 
    }
    .stMetric label { color: #ccfbf1 !important; font-weight: bold !important; }
    .stMetric div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 24px !important; }
    h1 { color: #0d9488; font-family: 'Helvetica Neue', sans-serif; }
    h3 { color: #0f766e; }
    </style>
    """, unsafe_allow_html=True)

if 'arama_df' in st.session_state and st.session_state['arama_df'] is not None:
    try:
        raw_df = st.session_state['arama_df'].copy()
        
        # 1. VERİYİ REKLAM VE İZLEME GEÇMİŞİ KALINTILARINDAN ARINDIRMA
        video_ve_reklam_ekleri = ['videoyu izlediniz', 'izlenen video', 'reklam', 'indirim', 'sepetine göre', 'kampanya']
        raw_df['title_clean'] = raw_df['title'].astype(str)
        izleme_mi = raw_df['title_clean'].str.contains('|'.join(video_ve_reklam_ekleri), case=False, na=False)
        arama_df = raw_df[~izleme_mi].copy()
        
        # Ön ekleri ve arka ekleri temizleme
        arama_df['Arama Terimi'] = arama_df['title_clean']
        arama_df['Arama Terimi'] = arama_df['Arama Terimi'].str.replace('Şunu aradınız: ', '', case=False, regex=False)
        arama_df['Arama Terimi'] = arama_df['Arama Terimi'].str.replace('Aranan: ', '', case=False, regex=False)
        arama_df['Arama Terimi'] = arama_df['Arama Terimi'].str.replace(' araması yaptınız', '', case=False, regex=False)
        arama_df['Arama Terimi'] = arama_df['Arama Terimi'].str.replace(' aratıldı', '', case=False, regex=False)
        arama_df['Arama Terimi'] = arama_df['Arama Terimi'].str.strip()
        
        arama_df = arama_df.dropna(subset=['Arama Terimi'])
        arama_df = arama_df[arama_df['Arama Terimi'] != ""]

        # --- YAPAY ZEKA KATEGORİZE ETME ALGORİTMASI ---
        def kategori_ata(metin):
            metin_low = str(metin).lower()
            yazilim_anahtar = ['devops', 'python', 'sql', 'git', 'github', 'kod', 'yazılım', 'programlama', 'veritabanı', 'docker', 'api', 'html', 'css', 'hata', 'error']
            oyun_anahtar = ['efootball', 'gta', 'fifa', 'pes', 'oyun', 'game', 'gameplay', 'twitch', 'easter gamers', 'csgo', 'valorant', 'pubg']
            egitim_anahtar = ['mikroişlemciler', 'ders', 'hoca', 'üniversite', 'keil', 'matematik', 'fizik', 'vize', 'final', 'ödev', 'konuları']
            
            if any(k in metin_low for k in yazilim_anahtar):
                return '💻 Yazılım & Teknoloji'
            elif any(k in metin_low for k in oyun_anahtar):
                return '🎮 Oyun & Gaming'
            elif any(k in metin_low for k in egitim_anahtar):
                return '📚 Eğitim & Ders'
            else:
                return '🌐 Diğer / Genel Merak'

        arama_df['Kategori'] = arama_df['Arama Terimi'].apply(kategori_ata)

        st.title("🔍 Gelişmiş YouTube Arama Odası")
        st.markdown("Arama istatistikleriniz, ilgi alanlarınız ve kelime haritanız.")
        st.write("---")

        # --- SOL MENÜ GELİŞMİŞ FİLTRELERİ ---
        st.sidebar.header("⚙️ Gelişmiş Arama Filtreleri")
        
        yillar = sorted(arama_df['Yıl'].unique().tolist(), reverse=True) if 'Yıl' in arama_df.columns and not arama_df['Yıl'].empty else []
        secilen_yil = st.sidebar.selectbox("Yıl Seçin", ["Tüm Zamanlar"] + yillar)
        if secilen_yil != "Tüm Zamanlar":
            arama_df = arama_df[arama_df['Yıl'] == secilen_yil]
            
        kategoriler = arama_df['Kategori'].unique().tolist() if 'Kategori' in arama_df.columns else []
        secilen_kat = st.sidebar.multiselect("Kategorileri Filtrele", kategoriler, default=kategoriler)
        arama_df = arama_df[arama_df['Kategori'].isin(secilen_kat)]

        # --- ÜST METRİKLER ---
        toplam_arama = len(arama_df)
        en_populer_kat = arama_df['Kategori'].mode()[0] if not arama_df['Kategori'].empty else "Bilinmiyor"
        
        c1, c2 = st.columns(2)
        with c1: st.metric("🔎 Filtrelenmiş Arama Sayısı", f"{toplam_arama:,} kez")
        with c2: st.metric("👑 En Çok İlgi Duyduğun Alan", en_populer_kat)
        
        st.write("---")
        
        if toplam_arama > 0:
            # --- GRAFİKLER BÖLÜMÜ ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 İlgi Alanları Dağılımı (Kategoriler)")
                kat_veri = arama_df['Kategori'].value_counts().reset_index()
                kat_veri.columns = ['Kategori', 'Arama Sayısı']
                fig_kat = px.pie(kat_veri, values='Arama Sayısı', names='Kategori', 
                                 color_discrete_sequence=px.colors.sequential.Teal_r, hole=0.4)
                st.plotly_chart(fig_kat, use_container_width=True)
                
            with col2:
                st.subheader("🏆 En Çok Arattığın İlk 10 Terim")
                top_searches = arama_df['Arama Terimi'].value_counts().head(10).reset_index()
                top_searches.columns = ['Arama Terimi', 'Aratma Sayısı']
                fig_bar = px.bar(top_searches, x='Aratma Sayısı', y='Arama Terimi', orientation='h',
                                 color='Aratma Sayısı', color_continuous_scale='Teal')
                fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
                
            st.write("---")
            
            # --- KELİME ANALİZİ SEKANSI (TREEMAP) ---
            st.subheader("📊 En Sık Aratılan Kelimelerin Haritası (Treemap)")
            st.markdown("Aramalarınızda en çok geçen kelimelerin hacimsel dağılımı.")
            
            tum_kelimeler = " ".join(arama_df['Arama Terimi'].astype(str)).lower().split()
            cop_kelimeler = ['nedir', 'nasıl', 've', 'bir', 'bu', 'ne', 'için', 'ile', 'mı', 'mu', 'en', 'göre', 
                             'adlı', 'izlediniz', 'ettiniz', 'sayfasını', 'the', 'ben', 'olur', 'watch', 'olan', 'sonra', 'yaptınız']
            temiz_kelimeler = [w for w in tum_kelimeler if w not in cop_kelimeler and len(w) > 2]
            
            if temiz_kelimeler:
                kelime_serisi = pd.Series(temiz_kelimeler).value_counts().head(30).reset_index()
                kelime_serisi.columns = ['Kelime', 'Sıklık']
                
                fig_treemap = px.treemap(kelime_serisi, path=['Kelime'], values='Sıklık', color='Sıklık', color_continuous_scale='Teal')
                fig_treemap.update_layout(margin=dict(t=10, l=10, r=10, b=10), height=450)
                st.plotly_chart(fig_treemap, use_container_width=True)
            else:
                st.info("Analiz edecek kadar kelime bulunamadı.")
        else:
            st.info("Gösterilecek arama geçmişi verisi bulunmuyor.")

        st.write("---")
        
        # --- TABLO ---
        st.subheader("📋 Filtrelenmiş Kategori Tablosu")
        mevcut_sutunlar = [c for c in ['Arama Terimi', 'Kategori', 'Yıl', 'Ay', 'Gün'] if c in arama_df.columns]
        tablo_df = arama_df[mevcut_sutunlar].copy()
        st.dataframe(tablo_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Arama dosyası işlenirken bir hata oluştu: {e}")
else:
    st.warning("⚠️ Arama geçmişi verisi bulunamadı! Lütfen ana sayfaya gidip 'Arama Geçmişi' dosyasını yükleyin.")