"""BEDAŞ yanıtını ayrıştırır ve adrese göre süzer. Home Assistant'a bağımlı değildir (testlerde doğrudan kullanılır)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Europe/Istanbul")
_TR = str.maketrans("İIıŞşĞğÜüÖöÇç", "IIISSGGUUOOCC")
_EKLER = r"\b(MAHALLESI|MAH|CADDESI|CAD|CD|SOKAGI|SOKAK|SOK|SK|BULVARI|BLV|BUL)\b\.?"


def norm(metin: str) -> list[str]:
    """Türkçe harf, büyük/küçük harf ve Cd./Sk./Mah. farklarını yok sayan karşılaştırma anahtarı."""
    s = metin.upper().translate(_TR).upper()
    s = re.sub(_EKLER, " ", s)
    return re.sub(r"[^A-Z0-9 ]", " ", s).split()


def ilce_sorgu(ilce: str) -> str:
    """BEDAŞ'ın beklediği büyük harfli Türkçe ilçe adı (i -> İ)."""
    return ilce.strip().replace("i", "İ").replace("ı", "I").upper()


def ayristir(mesaj: str) -> list[tuple[str, list[str]]]:
    """'... ilce MERKEZ-YAKUPLU mah BİRLİK, DEREBOYU sk  bölgelerinde' -> [('YAKUPLU', ['BİRLİK', 'DEREBOYU'])]"""
    m = re.search(r"\bilce\b(.*?)\bbölgelerinde\b", mesaj, re.S)
    govde = m.group(1) if m else mesaj
    sonuc = []
    for p in re.finditer(r"(.*?)\bmah\b(.*?)\bsk\b", govde, re.S):
        mah = p.group(1).strip(" ,").split("-")[-1].strip()
        soks = [x.strip() for x in p.group(2).split(",") if x.strip()]
        sonuc.append((mah, soks))
    return sonuc


def esles(mah: str, soks: list[str], hedef_mah: str, hedef_soklar: list[str]) -> str | None:
    if norm(mah) != norm(hedef_mah):
        return None
    if not soks:
        return "olasi"
    hedef = [norm(h) for h in hedef_soklar if h.strip()]
    if any(norm(s) in hedef for s in soks):
        return "kesin"
    return None


@dataclass(frozen=True)
class Kesinti:
    baslangic: datetime
    bitis: datetime
    seviye: str
    neden: str
    mahalle: str
    sokaklar: str

    def as_dict(self) -> dict:
        return {"baslangic": self.baslangic.isoformat(), "bitis": self.bitis.isoformat(), "seviye": self.seviye,
                "neden": self.neden, "mahalle": self.mahalle, "sokaklar": self.sokaklar}


def suz(veri: list, mahalle: str, sokaklar: list[str], simdi: datetime | None = None) -> list[Kesinti]:
    """Ham BEDAŞ listesinden, bitmemiş ve adrese uyan kesintiler (başlangıca göre sıralı)."""
    simdi = simdi or datetime.now(IST)
    liste: list[Kesinti] = []
    for kayit in veri or []:
        po = (kayit or {}).get("plannedOutage") or {}
        try:
            bas = datetime.strptime(po["startDateTime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
            bit = datetime.strptime(po["endDateTime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=IST)
        except (KeyError, TypeError, ValueError):
            continue
        if bit <= simdi:
            continue
        for mah, soks in ayristir(po.get("message") or ""):
            seviye = esles(mah, soks, mahalle, sokaklar)
            if seviye:
                liste.append(Kesinti(bas, bit, seviye, po.get("reason") or "", mah, ", ".join(soks)[:300]))
                break
    return sorted(set(liste), key=lambda k: (k.baslangic, k.bitis))


def duyurudaki_mahalleler(veri: list) -> list[str]:
    """Ham BEDAŞ listesinde geçen mahalle adları (kurulumda yazım kontrolü için)."""
    adlar = {}
    for kayit in veri or []:
        po = (kayit or {}).get("plannedOutage") or {}
        for mah, _ in ayristir(po.get("message") or ""):
            if mah:
                adlar.setdefault(" ".join(norm(mah)), mah)
    return sorted(adlar.values())


def mahalle_kontrol(veri: list, mahalle: str) -> tuple[bool, list[str]]:
    """(duyurularda geçiyor mu, benzer ad önerileri)."""
    import difflib
    adlar = duyurudaki_mahalleler(veri)
    anahtar = " ".join(norm(mahalle))
    if any(" ".join(norm(a)) == anahtar for a in adlar):
        return True, []
    yakin = difflib.get_close_matches(anahtar, [" ".join(norm(a)) for a in adlar], n=3, cutoff=0.6)
    harita = {" ".join(norm(a)): a for a in adlar}
    return False, [harita[y] for y in yakin] or adlar[:8]
