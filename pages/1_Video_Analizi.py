import streamlit as st
import plotly.express as px
import pandas as pd

st.set_page_config(page_title="Gelişmiş Video Analizi", page_icon="🎬", layout="wide")

# Mor/Platin Tema CSS Dokunuşu
st.markdown("""
    <style>
    .main { background-color: #f5f3f7; }
    .stMetric { 
        background-color: #4a2868 !important; 
        padding: 15px; 
        border-radius: 12px; 
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1); 
    }
    .stMetric label { color: #f3e8ff !important; font-weight: bold !important; }
    .stMetric div[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 24px !important; }
    h1 { color: #4a2868; font-family: 'Helvetica Neue', sans-serif; }
    h3 { color: #6b21a8; }
    </style>
    """, unsafe_allow_html=True)

# GÜVENLİK VE HAFIZA DUVARI: Sadece kendine ait video hafızası varsa çalışır
if 'video_df' in st.session_state and st.session_state['video_df'] is not None:
    df = st.session_state['video_df'].copy()
    
    # REKLAM VE ÇÖP VİDEOLARI AYIKLAMA SÜZGECİ
    reklam_kelimeler = ['indirim', 'sepetine göre', 'fırsat', 'kampanya', 'satın al', 'tıkla', 'abone olun', 'reklamı']
    df['title_str'] = df['title'].astype(str)
    is_reklam = df['title_str'].str.contains('|'.join(reklam_kelimeler), case=False, na=False)
    video_df = df[~is_reklam].copy()
    
    # SAF VİDEO BAŞLIĞI TEMİZLİĞİ
    video_df['Video Başlığı'] = video_df['title_str'].str.replace('İzlenen video: ', '', case=False, regex=False)
    video_df['Video Başlığı'] = video_df['Video Başlığı'].str.replace('Yeniden izlenen video: ', '', case=False, regex=False)
    video_df['Video Başlığı'] = video_df['Video Başlığı'].str.replace(' adlı videoyu izlediniz', '', case=False, regex=False)
    video_df['Video Başlığı'] = video_df['Video Başlığı'].str.replace(' videosunu izlediniz', '', case=False, regex=False)
    video_df['Video Başlığı'] = video_df['Video Başlığı'].str.strip()
    
    st.title("🎬 Gelişmiş Video İzleme Odası")
    st.markdown("YouTube video izleme alışkanlıklarının en ince detaylarına kadar inelim.")
    st.write("---")
    
    # --- YAN MENÜ FİLTRELERİ ---
    st.sidebar.header("⚙️ Gelişmiş Filtreler")
    
    # Yıl Filtresi
    yillar = sorted(video_df['Yıl'].unique().tolist(), reverse=True)
    secilen_yil = st.sidebar.selectbox("Yıl Seçin", ["Tüm Zamanlar"] + yillar)
    if secilen_yil != "Tüm Zamanlar":
        video_df = video_df[video_df['Yıl'] == secilen_yil]
        
    # Saat Aralığı Filtresi (Slider)
    saat_araligi = st.sidebar.slider("Saat Aralığı Seçin (0-23)", 0, 23, (0, 23))
    video_df = video_df[(video_df['Saat'] >= saat_araligi[0]) & (video_df['Saat'] <= saat_araligi[1])]

    # --- METRİKLER (KPIs) ---
    toplam_video = len(video_df)
    tahmini_dakika = toplam_video * 12  # Ortalama video süresini 12 dk kabul ettik
    tahmini_saat = tahmini_dakika // 60
    en_populer_kanal = video_df['Kanal'].mode()[0] if not video_df['Kanal'].empty else "Bilinmiyor"
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📹 Filtrelenmiş Video Sayısı", f"{toplam_video:,} kez")
    with c2: st.metric("⏳ Harcanan Tahmini Süre", f"{tahmini_saat:,} Saat")
    with c3: st.metric("👑 Dönemin En Çok İzlenen Kanalı", en_populer_kanal)
    
    st.write("---")
    
    # --- GRAFİKLER: 1. SATIR ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 En Çok İzlenen İlk 10 YouTube Kanalı")
        top_v = video_df['Kanal'].value_counts().head(10).reset_index()
        top_v.columns = ['Kanal', 'İzlenme Sayısı']
        fig_bar = px.bar(top_v, x='İzlenme Sayısı', y='Kanal', orientation='h', 
                         color='İzlenme Sayısı', color_continuous_scale='Purples')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col2:
        st.subheader("🦉 İzleyici Tipi Dağılımı")
        profil_veri = video_df['Zaman Dilimi'].value_counts().reset_index()
        profil_veri.columns = ['Zaman Dilimi', 'Video Sayısı']
        fig_pie = px.pie(profil_veri, values='Video Sayısı', names='Zaman Dilimi', 
                         color_discrete_sequence=px.colors.sequential.Purples_r, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    st.write("---")
    
    # --- GRAFİKLER: 2. SATIR (GELİŞMİŞ HEATMAP VE TREND) ---
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🔥 Haftalık Yoğunluk Haritası (Gün & Saat)")
        heatmap_data = video_df.groupby(['Gün', 'Saat']).size().reset_index(name='İzlenme')
        gun_sirasi = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        heatmap_pivot = heatmap_data.pivot(index='Gün', columns='Saat', values='İzlenme').reindex(gun_sirasi).fillna(0)
        
        fig_heatmap = px.imshow(heatmap_pivot, 
                                labels=dict(x="Günün Saati", y="Haftanın Günü", color="İzlenme"),
                                x=heatmap_pivot.columns,
                                y=heatmap_pivot.index,
                                color_continuous_scale='Purples')
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
    with col4:
        st.subheader("📅 Aylık İzlenme Değişim Grafiği")
        ay_sirasi = ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık']
        ay_v = video_df['Ay'].value_counts().reindex(ay_sirasi).fillna(0).reset_index()
        ay_v.columns = ['Ay', 'İzlenme']
        fig_line = px.line(ay_v, x='Ay', y='İzlenme', markers=True, color_discrete_sequence=['#6b21a8'])
        st.plotly_chart(fig_line, use_container_width=True)

    st.write("---")

    # --- GELİŞMİŞ DETAYLI ARAMA MOTORU ---
    st.subheader("🔍 Akıllı Geçmiş Arama Motoru")
    st.markdown("Geçmişinde merak ettiğin bir kelimeyi arat, röntgenini çıkaralım.")
    
    arama_kelimesi = st.text_input("Arama çubuğu:", placeholder="Aratmak istediğiniz kanal veya video kelimesini yazıp Enter'a basın...")
    
    tablo_df = video_df[['Video Başlığı', 'Kanal', 'Gün', 'Saat', 'Yıl', 'Ay']].copy()
    
    if arama_kelimesi:
        filtreli_df = tablo_df[tablo_df['Video Başlığı'].str.contains(arama_kelimesi, case=False, na=False) | 
                                tablo_df['Kanal'].str.contains(arama_kelimesi, case=False, na=False)]
        
        arama_skor = len(filtreli_df)
        
        if arama_skor > 0:
            st.success(f"🔍 **'{arama_kelimesi}'** kelimesi geçmişinizde tam **{arama_skor:,} kez** bulundu!")
            
            arama_saat = filtreli_df['Saat'].value_counts().sort_index().reset_index()
            arama_saat.columns = ['Saat', 'İzlenme']
            fig_arama_saat = px.bar(arama_saat, x='Saat', y='İzlenme', color_discrete_sequence=['#9333ea'])
            fig_arama_saat.update_layout(height=250)
            st.plotly_chart(fig_arama_saat, use_container_width=True)
            
            st.dataframe(filtreli_df, use_container_width=True)
        else:
            st.error(f"Geçmişinizde '{arama_kelimesi}' ile eşleşen bir video veya kanal bulunamadı.")
    else:
        st.info("Son izlediğiniz 100 video aşağıda listelenmiştir. Detaylı analiz için yukarıdaki çubuğa kelime yazabilirsiniz.")
        st.dataframe(tablo_df.head(100), use_container_width=True)

else:
    st.warning("⚠️ İzleme geçmişi verisi bulunamadı! Lütfen ana sayfaya gidip 'İzleme Geçmişi' dosyasını yükleyin.")