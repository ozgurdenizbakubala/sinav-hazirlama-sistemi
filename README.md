# sinav-hazirlama-sistemi
Öğretmenler için soru bankası ve PDF sınav hazırlama uygulaması. Python + Tkinter. Windows &amp; Linux. Claude Opus 4.6 ile geliştirilmiştir.
# 📚 Sınav Hazırlama Sistemi

Öğretmenler için geliştirilmiş, soru bankası oluşturma ve PDF sınav hazırlama masaüstü uygulaması.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-orange)
![AI](https://img.shields.io/badge/Claude-Opus%204.6-purple)

---

## Özellikler

- 📷 Ekran görüntüsü veya dosyadan soru ekleme (pano desteği dahil)
- 🗂️ Sınıf ve konu bazlı soru bankası yönetimi
- 📝 Sürükle-bırak PDF sınav düzenleyici
- 📐 Her soru için özelleştirilebilir çözüm alanı ve noktalı satırlar
- 📋 Otomatik cevap anahtarı ve çözüm PDF'i
- 🌙 Koyu / Açık tema (tercih kaydedilir)
- 🔐 Şifreli giriş sistemi + 32 adet kurtarma kodu
- 🔡 Türkçe karakter destekli PDF çıktısı (DejaVu font)
- 🎲 Sınıf ve konu bazlı rastgele soru seçimi

---

## Kullanılan Teknolojiler

| Teknoloji | Amaç |
|-----------|------|
| **Python 3.10+** | Ana programlama dili |
| **Tkinter** | Masaüstü arayüzü |
| **SQLite3** | Yerel veritabanı (soru ve ayar saklama) |
| **Pillow (PIL)** | Görsel işleme ve önizleme |
| **ReportLab** | PDF oluşturma |
| **OpenCV (cv2)** | Görsel bölge tespiti |
| **NumPy** | Görsel işleme yardımcısı |
| **DejaVu Sans** | Türkçe karakter destekli font |

---

## Yapay Zeka Desteği

Bu proje **Claude Opus 4.6** (Anthropic) yapay zeka modeli yardımıyla geliştirilmiştir.

---

## Kurulum

### Yöntem 1 — Hazır Installer (Önerilen)

1. [Releases](../../releases) sayfasından `SinavHazirlamaSistemi_Kurulum.exe` dosyasını indirin
2. Çift tıklayın, kurulum sihirbazını takip edin
3. Masaüstündeki ikona çift tıklayarak açın

> Python veya başka bir şey kurmanız **gerekmez** — her şey pakette.

### Yöntem 2 — Kaynak Koddan Çalıştırma

**Gereksinimler:** Python 3.10+

```bash
git clone https://github.com/ozgurdenizbakubala/sinav-hazirlama-sistemi.git
cd sinav-hazirlama-sistemi
pip install -r requirements.txt
python main.py
```

---

## PC Değişince Ne Olur?

### Installer (.exe) kullandıysanız:
- Yeni PC'ye `SinavHazirlamaSistemi_Kurulum.exe` dosyasını atın ve kurun
- Eski PC'deki `sinav.db` dosyasını yeni kurulum klasörüne kopyalayın
- Tüm sorularınız, konularınız ve ayarlarınız korunur
- Python veya kütüphane kurmanız **gerekmez**

### Kaynak koddan çalıştırıyorsanız:
- Yeni PC'ye Python kurun
- `pip install -r requirements.txt` ile kütüphaneleri kurun
- `sinav.db` dosyasını kopyalayın

> **`sinav.db` dosyası nerede?** Kurulum klasörünün içinde — varsayılan olarak `C:\Program Files\SinavHazirlamaSistemi\sinav.db`

---

## Geliştirme

Projeye katkıda bulunmak için:

1. Bu repoyu **fork** edin
2. Yeni bir branch oluşturun: `git checkout -b yeni-ozellik`
3. Değişikliklerinizi commit edin: `git commit -m "Yeni özellik: ..."`
4. Branch'i push edin: `git push origin yeni-ozellik`
5. **Pull Request** açın

---

## Lisans

Bu proje **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** lisansı altındadır.

### Bu lisans kapsamında:

✅ **İzin verilenler:**
- Özgürce kullanabilirsiniz
- Değiştirebilir ve geliştirebilirsiniz
- Paylaşabilir ve dağıtabilirsiniz
- Atıf vererek türev çalışmalar oluşturabilirsiniz

❌ **İzin verilmeyenler:**
- **Ticari amaçla kullanamazsınız**
- Satış yapamaz, ücret karşılığı dağıtamazsınız
- Ticari bir ürüne entegre edemezsiniz

Lisans detayları için: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.tr)

---

## İletişim

Hata bildirimi ve öneriler için [Issues](../../issues) sekmesini kullanabilirsiniz.

📧 **E-posta:** denizbakubala@gmail.com
