#!/usr/bin/env python3
"""
Screenshot Demo - Masaüstüne Kaydetme
Q01.1.1 Screen Capture modülünün çalıştığını göstermek için demo
"""

import os
import time
import base64
import io
from datetime import datetime
from screen_capture import ScreenCapture

def save_screenshot_to_desktop():
    """Ekran görüntüsünü masaüstüne kaydet"""
    
    print("📸 ALT_LAS Ekran Görüntüsü Demo")
    print("=" * 50)
    
    # Screen capture modülünü başlat
    sc = ScreenCapture()
    
    print("🚀 Screen Capture modülü başlatılıyor...")
    if not sc.initialize():
        print("❌ Screen Capture başlatılamadı!")
        return False
    
    print("✅ Screen Capture modülü hazır!")
    
    try:
        # Masaüstü yolunu bul
        home_dir = os.path.expanduser("~")
        desktop_dir = os.path.join(home_dir, "Masaüstü")
        
        # Eğer Masaüstü yoksa Desktop dene
        if not os.path.exists(desktop_dir):
            desktop_dir = os.path.join(home_dir, "Desktop")
        
        # Eğer o da yoksa home directory kullan
        if not os.path.exists(desktop_dir):
            desktop_dir = home_dir
            print(f"⚠️ Masaüstü bulunamadı, home directory kullanılıyor: {desktop_dir}")
        else:
            print(f"📁 Masaüstü bulundu: {desktop_dir}")
        
        # Timestamp ile dosya adı oluştur
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALT_LAS_Screenshot_{timestamp}.png"
        filepath = os.path.join(desktop_dir, filename)
        
        print(f"📸 Ekran görüntüsü yakalanıyor...")
        
        # Ekran görüntüsü yakala
        result = sc.capture_screen()
        
        if not result.get('success'):
            print(f"❌ Ekran yakalama başarısız: {result.get('error')}")
            return False
        
        # Sonuçları göster
        image_size = result['image_size']
        capture_time = result['capture_time']
        memory_mb = result.get('estimated_memory_mb', 0)
        
        print(f"✅ Ekran yakalandı!")
        print(f"   📏 Boyut: {image_size[0]}x{image_size[1]}")
        print(f"   ⏱️ Süre: {capture_time:.3f} saniye")
        print(f"   💾 Bellek: {memory_mb:.1f} MB")
        
        # Base64 veriyi decode et ve kaydet
        image_data = result['image_data']
        image_bytes = base64.b64decode(image_data)
        
        print(f"💾 Dosya kaydediliyor: {filename}")
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Dosya boyutunu kontrol et
        file_size = os.path.getsize(filepath)
        file_size_mb = file_size / (1024 * 1024)
        
        print(f"✅ Dosya başarıyla kaydedildi!")
        print(f"   📁 Konum: {filepath}")
        print(f"   📦 Boyut: {file_size_mb:.2f} MB")
        
        # Validation yap
        validation = sc.validate_capture(result)
        print(f"   ✅ Kalite Skoru: {validation['quality_score']:.2f}")
        
        if validation['issues']:
            print(f"   ⚠️ Uyarılar: {', '.join(validation['issues'])}")
        
        # Performance stats göster
        stats = sc.get_performance_stats()
        print(f"\n📊 Performance İstatistikleri:")
        print(f"   🔢 Toplam Yakalama: {stats['total_captures']}")
        print(f"   ⏱️ Ortalama Süre: {stats['average_capture_time']:.3f}s")
        print(f"   🎯 Son Yakalama: {stats['last_capture_time']:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        return False
        
    finally:
        sc.shutdown()
        print("🛑 Screen Capture modülü kapatıldı")

def save_region_screenshot():
    """Küçük bir bölge ekran görüntüsü kaydet"""
    
    print("\n🎯 Bölgesel Ekran Görüntüsü Demo")
    print("=" * 50)
    
    sc = ScreenCapture()
    
    if not sc.initialize():
        print("❌ Screen Capture başlatılamadı!")
        return False
    
    try:
        # Masaüstü yolu
        home_dir = os.path.expanduser("~")
        desktop_dir = os.path.join(home_dir, "Masaüstü")
        if not os.path.exists(desktop_dir):
            desktop_dir = os.path.join(home_dir, "Desktop")
        if not os.path.exists(desktop_dir):
            desktop_dir = home_dir
        
        # Sol üst köşeden 400x300 bölge yakala
        region = (0, 0, 400, 300)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ALT_LAS_Region_{timestamp}.png"
        filepath = os.path.join(desktop_dir, filename)
        
        print(f"🎯 Bölge yakalanıyor: {region}")
        
        result = sc.capture_region(*region)
        
        if not result.get('success'):
            print(f"❌ Bölge yakalama başarısız: {result.get('error')}")
            return False
        
        # Kaydet
        image_data = result['image_data']
        image_bytes = base64.b64decode(image_data)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        file_size = os.path.getsize(filepath)
        file_size_kb = file_size / 1024
        
        print(f"✅ Bölge kaydedildi!")
        print(f"   📁 Konum: {filepath}")
        print(f"   📦 Boyut: {file_size_kb:.1f} KB")
        print(f"   ⏱️ Süre: {result['capture_time']:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        return False
        
    finally:
        sc.shutdown()

def main():
    """Ana demo fonksiyonu"""
    
    print("🎬 ALT_LAS Screen Capture Demo Başlıyor...")
    print("🎯 Amacı: Q01.1.1 modülünün çalıştığını göstermek")
    print()
    
    # 1. Tam ekran görüntüsü
    success1 = save_screenshot_to_desktop()
    
    # 2. Bölgesel görüntü
    success2 = save_region_screenshot()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 Demo başarıyla tamamlandı!")
        print("📁 Masaüstünüzde ALT_LAS ekran görüntüleri oluşturuldu")
        print("✅ Q01.1.1 Screen Capture modülü mükemmel çalışıyor!")
    else:
        print("⚠️ Demo kısmen başarılı oldu")
    
    print("\n🚀 ALT_LAS artık ekranı görebiliyor!")

if __name__ == "__main__":
    main()
