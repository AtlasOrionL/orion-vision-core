# 📁 **FILE_LOCATION_GUIDE - Q02 OTONOM ÇEVRE ETKİLEŞİMİ**

## 💖 **DUYGULANDIK! ORION'UN MESAJI: "NEYİN NEREDE OLDUĞUNU BİLELİM!"**

### **🎯 Q02 DOSYA KONUM REHBERİ**

Bu rehber, Q02 Otonom Çevre Etkileşimi sprintindeki tüm dosyaların konumlarını ve amaçlarını detaylandırır.

## 📊 **ANA KLASÖR YAPISI**

### **🎯 Q02 GÖREV KLASÖRÜ**
```
docs/Q_Tasks/Q02_Otonom_Cevre_Etkilesimi/
├── README.md                       # Sprint genel bakış 🔴 NOT_STARTED
├── STATUS.md                       # Güncel durum takibi 🔴 NOT_STARTED
├── TASKS.md                        # Detaylı görev listesi 🔴 NOT_STARTED
├── ARCHITECTURE.md                 # Sprint özel mimari 🔴 NOT_STARTED
├── FILE_LOCATION_GUIDE.md          # Bu dosya ✅ COMPLETED
├── CHECKPOINTS.md                  # Kontrol noktaları 🔴 NOT_STARTED
├── TESTS.md                        # Test senaryoları 🔴 NOT_STARTED
├── IMPLEMENTATION/                 # Kod implementasyonu 🔴 NOT_STARTED
└── NOTES.md                        # Notlar ve gözlemler 🔴 NOT_STARTED
```

### **🚀 IMPLEMENTATION KLASÖRÜ (PLANLI)**
```
IMPLEMENTATION/
├── core/                           # Ana modüller
│   ├── environment/                # Q02.1.1 - Çevre Algısı
│   │   ├── environment_sensor.py  # Çevre sensörü 🔴 NOT_STARTED
│   │   ├── context_analyzer.py    # Bağlam analizi 🔴 NOT_STARTED
│   │   └── __init__.py            # Modül init 🔴 NOT_STARTED
│   ├── targeting/                 # Q02.1.2 - Hedef Belirleme
│   │   ├── target_selector.py     # Hedef seçici 🔴 NOT_STARTED
│   │   ├── priority_manager.py    # Öncelik yöneticisi 🔴 NOT_STARTED
│   │   └── __init__.py            # Modül init 🔴 NOT_STARTED
│   ├── coordination/              # Q02.2.1 - Görev Koordinasyonu
│   │   ├── task_coordinator.py    # Görev koordinatörü 🔴 NOT_STARTED
│   │   ├── resource_manager.py    # Kaynak yöneticisi 🔴 NOT_STARTED
│   │   └── __init__.py            # Modül init 🔴 NOT_STARTED
│   └── learning/                  # Q02.2.2 - Adaptif Öğrenme
│       ├── adaptive_learner.py    # Adaptif öğrenme 🔴 NOT_STARTED
│       ├── pattern_recognizer.py  # Desen tanıma 🔴 NOT_STARTED
│       └── __init__.py            # Modül init 🔴 NOT_STARTED
├── integration/                   # Entegrasyon modülleri
│   ├── q01_bridge/                # Q01 entegrasyonu
│   │   ├── vision_bridge.py       # Görsel köprü 🔴 NOT_STARTED
│   │   └── __init__.py            # Modül init 🔴 NOT_STARTED
│   └── external/                  # Dış entegrasyonlar
│       ├── api_connector.py       # API bağlayıcı 🔴 NOT_STARTED
│       └── __init__.py            # Modül init 🔴 NOT_STARTED
├── utils/                         # Yardımcı fonksiyonlar
│   ├── q02_utils.py               # Q02 özel yardımcılar 🔴 NOT_STARTED
│   └── __init__.py                # Modül init 🔴 NOT_STARTED
├── config/                        # Konfigürasyon dosyaları
│   ├── q02_config.py              # Q02 konfigürasyonu 🔴 NOT_STARTED
│   └── __init__.py                # Modül init 🔴 NOT_STARTED
├── tests/                         # Test dosyaları
│   ├── unit/                      # Birim testleri
│   ├── integration/               # Entegrasyon testleri
│   └── performance/               # Performans testleri
└── docs/                          # Teknik dokümantasyon
```

## 📋 **DOSYA DETAYLARI**

### **📚 DOKÜMANTASYON DOSYALARI**

| Dosya | Konum | Amaç | Durum | Hedef Tamamlama |
|-------|-------|------|-------|-----------------|
| `README.md` | `Q02_Otonom_Cevre_Etkilesimi/` | Sprint genel bakış | 🔴 NOT_STARTED | Sprint başında |
| `STATUS.md` | `Q02_Otonom_Cevre_Etkilesimi/` | Güncel durum | 🔴 NOT_STARTED | Günlük güncelleme |
| `TASKS.md` | `Q02_Otonom_Cevre_Etkilesimi/` | Görev detayları | 🔴 NOT_STARTED | Sprint başında |
| `ARCHITECTURE.md` | `Q02_Otonom_Cevre_Etkilesimi/` | Mimari kararlar | 🔴 NOT_STARTED | Mimari tasarım |
| `FILE_LOCATION_GUIDE.md` | `Q02_Otonom_Cevre_Etkilesimi/` | Bu dosya | ✅ COMPLETED | BUGÜN |
| `CHECKPOINTS.md` | `Q02_Otonom_Cevre_Etkilesimi/` | Kontrol noktaları | 🔴 NOT_STARTED | Sprint başında |
| `TESTS.md` | `Q02_Otonom_Cevre_Etkilesimi/` | Test senaryoları | 🔴 NOT_STARTED | Test tasarımı |
| `NOTES.md` | `Q02_Otonom_Cevre_Etkilesimi/` | Notlar | 🔴 NOT_STARTED | Gerektiğinde |

### **💻 KOD DOSYALARI (PLANLI)**

#### **Q02.1.1 - Gelişmiş Çevre Algısı**
| Dosya | Konum | Amaç | Durum | Bağımlılık |
|-------|-------|------|-------|------------|
| `environment_sensor.py` | `IMPLEMENTATION/core/environment/` | Çevre sensörü | 🔴 NOT_STARTED | Q01 Vision |
| `context_analyzer.py` | `IMPLEMENTATION/core/environment/` | Bağlam analizi | 🔴 NOT_STARTED | environment_sensor |
| `test_environment_sensor.py` | `IMPLEMENTATION/tests/unit/` | Çevre sensörü testi | 🔴 NOT_STARTED | environment_sensor |

#### **Q02.1.2 - Dinamik Hedef Belirleme**
| Dosya | Konum | Amaç | Durum | Bağımlılık |
|-------|-------|------|-------|------------|
| `target_selector.py` | `IMPLEMENTATION/core/targeting/` | Hedef seçici | 🔴 NOT_STARTED | context_analyzer |
| `priority_manager.py` | `IMPLEMENTATION/core/targeting/` | Öncelik yöneticisi | 🔴 NOT_STARTED | target_selector |
| `test_target_selector.py` | `IMPLEMENTATION/tests/unit/` | Hedef seçici testi | 🔴 NOT_STARTED | target_selector |

#### **Q02.2.1 - Çoklu Görev Koordinasyonu**
| Dosya | Konum | Amaç | Durum | Bağımlılık |
|-------|-------|------|-------|------------|
| `task_coordinator.py` | `IMPLEMENTATION/core/coordination/` | Görev koordinatörü | 🔴 NOT_STARTED | Q01 TaskEngine |
| `resource_manager.py` | `IMPLEMENTATION/core/coordination/` | Kaynak yöneticisi | 🔴 NOT_STARTED | task_coordinator |
| `test_task_coordinator.py` | `IMPLEMENTATION/tests/unit/` | Koordinatör testi | 🔴 NOT_STARTED | task_coordinator |

#### **Q02.2.2 - Adaptif Öğrenme Sistemi**
| Dosya | Konum | Amaç | Durum | Bağımlılık |
|-------|-------|------|-------|------------|
| `adaptive_learner.py` | `IMPLEMENTATION/core/learning/` | Adaptif öğrenme | 🔴 NOT_STARTED | Tüm Q02 modüller |
| `pattern_recognizer.py` | `IMPLEMENTATION/core/learning/` | Desen tanıma | 🔴 NOT_STARTED | adaptive_learner |
| `test_adaptive_learner.py` | `IMPLEMENTATION/tests/unit/` | Öğrenme testi | 🔴 NOT_STARTED | adaptive_learner |

### **🔗 ENTEGRASYON DOSYALARI**

| Dosya | Konum | Amaç | Durum | Bağımlılık |
|-------|-------|------|-------|------------|
| `vision_bridge.py` | `IMPLEMENTATION/integration/q01_bridge/` | Q01 köprüsü | 🔴 NOT_STARTED | Q01 tüm modüller |
| `api_connector.py` | `IMPLEMENTATION/integration/external/` | Dış API bağlantısı | 🔴 NOT_STARTED | - |

### **⚙️ KONFIGÜRASYON VE YARDIMCI DOSYALAR**

| Dosya | Konum | Amaç | Durum | Bağımlılık |
|-------|-------|------|-------|------------|
| `q02_config.py` | `IMPLEMENTATION/config/` | Q02 konfigürasyonu | 🔴 NOT_STARTED | Q01 config |
| `q02_utils.py` | `IMPLEMENTATION/utils/` | Q02 yardımcıları | 🔴 NOT_STARTED | Q01 utils |

## 📊 **DOSYA DURUM TAKİBİ**

### **Durum Kodları**
- 🔴 **NOT_STARTED**: Henüz başlanmamış
- 🟡 **IN_PROGRESS**: Geliştirme devam ediyor
- 🔄 **TESTING**: Test aşamasında
- ✅ **COMPLETED**: Tamamlandı
- ⚠️ **BLOCKED**: Engellenmiş
- ❌ **FAILED**: Başarısız

### **Güncel Durum Özeti**
- **Toplam Dosya**: 25 dosya (planlanan)
- **Tamamlanan**: 1 dosya ✅ (%4)
- **Devam Eden**: 0 dosya 🟡 (%0)
- **Bekleyen**: 24 dosya 🔴 (%96)

### **Kategori Bazında Durum**
- **Dokümantasyon**: 1/8 ✅ (%12.5)
- **Core Modüller**: 0/8 🔴 (%0)
- **Integration Modüller**: 0/2 🔴 (%0)
- **Test Dosyaları**: 0/4 🔴 (%0)
- **Utility Dosyaları**: 0/2 🔴 (%0)
- **Config Dosyaları**: 0/1 🔴 (%0)

## 🔗 **BAĞIMLILIK HARİTASI**

### **Q01 Bağımlılıkları**
```
Q02.environment_sensor → Q01.VisualProcessingPipeline
Q02.context_analyzer → Q01.UIElementDetector
Q02.target_selector → Q01.AutonomousActionSystem
Q02.task_coordinator → Q01.TaskExecutionEngine
Q02.vision_bridge → Q01.tüm_modüller
```

### **İç Bağımlılıklar**
```
context_analyzer → environment_sensor
target_selector → context_analyzer
priority_manager → target_selector
task_coordinator → priority_manager
resource_manager → task_coordinator
adaptive_learner → tüm_Q02_modüller
pattern_recognizer → adaptive_learner
```

### **Dış Bağımlılıklar**
```
Machine Learning Libraries → adaptive_learner
External APIs → api_connector
Database Systems → resource_manager
Monitoring Tools → task_coordinator
```

## 🎯 **DOSYA OLUŞTURMA SIRASI (PLANLI)**

### **Faz 1: Temel Altyapı (1. Hafta)**
1. 🔴 `q02_config.py` - Q02 konfigürasyon sistemi
2. 🔴 `q02_utils.py` - Q02 yardımcı fonksiyonlar
3. 🔴 `vision_bridge.py` - Q01 entegrasyon köprüsü
4. 🔴 `__init__.py` dosyaları - Modül yapısı

### **Faz 2: Çevre Algısı (2. Hafta)**
1. 🔴 `environment_sensor.py` - Çevre sensörü
2. 🔴 `context_analyzer.py` - Bağlam analizi
3. 🔴 `test_environment_sensor.py` - Çevre sensörü testleri

### **Faz 3: Hedef Belirleme (3. Hafta)**
1. 🔴 `target_selector.py` - Hedef seçici
2. 🔴 `priority_manager.py` - Öncelik yöneticisi
3. 🔴 `test_target_selector.py` - Hedef seçici testleri

### **Faz 4: Koordinasyon ve Öğrenme (4. Hafta)**
1. 🔴 `task_coordinator.py` - Görev koordinatörü
2. 🔴 `resource_manager.py` - Kaynak yöneticisi
3. 🔴 `adaptive_learner.py` - Adaptif öğrenme
4. 🔴 `pattern_recognizer.py` - Desen tanıma

## 🔍 **DOSYA ARAMA REHBERİ**

### **Hızlı Erişim Komutları (Gelecek)**
```bash
# Q02 ana modül dosyaları
find docs/Q_Tasks/Q02_Otonom_Cevre_Etkilesimi/IMPLEMENTATION/core -name "*.py" -type f

# Q02 test dosyaları
find docs/Q_Tasks/Q02_Otonom_Cevre_Etkilesimi/IMPLEMENTATION/tests -name "*.py" -type f

# Q02 dokümantasyon dosyaları
find docs/Q_Tasks/Q02_Otonom_Cevre_Etkilesimi -name "*.md" -type f

# Q02 konfigürasyon dosyaları
find docs/Q_Tasks/Q02_Otonom_Cevre_Etkilesimi/IMPLEMENTATION/config -name "*.py" -type f
```

### **Dosya İsimlendirme Kuralları**
- **Modül dosyaları**: `{module_name}.py`
- **Test dosyaları**: `test_{module_name}.py`
- **Konfigürasyon**: `q02_config.py`
- **Dokümantasyon**: `BÜYÜK_HARFLER.md`
- **Yardımcı**: `q02_utils.py`

## 💖 **DUYGULANDIK Q02 HAZIRLIK RAPORU**

### **🎯 ORION'UN MESAJI UYGULAMASI:**
- ✅ **FILE_LOCATION_GUIDE** oluşturuldu
- 🎯 **Tüm dosya konumları** planlandı
- 📊 **Bağımlılık haritası** çıkarıldı
- 🔄 **Oluşturma sırası** belirlendi
- 📁 **Modüler yapı** Q01'den devralındı

### **🚀 SONRAKI ADIMLAR:**
1. Q02 dokümantasyon dosyalarını oluştur
2. Q02 mimari tasarımını tamamla
3. Q01 entegrasyon köprüsünü kur
4. İlk modül geliştirmeye başla

**🌟 WAKE UP ORION! Q02 DOSYA KONUMLARI HAZIR!**

---

**Son Güncelleme**: BUGÜN - Q02 Hazırlık Aşaması  
**Güncelleme Sıklığı**: Her dosya ekleme/değişikliğinde  
**Sorumlu**: Q02 Development Team  
**Onay**: Q-Task Architecture Team  
**Önceki Sprint**: Q01 (TAMAMLANDI)  
**Sonraki Sprint**: Q03 (BEKLEMEDE)
