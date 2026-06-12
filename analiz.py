import pandas as pd

def veriyi_isle(file):
    df = pd.read_json(file)
    
    # Zaman dönüşümleri (Hem video hem arama için ortak temel alanlar)
    if 'time' in df.columns:
        df['tarih_saat'] = pd.to_datetime(df['time'], format='ISO8601')
        df['Yıl'] = df['tarih_saat'].dt.year
        df['Ay_No'] = df['tarih_saat'].dt.month
        df['Saat'] = df['tarih_saat'].dt.hour
        
        gunler_tr = {'Monday':'Pazartesi', 'Tuesday':'Salı', 'Wednesday':'Çarşamba', 
                     'Thursday':'Perşembe', 'Friday':'Cuma', 'Saturday':'Cumartesi', 'Sunday':'Pazar'}
        df['Gün'] = df['tarih_saat'].dt.day_name().map(gunler_tr)
        
        aylar_tr = {1:'Ocak', 2:'Şubat', 3:'Mart', 4:'Nisan', 5:'Mayıs', 6:'Haziran', 
                    7:'Temmuz', 8:'Ağustos', 9:'Eylül', 10:'Ekim', 11:'Kasım', 12:'Aralık'}
        df['Ay'] = df['Ay_No'].map(aylar_tr)

    # --- SADECE VİDEO GEÇMİŞİ İÇİN ÇALIŞACAK BLOK ---
    if 'subtitles' in df.columns:
        df = df.dropna(subset=['subtitles'])
        
        def sanatciyi_bul(sub_list):
            if isinstance(sub_list, list) and len(sub_list) > 0:
                return sub_list[0].get('name')
            return None

        df['Kanal'] = df['subtitles'].apply(sanatciyi_bul)
        
        # Video başlığı temizleme
        df['Video Başlığı'] = df['title'].str.replace('İzlenen video: ', '', case=False, regex=False)
        df['Video Başlığı'] = df['Video Başlığı'].str.replace(' adlı videoyu izlediniz', '', case=False, regex=False)
        df['Video Başlığı'] = df['Video Başlığı'].str.replace('Yeniden izlenen video: ', '', case=False, regex=False)
        
        # Müzik Filtresi
        yasakli_kelimeler = ['tarif', 'yemek', 'vlog', 'bölüm', 'parodi', 'kışkırtma', 'komedi', 'şaka', 'filmi', 'dizisi']
        muzik_anahtar = ['records', 'vevo', 'netd', 'lyrics', 'şarkı', 'official audio', 'official video', 'remix', 'prod.', 'feat']
        
        is_music_header = df['header'].str.contains('YouTube Music', case=False, na=False)
        is_music_title = df['Video Başlığı'].str.contains('|'.join(muzik_anahtar), case=False, na=False)
        has_dash = df['Video Başlığı'].str.contains(' - ', regex=False, na=False)
        is_blocked = df['Video Başlığı'].str.contains('|'.join(yasakli_kelimeler), case=False, na=False) | df['Kanal'].str.contains('|'.join(yasakli_kelimeler), case=False, na=False)
        
        df['Tur'] = 'Video'
        df.loc[(is_music_header | (is_music_title & has_dash)) & (~is_blocked), 'Tur'] = 'Müzik'
        
        def sarki_sanatci_ayir(row):
            baslik = row['Video Başlığı']
            if ' - ' in baslik:
                parcalar = baslik.split(' - ', 1)
                sanatci = parcalar[0].strip()
                sarki = parcalar[1].split('(')[0].split('[')[0].strip()
                return pd.Series([sanatci, sarki])
            else:
                return pd.Series([row['Kanal'], baslik])
                
        df[['Temiz_Sanatci', 'Temiz_Sarki']] = df.apply(sarki_sanatci_ayir, axis=1)
        
    def kullanıcı_tipi(saat):
        if 0 <= saat < 5: return 'Gece Kuşu 🦉'
        elif 5 <= saat < 12: return 'Erken Kalkan 🌅'
        elif 12 <= saat < 18: return 'Gündüzcü ☀️'
        else: return 'Akşam Sefası 🌙'
        
    df['Zaman Dilimi'] = df['Saat'].apply(kullanıcı_tipi)
    return df