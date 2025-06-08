# 📋 **Q01 GÖREV DETAYLARI**

## 🎯 **GÖREV: Q01.1.1 - Ekran Görüntüsü Yakalama API Entegrasyonu**

### **📝 GÖREV TANIMI**
ALT_LAS'ın ekranı "görebilmesi" için temel ekran görüntüsü yakalama API'sini entegre etmek ve optimize etmek.

### **🎯 GÖREV AMACI**
Sistem, mevcut ekran içeriğini yakalayabilecek ve bu veriyi işleyebilecek hale gelecek. Bu, tüm görsel algı sisteminin temelidir.

### **📊 ATLAS PROMPT**
**Atlas Prompt ID**: Q01.1.1.1

```
ALT_LAS, ekranı gör ve analiz et:
1. Mevcut ekran görüntüsünü yakala
2. Görüntü kalitesini değerlendir
3. İşlenebilir format'a dönüştür
4. Temel görsel elementleri tespit et
```

### **✅ ÖN KOŞULLAR**
- [ ] Python PIL/Pillow kütüphanesi kurulu
- [ ] OpenCV kütüphanesi kurulu
- [ ] Mevcut Vision Module temel fonksiyonları çalışıyor
- [ ] Test ortamı hazır
- [ ] Geliştirme izinleri mevcut

### **🎯 KABUL KRİTERLERİ**
- [ ] Ekran görüntüsü başarıyla yakalanabiliyor
- [ ] Farklı çözünürlüklerde çalışıyor (1920x1080, 1366x768, 2560x1440)
- [ ] Yakalama süresi <500ms
- [ ] Görüntü kalitesi korunuyor
- [ ] Memory usage <50MB per capture
- [ ] Error handling implementasyonu
- [ ] Unit testler %100 geçiyor

### **🧪 TEST ADIMLARI**

#### **1. Unit Test**
```bash
cd src/jobone/vision_core/computer_access/vision/
python3 -m pytest test_screen_capture.py -v
```

#### **2. Integration Test**
```bash
python3 test_screen_capture_integration.py
```

#### **3. Manual Test**
1. Ekran görüntüsü yakalama fonksiyonunu çağır
2. Dönen görüntüyü kontrol et
3. Farklı çözünürlüklerde test et
4. Performance metriklerini ölç

### **🔧 İMPLEMENTASYON DETAYLARI**

#### **Dosya Lokasyonu**
```
src/jobone/vision_core/computer_access/vision/screen_capture.py
```

#### **Ana Fonksiyonlar**
- `capture_screen()`: Tam ekran yakalama
- `capture_region(x, y, width, height)`: Bölgesel yakalama
- `optimize_image(image)`: Görüntü optimizasyonu
- `validate_capture(image)`: Yakalama doğrulama

---

## 🎯 **GÖREV: Q01.1.2 - Temel OCR Entegrasyonu**

### **📝 GÖREV TANIMI**
Yakalanan ekran görüntülerinden metin çıkarma yeteneği kazandırmak için OCR sistemini entegre etmek.

### **🎯 GÖREV AMACI**
Sistem, görsel içerikteki metinleri okuyabilecek ve bu bilgiyi işleyebilecek hale gelecek.

### **📊 ATLAS PROMPT**
**Atlas Prompt ID**: Q01.1.2.1

```
ALT_LAS, görüntüdeki metni oku ve anla:
1. Ekran görüntüsündeki metinleri tespit et
2. OCR ile metinleri çıkar
3. Metin kalitesini değerlendir
4. Yapılandırılmış veri olarak sun
```

### **✅ ÖN KOŞULLAR**
- [ ] Q01.1.1 tamamlanmış
- [ ] Tesseract OCR kurulu
- [ ] pytesseract kütüphanesi kurulu
- [ ] Ekran yakalama sistemi çalışıyor

### **🎯 KABUL KRİTERLERİ**
- [ ] Temel metin tanıma %80+ doğruluk
- [ ] Türkçe karakter desteği
- [ ] Farklı font boyutlarında çalışıyor
- [ ] OCR işlemi <2 saniye
- [ ] Confidence score hesaplaması
- [ ] Error handling ve fallback

---

## 🎯 **GÖREV: Q01.1.3 - UI Element Tespiti**

### **📝 GÖREV TANIMI**
Ekran görüntüsündeki UI elementlerini (buton, textbox, menu vb.) tespit etme yeteneği geliştirmek.

### **🎯 GÖREV AMACI**
Sistem, görsel arayüz elementlerini tanıyabilecek ve bunlarla etkileşim kurabilecek.

### **📊 ATLAS PROMPT**
**Atlas Prompt ID**: Q01.1.3.1

```
ALT_LAS, UI elementlerini tanı ve kategorize et:
1. Butonları tespit et
2. Metin kutularını bul
3. Menüleri ve linkleri tanı
4. Etkileşim alanlarını belirle
```

### **✅ ÖN KOŞULLAR**
- [ ] Q01.1.1 ve Q01.1.2 tamamlanmış
- [ ] OpenCV kurulu
- [ ] Template matching algoritmaları hazır

### **🎯 KABUL KRİTERLERİ**
- [ ] Temel UI elementleri %75+ doğrulukla tespit ediliyor
- [ ] Bounding box koordinatları doğru
- [ ] Element türü sınıflandırması
- [ ] Confidence scoring sistemi

---

## 🎯 **GÖREV: Q01.1.4 - Görsel Veri İşleme Pipeline**

### **📝 GÖREV TANIMI**
Yakalanan görsel veriyi işlemek ve analiz etmek için pipeline sistemi oluşturmak.

### **🎯 GÖREV AMACI**
Ham görsel veriyi yapılandırılmış, işlenebilir bilgiye dönüştürmek.

### **📊 ATLAS PROMPT**
**Atlas Prompt ID**: Q01.1.4.1

```
ALT_LAS, görsel veriyi işle ve yapılandır:
1. Ham görüntüyü al
2. Ön işleme uygula
3. Analiz et ve kategorize et
4. Yapılandırılmış çıktı üret
```

---

## 🎯 **GÖREV: Q01.2.1 - Gelişmiş Klavye Kontrolü Entegrasyonu**

### **📝 GÖREV TANIMI**
Mevcut Enhanced Keyboard Controller'ı Q01 sistemine entegre etmek.

### **🎯 GÖREV AMACI**
Görsel algı ile klavye kontrolünü birleştirerek otonom etkileşim sağlamak.

### **📊 ATLAS PROMPT**
**Atlas Prompt ID**: Q01.2.1.1

```
ALT_LAS, klavye ile etkileşim kur:
1. Hedef alanı görsel olarak tespit et
2. Uygun klavye komutunu seç
3. Komutu güvenli şekilde yürüt
4. Sonucu doğrula
```

### **✅ ÖN KOŞULLAR**
- [ ] Enhanced Keyboard Controller %100 çalışıyor
- [ ] Q01.1.x görevleri tamamlanmış
- [ ] Integration test ortamı hazır

### **🎯 KABUL KRİTERLERİ**
- [ ] Keyboard controller entegre edildi
- [ ] Görsel hedefleme çalışıyor
- [ ] Güvenli komut yürütme
- [ ] Error recovery mekanizması

---

## 🎯 **GÖREV: Q01.2.2 - Mouse Kontrolü Entegrasyonu**

### **📝 GÖREV TANIMI**
Mevcut Mouse Controller'ı görsel algı sistemiyle entegre etmek.

### **🎯 GÖREV AMACI**
Görsel hedefleme ile mouse kontrolünü birleştirmek.

---

## 🎯 **GÖREV: Q01.2.3 - Temel Otonom Eylem Sistemi**

### **📝 GÖREV TANIMI**
Basit otonom eylemleri planlama ve yürütme sistemi oluşturmak.

### **🎯 GÖREV AMACI**
Sistem, basit görevleri otomatik olarak planlayıp yürütebilecek.

---

## 🎯 **GÖREV: Q01.2.4 - Basit Görev Yürütme Motoru**

### **📝 GÖREV TANIMI**
Görevleri sıralı olarak yürüten temel motor sistemi geliştirmek.

### **🎯 GÖREV AMACI**
Karmaşık görevleri basit adımlara bölerek yürütmek.

---

**Son Güncelleme**: {TARIH}  
**Sorumlu**: Development Team  
**Onay**: Sprint Master
