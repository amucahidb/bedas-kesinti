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
