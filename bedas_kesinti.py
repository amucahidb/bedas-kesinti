#!/usr/bin/env python3
"""BEDAŞ planlı kesintilerini sorgular, sadece verilen mahalle/sokağı ilgilendirenleri döndürür.
Kullanım: bedas_kesinti.py İLÇE MAHALLE SOKAK [SOKAK2 ...]   (çıktı: JSON, HA command_line sensörü için)
Test:     bedas_kesinti.py --dosya örnek.json İLÇE MAHALLE SOKAK"""
import json, re, sys, urllib.parse, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Europe/Istanbul")

URL = "https://www.bedas.com.tr/elektrik-getir"
TR = str.maketrans("İIıŞşĞğÜüÖöÇç", "IIISSGGUUOOCC")
EKLER = r"\b(MAHALLESI|MAH|CADDESI|CAD|CD|SOKAGI|SOKAK|SOK|SK|BULVARI|BLV|BUL)\b\.?"

def norm(s):
    s = s.upper().translate(TR).upper()
    s = re.sub(EKLER, " ", s)
    return re.sub(r"[^A-Z0-9 ]", " ", s).split()

def ayristir(mesaj):
    """'... ilce MERKEZ-YAKUPLU mah BİRLİK, DEREBOYU sk  bölgelerinde ...' -> [(mahalle, [sokaklar])]"""
    m = re.search(r"\bilce\b(.*?)\bbölgelerinde\b", mesaj, re.S)
    govde = m.group(1) if m else mesaj
    sonuc = []
    for p in re.finditer(r"(.*?)\bmah\b(.*?)\bsk\b", govde, re.S):
        mah = p.group(1).strip(" ,").split("-")[-1].strip()
        soks = [x.strip() for x in p.group(2).split(",") if x.strip()]
        sonuc.append((mah, soks))
    return sonuc

def esles(mah, soks, hedef_mah, hedef_soklar):
    if norm(mah) != norm(hedef_mah):
        return None
    if not soks:
        return "olasi"
    for s in soks:
        if any(norm(s) == norm(h) for h in hedef_soklar):
            return "kesin"
    return None

def main(a):
    veri = None
    if a and a[0] == "--dosya":
        veri = json.load(open(a[1], encoding="utf-8")); a = a[2:]
    ilce, mahalle, soklar = a[0], a[1], a[2:]
    if veri is None:
        data = urllib.parse.urlencode({"countryName": "İSTANBUL", "cityName": ilce.upper().replace("i", "İ")}).encode()
        req = urllib.request.Request(URL, data=data, headers={
            "Content-Type": "application/x-www-form-urlencoded", "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.bedas.com.tr/elektrik-kesintisi-sorgulama", "User-Agent": "Mozilla/5.0 (HomeAssistant)"})
        veri = json.load(urllib.request.urlopen(req, timeout=25))
    simdi = datetime.now(IST)
    liste = []
    for k in veri or []:
        po = k.get("plannedOutage") or {}
        try:
            bas = datetime.strptime(po["startDateTime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
            bit = datetime.strptime(po["endDateTime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
        except (KeyError, ValueError):
            continue
        if bit < simdi:
            continue
        for mah, soks in ayristir(po.get("message", "")):
            sev = esles(mah, soks, mahalle, soklar)
            if sev:
                liste.append({"baslangic": bas.isoformat(), "bitis": bit.isoformat(), "seviye": sev,
                              "neden": po.get("reason", ""), "mahalle": mah, "sokaklar": ", ".join(soks)[:300]})
                break
    liste.sort(key=lambda x: x["baslangic"])
    print(json.dumps({"adet": len(liste), "ilce_kayit": len(veri or []), "kesintiler": liste[:10],
                      "guncelleme": simdi.isoformat(timespec="seconds")}, ensure_ascii=False))

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:  # sensör bozulmasın: hata da JSON
        print(json.dumps({"adet": None, "hata": str(e)[:200], "kesintiler": []}, ensure_ascii=False))
