import json, os, subprocess, sys
K = os.path.dirname(__file__)
BETIK = os.path.join(K, "..", "bedas_kesinti.py")
ORNEK = os.path.join(K, "ornek_beylikduzu.json")
sys.path.insert(0, os.path.join(K, ".."))
import bedas_kesinti as b

def calistir(*a):
    return json.loads(subprocess.check_output([sys.executable, BETIK, "--dosya", ORNEK, *a]))

def test_sokak_eslesir_kesin():
    r = calistir("BEYLİKDÜZÜ", "Yakuplu", "Birlik Sk.")
    assert r["adet"] == 1 and r["kesintiler"][0]["seviye"] == "kesin"

def test_sokaksiz_duyuru_olasi():
    r = calistir("BEYLİKDÜZÜ", "Adnan Kahveci", "Herhangi Cd.")
    assert r["adet"] >= 1 and all(k["seviye"] == "olasi" for k in r["kesintiler"])

def test_baska_mahalle_gelmez():
    assert calistir("BEYLİKDÜZÜ", "Gürpınar", "Deniz Cd.")["adet"] == 0

def test_yazim_farklari():
    assert b.norm("Çınar Cad.") == b.norm("ÇINAR CD") == b.norm("cinar caddesi")
    assert b.norm("İnönü Mah.") == b.norm("INONU")

def test_mesaj_ayristirma():
    m = "İSTANBUL BEYLİKDÜZÜ ilce MERKEZ-YAKUPLU mah BİRLİK, DEREBOYU sk  bölgelerinde"
    assert b.ayristir(m) == [("YAKUPLU", ["BİRLİK", "DEREBOYU"])]
