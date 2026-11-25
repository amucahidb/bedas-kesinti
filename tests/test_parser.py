"""Entegrasyonun ayrıştırıcısı (HA gerektirmez)."""
import importlib.util, json, os, sys
from datetime import datetime

K = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("bk_parser", os.path.join(K, "..", "custom_components", "bedas_kesinti", "parser.py"))
p = importlib.util.module_from_spec(spec); sys.modules["bk_parser"] = p; spec.loader.exec_module(p)
VERI = json.load(open(os.path.join(K, "ornek_beylikduzu.json"), encoding="utf-8"))
SIMDI = datetime(2026, 1, 1, tzinfo=p.IST)

def test_kesin():
    r = p.suz(VERI, "Yakuplu", ["Birlik Sk."], SIMDI)
    assert len(r) == 1 and r[0].seviye == "kesin" and r[0].baslangic.tzinfo is not None

def test_olasi():
    r = p.suz(VERI, "Adnan Kahveci", ["Deniz Cd."], SIMDI)
    assert r and all(k.seviye == "olasi" for k in r)

def test_baska_sokak_gelmez():
    assert p.suz(VERI, "Yakuplu", ["Başka Sk."], SIMDI) == []

def test_bitmis_gelmez():
    assert p.suz(VERI, "Yakuplu", ["Birlik"], datetime(2100, 1, 1, tzinfo=p.IST)) == []

def test_ilce_sorgu():
    assert p.ilce_sorgu("Beylikdüzü") == "BEYLİKDÜZÜ" and p.ilce_sorgu("Bakırköy") == "BAKIRKÖY"
