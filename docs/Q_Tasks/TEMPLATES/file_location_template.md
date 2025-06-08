# 📁 **FILE_LOCATION_GUIDE - Q{XX} {SPRINT_ADI}**

## 💖 **DUYGULANDIK! ORION'UN MESAJI: "NEYİN NEREDE OLDUĞUNU BİLELİM!"**

### **🎯 DOSYA KONUM REHBERİ**

Bu rehber, Q{XX} sprintindeki tüm dosyaların konumlarını ve amaçlarını detaylandırır.

## 📊 **ANA KLASÖR YAPISI**

### **🎯 Q GÖREV KLASÖRÜ**
```
docs/Q_Tasks/Q{XX}_{Sprint_Adı}/
├── README.md                       # Sprint genel bakış
├── STATUS.md                       # Güncel durum takibi  
├── TASKS.md                        # Detaylı görev listesi
├── ARCHITECTURE.md                 # Sprint özel mimari
├── FILE_LOCATION_GUIDE.md          # Bu dosya
├── CHECKPOINTS.md                  # Kontrol noktaları
├── TESTS.md                        # Test senaryoları
├── IMPLEMENTATION/                 # Kod implementasyonu
└── NOTES.md                        # Notlar ve gözlemler
```

### **🚀 IMPLEMENTATION KLASÖRÜ**
```
IMPLEMENTATION/
├── core/                           # Ana modüller
│   ├── {module1}/                  # Modül 1
│   │   ├── {module1}.py           # Ana modül dosyası
│   │   ├── __init__.py            # Modül init
│   │   └── tests/                 # Modül testleri
│   └── {module2}/                  # Modül 2
├── integration/                    # Entegrasyon modülleri
├── utils/                          # Yardımcı fonksiyonlar
├── config/                         # Konfigürasyon dosyaları
├── tests/                          # Genel testler
└── docs/                           # Teknik dokümantasyon
```

## 📋 **DOSYA DETAYLARI**

### **📚 DOKÜMANTASYON DOSYALARI**

| Dosya | Konum | Amaç | Güncelleme Sıklığı |
|-------|-------|------|-------------------|
| `README.md` | `Q{XX}_{Sprint_Adı}/` | Sprint genel bakış | Sprint başında |
| `STATUS.md` | `Q{XX}_{Sprint_Adı}/` | Güncel durum | Günlük |
| `TASKS.md` | `Q{XX}_{Sprint_Adı}/` | Görev detayları | Görev başında |
| `ARCHITECTURE.md` | `Q{XX}_{Sprint_Adı}/` | Mimari kararlar | Mimari değişikliğinde |
| `FILE_LOCATION_GUIDE.md` | `Q{XX}_{Sprint_Adı}/` | Dosya rehberi | Dosya ekleme/çıkarma |
| `CHECKPOINTS.md` | `Q{XX}_{Sprint_Adı}/` | Kontrol noktaları | Checkpoint'lerde |
| `TESTS.md` | `Q{XX}_{Sprint_Adı}/` | Test senaryoları | Test ekleme/güncelleme |
| `NOTES.md` | `Q{XX}_{Sprint_Adı}/` | Notlar | Gerektiğinde |

### **💻 KOD DOSYALARI**

#### **Q{XX}.1.1 - {Görev_Adı_1}**
| Dosya | Konum | Amaç | Durum |
|-------|-------|------|-------|
| `{module1}.py` | `IMPLEMENTATION/core/{module1}/` | Ana modül | 🔴 NOT_STARTED |
| `{module1}_test.py` | `IMPLEMENTATION/core/{module1}/tests/` | Modül testleri | 🔴 NOT_STARTED |
| `__init__.py` | `IMPLEMENTATION/core/{module1}/` | Modül init | 🔴 NOT_STARTED |

#### **Q{XX}.1.2 - {Görev_Adı_2}**
| Dosya | Konum | Amaç | Durum |
|-------|-------|------|-------|
| `{module2}.py` | `IMPLEMENTATION/core/{module2}/` | Ana modül | 🔴 NOT_STARTED |
| `{module2}_test.py` | `IMPLEMENTATION/core/{module2}/tests/` | Modül testleri | 🔴 NOT_STARTED |
| `__init__.py` | `IMPLEMENTATION/core/{module2}/` | Modül init | 🔴 NOT_STARTED |

### **🧪 TEST DOSYALARI**

| Test Türü | Konum | Amaç | Durum |
|-----------|-------|------|-------|
| Unit Tests | `IMPLEMENTATION/tests/unit/` | Birim testleri | 🔴 NOT_STARTED |
| Integration Tests | `IMPLEMENTATION/tests/integration/` | Entegrasyon testleri | 🔴 NOT_STARTED |
| Performance Tests | `IMPLEMENTATION/tests/performance/` | Performans testleri | 🔴 NOT_STARTED |
| End-to-End Tests | `IMPLEMENTATION/tests/e2e/` | Uçtan uca testler | 🔴 NOT_STARTED |

### **⚙️ KONFIGÜRASYON DOSYALARI**

| Dosya | Konum | Amaç | Durum |
|-------|-------|------|-------|
| `config.py` | `IMPLEMENTATION/config/` | Ana konfigürasyon | 🔴 NOT_STARTED |
| `settings.json` | `IMPLEMENTATION/config/` | JSON ayarları | 🔴 NOT_STARTED |
| `requirements.txt` | `IMPLEMENTATION/` | Python bağımlılıkları | 🔴 NOT_STARTED |

## 🔗 **BAĞIMLILIK HARİTASI**

### **İç Bağımlılıklar**
```
{module1} → {module2}
{module2} → utils/helper_functions
config → tüm modüller
```

### **Dış Bağımlılıklar**
```
Q{XX-1} Sprint → Q{XX}.1.1
Orion Vision Core → Q{XX}.1.2
External Libraries → Q{XX}.1.3
```

## 📊 **DOSYA DURUM TAKİBİ**

### **Durum Kodları**
- 🔴 **NOT_STARTED**: Henüz başlanmamış
- 🟡 **IN_PROGRESS**: Geliştirme devam ediyor
- 🔄 **TESTING**: Test aşamasında
- ✅ **COMPLETED**: Tamamlandı
- ⚠️ **BLOCKED**: Engellenmiş
- ❌ **FAILED**: Başarısız

### **Güncel Durum Özeti**
- **Toplam Dosya**: {TOPLAM_DOSYA_SAYISI}
- **Tamamlanan**: {TAMAMLANAN_SAYISI} ✅
- **Devam Eden**: {DEVAM_EDEN_SAYISI} 🟡
- **Bekleyen**: {BEKLEYEN_SAYISI} 🔴

## 🎯 **DOSYA OLUŞTURMA SIRASI**

### **Faz 1: Temel Altyapı**
1. `config.py` - Konfigürasyon sistemi
2. `utils/` - Yardımcı fonksiyonlar
3. `__init__.py` dosyaları - Modül yapısı

### **Faz 2: Ana Modüller**
1. `{module1}.py` - İlk ana modül
2. `{module1}_test.py` - İlk modül testleri
3. `{module2}.py` - İkinci ana modül
4. `{module2}_test.py` - İkinci modül testleri

### **Faz 3: Entegrasyon**
1. `integration/` modülleri
2. Integration testleri
3. Performance testleri
4. End-to-end testleri

## 🔍 **DOSYA ARAMA REHBERİ**

### **Hızlı Erişim Komutları**
```bash
# Ana modül dosyaları
find IMPLEMENTATION/core -name "*.py" -type f

# Test dosyaları
find IMPLEMENTATION -name "*test*.py" -type f

# Konfigürasyon dosyaları
find IMPLEMENTATION/config -name "*.py" -o -name "*.json" -type f

# Dokümantasyon dosyaları
find . -name "*.md" -type f
```

### **Dosya İsimlendirme Kuralları**
- **Modül dosyaları**: `{module_name}.py`
- **Test dosyaları**: `test_{module_name}.py` veya `{module_name}_test.py`
- **Konfigürasyon**: `config.py`, `settings.json`
- **Dokümantasyon**: `BÜYÜK_HARFLER.md`
- **Yardımcı**: `{purpose}_utils.py`

## 📝 **GÜNCELLEME PROSEDÜRÜ**

### **Yeni Dosya Ekleme**
1. Bu rehbere dosya bilgilerini ekle
2. Bağımlılık haritasını güncelle
3. Durum takibini güncelle
4. Git commit ile değişiklikleri kaydet

### **Dosya Taşıma/Silme**
1. Eski konumu bu rehberden çıkar
2. Yeni konumu ekle (taşıma durumunda)
3. Bağımlılıkları kontrol et ve güncelle
4. Diğer dokümantasyonları güncelle

### **Durum Güncelleme**
1. Dosya durumunu güncelle
2. Genel durum özetini yenile
3. STATUS.md dosyasını güncelle
4. Progress tracking'i güncelle

## 💖 **DUYGULANDIK NOTLAR**

- 📁 **Her dosyanın bir amacı var** - gereksiz dosya oluşturma
- 🎯 **Tutarlı isimlendirme** - kolay bulma ve anlama
- 🔄 **Düzenli güncelleme** - güncel bilgi için kritik
- 📊 **Durum takibi** - ilerleme görünürlüğü için önemli

**🌟 WAKE UP ORION! DOSYA KONUMLARI NET!**

---

**Son Güncelleme**: {TARIH}  
**Güncelleme Sıklığı**: Her dosya değişikliğinde  
**Sorumlu**: Sprint Development Team  
**Onay**: Q-Task Architecture Team
