import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Zaman Yolculuğu", page_icon="⏳", layout="wide")

# Eğer ana sayfada dosya SILINDIYYSE, zaman makinesinin seçtiği yılı da hafızadan kökten kazıyalım
if 'arama_df' not in st.session_state or st.session_state['arama_df'] is None:
    if 'hedef_yil' in st.session_state:
        del st.session_state['hedef_yil']
    
    st.warning("⚠️ Arama geçmişi verisi bulunamadı! Lütfen ana sayfaya gidip 'Arama Geçmişi' dosyasını yükleyin.")
    st.info("💡 Dosya yüklendiğinde Zaman Makinesi odası otomatik olarak kullanıma açılacaktır.")

else:
    # --- EĞER DOSYA VARSA KUSURSUZCA ÇALIŞACAK ALAN ---
    try:
        raw_df = st.session_state['arama_df'].copy()
        
        # Reklam ve izleme filtreleme duvarı
        video_ve_reklam_ekleri = ['videoyu izlediniz', 'izlenen video', 'reklam', 'indirim', 'sepetine göre', 'kampanya']
        raw_df['title_clean'] = raw_df['title'].astype(str)
        izleme_mi = raw_df['title_clean'].str.contains('|'.join(video_ve_reklam_ekleri), case=False, na=False)
        arama_df = raw_df[~izleme_mi].copy()
        
        arama_df['Arama Terimi'] = arama_df['title_clean'].str.replace('Şunu aradınız: ', '', case=False, regex=False)
        arama_df['Arama Terimi'] = arama_df['Arama Terimi'].str.replace(' araması yaptınız', '', case=False, regex=False).str.strip()
        
        # Zaman dönüşümleri
        if 'tarih_saat' not in arama_df.columns and 'time' in arama_df.columns:
            arama_df['tarih_saat'] = pd.to_datetime(arama_df['time'], format='ISO8601', errors='coerce')
            arama_df['Yıl'] = arama_df['tarih_saat'].dt.year
            arama_df['Ay_No'] = arama_df['tarih_saat'].dt.month
            arama_df['Gun_No'] = arama_df['tarih_saat'].dt.day
            arama_df['Saat'] = arama_df['tarih_saat'].dt.hour

        st.title("⏳ YouTube Arama Geçmişi: Zaman Yolculuğu")
        st.write("---")
        
        bugun = datetime.date.today()
        aylar_tr = {1:'Ocak', 2:'Şubat', 3:'Mart', 4:'Nisan', 5:'Mayıs', 6:'Haziran', 7:'Temmuz', 8:'Ağustos', 9:'Eylül', 10:'Ekim', 11:'Kasım', 12:'Aralık'}
        
        st.subheader(f"📅 Bugün: {bugun.day} {aylar_tr[bugun.month]} {bugun.year}")
        
        # Sütun butonları
        c1, c2, c3, c4 = st.columns(4)
        if 'hedef_yil' not in st.session_state: 
            st.session_state['hedef_yil'] = None
            
        with c1:
            if st.button("🚀 1 Sene Önceye Git"): st.session_state['hedef_yil'] = bugun.year - 1
        with c2:
            if st.button("🚀 2 Sene Önceye Git"): st.session_state['hedef_yil'] = bugun.year - 2
        with c3:
            if st.button("🚀 3 Sene Önceye Git"): st.session_state['hedef_yil'] = bugun.year - 3
        with c4:
            if st.button("🌌 Zaman Kapsülünden Çık"): st.session_state['hedef_yil'] = None
            
        st.write("---")
        
        # Seçilen yıla göre filtreleme yap
        if st.session_state['hedef_yil'] is not None:
            h_yil = st.session_state['hedef_yil']
            nostalji_df = arama_df[(arama_df['Yıl'] == h_yil) & (arama_df['Ay_No'] == bugun.month) & (arama_df['Gun_No'] == bugun.day)]
            
            st.subheader(f"🌌 {bugun.day} {aylar_tr[bugun.month]} {h_yil} Tarihindeki Aramaların")
            
            if not nostalji_df.empty:
                st.dataframe(nostalji_df[['Arama Terimi', 'Saat']], use_container_width=True)
            else:
                st.warning(f"O tarihte ({bugun.day} {aylar_tr[bugun.month]} {h_yil}) hiçbir arama kaydı bulunamadı kral.")
        else:
            st.info("💡 Geçmişe ışınlanmak için yukarıdaki butonlardan birine tıkla. O yılın bugünündeki aramaların buraya listelenecek.")
            
    except Exception as e:
        st.error(f"Zaman yolculuğu odasında bir hata oluştu: {e}")