# 📖 ORION CLEAN USAGE GUIDE

## 🧹 TEMİZ YERDE ÇALIŞMA KILAVUZU

### 📦 Import Kullanımı:

#### ✅ YENİ YÖNTEM:
```python
# Common imports
from orion_clean.imports.orion_common import logging, os, time, Dict, Any

# Sprint imports  
from orion_clean.imports.orion_sprints import TaskDecomposer, ContextAnalyzer
```

#### ❌ ESKİ YÖNTEM:
```python
from q03_task_decomposition import DeliAdamTaskDecomposer
import logging
import os
```

### 📁 Klasör Yapısı:
- `orion_clean/imports/` - Import modules
- `orion_clean/core/` - Core modules
- `orion_clean/tests/` - Test modules
- `orion_legacy/` - Legacy files

### 🎯 Faydalar:
- ✅ Temiz import'lar
- ✅ Organize yapı
- ✅ Kolay bakım
- ✅ Hızlı geliştirme

### 🚀 Sonraki Adımlar:
1. Yeni import'ları kullan
2. Clean structure'da çalış
3. Legacy'yi referans için kullan
4. Q04 development'a başla
