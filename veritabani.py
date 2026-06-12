import sqlite3
import hashlib

def veritabani_hazirla():
    # Türkçe karakter içermeyen temiz dosya adı
    conn = sqlite3.connect("kullanicilar.db")
    cursor = conn.cursor()
    # Tablo ve sütun isimleri tamamen İngilizce karakter standartlarında
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uyeler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kullanici_adi TEXT UNIQUE,
            sifre_hash TEXT
        )
    """)
    conn.commit()
    conn.close()

def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode('utf-8')).hexdigest()

def kullanici_ekle(kullanici_adi, sifre):
    try:
        conn = sqlite3.connect("kullanicilar.db")
        cursor = conn.cursor()
        sifre_sifreli = sifre_hashle(sifre)
        cursor.execute("INSERT INTO uyeler(kullanici_adi, sifre_hash) VALUES (?,?)", (kullanici_adi, sifre_sifreli))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Bu kullanıcı adı daha önce alınmışsa hata döndürür
        return False

def giris_kontrol(kullanici_adi, sifre):
    conn = sqlite3.connect("kullanicilar.db")
    cursor = conn.cursor()
    sifre_sifreli = sifre_hashle(sifre)
    cursor.execute("SELECT * FROM uyeler WHERE kullanici_adi = ? AND sifre_hash = ?", (kullanici_adi, sifre_sifreli))
    user = cursor.fetchone()
    conn.close()
    return user is not None