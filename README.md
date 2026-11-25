# BEDAŞ Kesinti — Home Assistant

İstanbul Avrupa yakasında **BEDAŞ planlı elektrik kesintilerini** Home Assistant'a getirir. Yalnızca **senin mahalleni ve sokağını** etkileyen kesintileri gösterir. Ek eklenti ya da entegrasyon kurman gerekmez. Bir Python betiği ve bir paket dosyasından ibarettir.

## Kurulum (önerilen: Marketplace)
1. **Ayarlar → Marketplace → ⋮ → Bağlantıdan ekle** (Custom repository): `https://github.com/amucahidb/bedas-kesinti`, tür: **Integration**
2. **BEDAŞ Kesinti**'yi indir, Home Assistant'ı yeniden başlat.
3. **Ayarlar → Cihazlar ve hizmetler → Entegrasyon ekle → BEDAŞ Kesinti**: ilçe, mahalle, sokak(lar)ı yaz. Sonradan **Yapılandır** ile değiştirebilirsin; birden çok adres için tekrar ekle.

Oluşan varlıklar (cihaz: *BEDAŞ Kesinti – Mahalle*): **Sıradaki kesinti** (zaman; `ozet`, `bitis`, `seviye`, `neden` öznitelikleri), **Kesinti sayısı**, **Şu an kesinti**, **Kesinti takvimi** (HA takviminde görünür).

**Bildirim:** `blueprints/automation/bedas_kesinti/bildirim.yaml` blueprint'ini içe aktar (Ayarlar → Otomasyonlar → Blueprint'ler → İçe aktar, dosyanın GitHub adresini yapıştır), telefonunu ve “ne kadar önce”yi seç. Farklı süreler için (ör. 12 saat ve 1 saat) iki otomasyon oluştur.

> Entegrasyon kurmadan, dosya kopyalayarak kurmak istersen aşağıdaki **paket yöntemi** de çalışır.

## Ne yapar?
- 3 saatte bir BEDAŞ'a sadece **senin ilçeni** sorar ve gelen listeden yalnızca senin mahalle ve sokağını içeren kesintileri ayırır.
- Her kesintiye bir **seviye** verir:
  - **kesin:** Duyuruda sokak listesi var ve senin sokağın listede.
  - **olası:** Duyuruda sokak verilmemiş, yalnızca mahalle adı geçiyor. Bunun bildirimini bir anahtarla açıp kapatabilirsin.
- Yazım farklarını tanır: "Cd." = "Cad." = "Caddesi", "Sk." = "Sokak", "Mah.", İ/ı, büyük-küçük harf.
- iPhone ya da Android telefonuna bildirim gönderir:
  - Kesintiden önceki akşam saat 20:00'de,
  - Kesintiye 1 saat kala,
  - BEDAŞ sorgusu 1 gündür çalışmıyorsa.

## Oluşan varlıklar (paket yöntemi)
| Varlık | Açıklama |
|---|---|
| `sensor.kesinti_bedas` | Eşleşen kesinti sayısı. Ayrıntıları özniteliklerde: `kesintiler`, `guncelleme`, `hata` |
| `sensor.kesinti_siradaki_elektrik` | Sıradaki kesintinin başlangıcı. Öznitelikler: `bitis`, `seviye`, `neden`, `ozet` |
| `binary_sensor.kesinti_elektrik_su_an` | Şu an kesinti varsa açık olur |
| `input_boolean.kesinti_olasi_bildirim` | Mahalle düzeyindeki (olası) kesintiler için bildirim açık mı |

## Paket yöntemi (entegrasyonsuz)
1. `configuration.yaml` dosyasında paketler açık değilse ekle:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
2. `bedas_kesinti.py` dosyasını `/config/bedas_kesinti/` klasörüne kopyala.
3. `packages/bedas_kesinti.yaml` dosyasını `/config/packages/` klasörüne kopyala. Dosyada iki şeyi değiştir:
   - `command:` satırında ilçe, mahalle ve sokak adını. Örnek: `... BEYLİKDÜZÜ Yakuplu Birlik`. Çok kelimeli adları tırnak içine al, örneğin `"Adnan Kahveci"`. Birden fazla sokak için sonuna boşlukla ekle.
   - `notify.mobile_app_TELEFONUN` yazan yerleri kendi telefonunun bildirim servisiyle değiştir. Servisin adını Geliştirici Araçları → Eylemler'de "notify" diye arayarak bulabilirsin.
4. Home Assistant'ı **yeniden başlat**. `command_line` yeni bir entegrasyon olduğu için yeniden yükleme yetmez.

İlk sorgu yeniden başlatmadan hemen sonra yapılır. Sonucu `sensor.kesinti_bedas` varlığının özniteliklerinde görebilirsin.

### Panel kartı (isteğe bağlı, Mushroom ile)
```yaml
type: custom:mushroom-template-card
primary: Elektrik kesintisi
secondary: "{{ state_attr('sensor.kesinti_siradaki_elektrik', 'ozet') or 'Bilgi yok' }}"
icon: mdi:transmission-tower-off
icon_color: >
  {{ 'red' if is_state('binary_sensor.kesinti_elektrik_su_an', 'on')
     else ('orange' if states('sensor.kesinti_siradaki_elektrik') not in ['unknown', 'unavailable'] else 'green') }}
tap_action:
  action: more-info
  entity: sensor.kesinti_bedas
```

## Elle deneme
```bash
python3 bedas_kesinti.py BEYLİKDÜZÜ Yakuplu Birlik
```
Çıktı JSON biçimindedir: `adet`, `ilce_kayit` (ilçedeki toplam kayıt), `kesintiler`.

## Sınırlar
- Yalnızca **BEDAŞ**'ın, yani Avrupa yakasının **planlı** kesintilerini kapsar. Anlık arızalar dahil değil.
- BEDAŞ duyuruları en fazla sokak düzeyinde. Bina ya da kapı numarası bilgisi yok.
- Veri BEDAŞ sitesinin kendi sorgu sayfasının kullandığı adresten gelir. Resmi, belgelenmiş bir API değil. BEDAŞ siteyi değiştirirse betik bozulabilir. Böyle bir durumda hata bildirimi seni uyarır.
- Su kesintileri (İSKİ) için herkese açık, düzenli bir veri kaynağı bulunamadı. Bunun için İSKİ'nin SMS bilgilendirme servisi öneriliyor.

## Geliştirme
Katkılar açık: AYEDAŞ (Anadolu yakası), anlık arızalar, diğer illerin dağıtım şirketleri…
Entegrasyon kodu `custom_components/bedas_kesinti/`; ayrıştırma `parser.py` (HA'dan bağımsız, testli).
```bash
pip install pytest pyyaml
pytest -q
```
`tests/ornek_beylikduzu.json` gerçek bir BEDAŞ yanıtından alınmış örnektir; testlerde tarihleri 2099'a kaydırılmıştır.

## Lisans
MIT
