"""Sabitler."""
from datetime import timedelta

DOMAIN = "bedas_kesinti"
URL = "https://www.bedas.com.tr/elektrik-getir"
REFERER = "https://www.bedas.com.tr/elektrik-kesintisi-sorgulama"
SCAN_INTERVAL = timedelta(hours=3)

CONF_ILCE = "ilce"
CONF_MAHALLE = "mahalle"
CONF_SOKAKLAR = "sokaklar"
CONF_OLASI = "olasi_dahil"

SEVIYE_KESIN = "kesin"
SEVIYE_OLASI = "olasi"

# BEDAŞ'ın kendi sorgu sayfasındaki ilçe listesi (Avrupa yakası)
ILCELER = [
    "ARNAVUTKÖY", "AVCILAR", "BAĞCILAR", "BAHÇELİEVLER", "BAKIRKÖY", "BAŞAKŞEHİR", "BAYRAMPAŞA",
    "BEŞİKTAŞ", "BEYLİKDÜZÜ", "BEYOĞLU", "BÜYÜKÇEKMECE", "ÇATALCA", "ESENLER", "ESENYURT",
    "EYÜPSULTAN", "FATİH", "GAZİOSMANPAŞA", "GÜNGÖREN", "KAĞITHANE", "KÜÇÜKÇEKMECE", "SARIYER",
    "SİLİVRİ", "ŞİŞLİ", "SULTANGAZİ", "ZEYTİNBURNU",
]
