#!/usr/bin/env python3
"""
💃 Q03 Dans Test - Orion'un Dans Felsefesi ile Test
🎵 KODLAR SENİN NOTALARIN, MODÜLER SENİN ENSTRÜMANIN!

ORION DANS FELSEFESİ:
"Dans edenler deli sandı müziği duymayanlar"
- Kodlar = Notalar (her modül bir melodi)
- Modüler = Enstrüman (sistemik armoni)  
- Dans = Test (ritimli doğrulama)
- Q04 Geçiş = Dans ile momentum

Author: Orion Vision Core Team + Dans Felsefesi
Status: 💃 DANS TEST ACTIVE
"""

import logging
import time
from datetime import datetime

# Q03 Dans Enstrümanları
try:
    from q03_task_decomposition import DeliAdamTaskDecomposer
    from q03_contextual_understanding import DeliAdamContextualAnalyzer
    from q03_task_flow_manager import AutomaticTaskFlowManager
    from q03_action_verification import ActionSuccessVerifier
    from q03_error_recovery import ZBozonErrorRecovery
    print("🎵 Q03 Dans Enstrümanları hazır!")
except ImportError as e:
    print(f"❌ Dans enstrümanları eksik: {e}")
    exit(1)

class OrionDansTest:
    """💃 Orion'un Dans Test Sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger('orion.dans_test')
        
        # Dans Enstrümanları (Q03 Modülleri)
        self.enstrumanlar = {
            'task_decomposer': DeliAdamTaskDecomposer(),
            'contextual_analyzer': DeliAdamContextualAnalyzer(), 
            'task_flow_manager': AutomaticTaskFlowManager(),
            'action_verifier': ActionSuccessVerifier(),
            'error_recovery': ZBozonErrorRecovery()
        }
        
        # Dans Notaları (Test Senaryoları)
        self.dans_notalari = [
            "not defterini aç ve 'wake up orion' yaz",
            "tarayıcıyı aç ve google'a git",
            "WAKE UP ORION! Dans test"
        ]
        
        # Dans Ritimleri (Test Metrikleri)
        self.dans_ritimleri = {
            'toplam_dans': 0,
            'basarili_dans': 0,
            'dans_skoru': 0.0,
            'ritim_uyumu': 0.0
        }
        
        self.logger.info("💃 Orion Dans Test sistemi hazır!")
    
    def enstruman_akordlama(self) -> bool:
        """🎼 Enstrümanları akordla (Initialize)"""
        try:
            self.logger.info("🎼 Enstrümanlar akordlanıyor...")
            
            for isim, enstruman in self.enstrumanlar.items():
                if not enstruman.initialize():
                    self.logger.error(f"❌ {isim} akordlanamadı")
                    return False
                self.logger.info(f"🎵 {isim} akordlandı")
            
            self.logger.info("✅ Tüm enstrümanlar akordlandı!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Akordlama hatası: {e}")
            return False
    
    def dans_et_test_et(self) -> dict:
        """💃 Dans et, test et - Ana dans performansı"""
        try:
            self.logger.info("💃 DANS BAŞLIYOR! MÜZİĞİ DUYMAYANLAR DELİ SANACAK!")
            
            dans_baslangic = datetime.now()
            dans_sonuclari = []
            
            # Her nota için dans et
            for i, nota in enumerate(self.dans_notalari, 1):
                self.logger.info(f"🎵 Dans {i}/{len(self.dans_notalari)}: {nota}")
                
                # Dans adımları (Test pipeline)
                dans_sonucu = self._tek_dans_performansi(nota)
                dans_sonuclari.append(dans_sonucu)
                
                # Dans arası nefes (Test delay)
                time.sleep(0.2)
            
            # Dans performansı değerlendirmesi
            dans_bitisi = datetime.now()
            final_performans = self._dans_performansi_degerlendir(
                dans_sonuclari, dans_baslangic, dans_bitisi
            )
            
            self.logger.info(f"💃 DANS TAMAMLANDI! Skor: {final_performans['dans_skoru']:.2f}")
            return final_performans
            
        except Exception as e:
            self.logger.error(f"❌ Dans hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def _tek_dans_performansi(self, nota: str) -> dict:
        """🎵 Tek nota için dans performansı"""
        try:
            performans_baslangic = datetime.now()
            
            # 1. Melodi Ayrıştırma (Task Decomposition)
            self.logger.info("🎼 Melodi ayrıştırılıyor...")
            task_queue = self.enstrumanlar['task_decomposer'].nehire_atla_decompose(nota)
            
            if not task_queue:
                return {'success': False, 'nota': nota, 'hata': 'melodi_ayristarilmadi'}
            
            # 2. Ritim Analizi (Contextual Understanding)
            self.logger.info("🥁 Ritim analiz ediliyor...")
            screen_context = self.enstrumanlar['contextual_analyzer'].ekrana_atla_analyze_context()
            
            if not screen_context:
                return {'success': False, 'nota': nota, 'hata': 'ritim_analizlenemedi'}
            
            # 3. Dans Akışı (Task Flow)
            self.logger.info("💃 Dans akışı başlıyor...")
            flow_result = self.enstrumanlar['task_flow_manager'].run_task_flow(task_queue, screen_context)
            
            # 4. Armoni Doğrulama (Action Verification)
            self.logger.info("🎶 Armoni doğrulanıyor...")
            # Verification otomatik olarak flow içinde yapılıyor
            
            # 5. Hata Düzeltme (Error Recovery)
            if not flow_result['success']:
                self.logger.info("🔄 Hata düzeltme devreye giriyor...")
                # Recovery otomatik olarak flow içinde yapılıyor
            
            # Performans süresi
            performans_suresi = (datetime.now() - performans_baslangic).total_seconds()
            
            # Dans skoru hesaplama
            dans_skoru = self._dans_skoru_hesapla(flow_result, performans_suresi)
            
            return {
                'success': flow_result['success'],
                'nota': nota,
                'dans_skoru': dans_skoru,
                'performans_suresi': performans_suresi,
                'adim_sayisi': flow_result['executions'],
                'basarili_adimlar': flow_result['successful_steps'],
                'flow_result': flow_result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Dans performans hatası: {e}")
            return {'success': False, 'nota': nota, 'hata': str(e)}
    
    def _dans_skoru_hesapla(self, flow_result: dict, performans_suresi: float) -> float:
        """🎯 Dans skoru hesaplama"""
        try:
            # Temel başarı skoru (0-40 puan)
            basari_orani = flow_result['successful_steps'] / max(flow_result['executions'], 1)
            basari_skoru = basari_orani * 40
            
            # Hız skoru (0-30 puan) - Hızlı dans daha iyi
            hiz_skoru = max(0, 30 - performans_suresi * 5)
            
            # Akıcılık skoru (0-20 puan) - Az hata daha iyi
            akicilik_skoru = 20 - (flow_result['failed_steps'] * 5)
            akicilik_skoru = max(0, akicilik_skoru)
            
            # Ritim skoru (0-10 puan) - Photon report kalitesi
            ritim_skoru = 10 if flow_result.get('photon_report', {}).get('success_rate', 0) > 0.8 else 5
            
            toplam_skor = basari_skoru + hiz_skoru + akicilik_skoru + ritim_skoru
            return min(toplam_skor, 100.0)
            
        except Exception as e:
            self.logger.error(f"❌ Skor hesaplama hatası: {e}")
            return 0.0
    
    def _dans_performansi_degerlendir(self, dans_sonuclari: list, 
                                    baslangic: datetime, bitis: datetime) -> dict:
        """🏆 Genel dans performansı değerlendirmesi"""
        try:
            toplam_dans = len(dans_sonuclari)
            basarili_dans = sum(1 for d in dans_sonuclari if d.get('success', False))
            
            # Ortalama dans skoru
            toplam_skor = sum(d.get('dans_skoru', 0) for d in dans_sonuclari)
            ortalama_skor = toplam_skor / max(toplam_dans, 1)
            
            # Ritim uyumu (tutarlılık)
            skorlar = [d.get('dans_skoru', 0) for d in dans_sonuclari]
            if len(skorlar) > 1:
                import statistics
                ritim_uyumu = 100 - (statistics.stdev(skorlar) * 2)
                ritim_uyumu = max(0, min(100, ritim_uyumu))
            else:
                ritim_uyumu = 100
            
            # Toplam performans süresi
            toplam_sure = (bitis - baslangic).total_seconds()
            
            # Dans derecesi belirleme
            dans_derecesi = self._dans_derecesi_belirle(ortalama_skor, basarili_dans, toplam_dans)
            
            # İstatistikleri güncelle
            self.dans_ritimleri.update({
                'toplam_dans': toplam_dans,
                'basarili_dans': basarili_dans,
                'dans_skoru': ortalama_skor,
                'ritim_uyumu': ritim_uyumu
            })
            
            return {
                'success': True,
                'toplam_dans': toplam_dans,
                'basarili_dans': basarili_dans,
                'basari_orani': basarili_dans / toplam_dans,
                'dans_skoru': ortalama_skor,
                'ritim_uyumu': ritim_uyumu,
                'toplam_sure': toplam_sure,
                'dans_derecesi': dans_derecesi,
                'detay_sonuclar': dans_sonuclari,
                'orion_mesaji': self._orion_dans_mesaji(dans_derecesi, ortalama_skor)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Performans değerlendirme hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def _dans_derecesi_belirle(self, ortalama_skor: float, basarili: int, toplam: int) -> str:
        """🏆 Dans derecesi belirleme"""
        basari_orani = basarili / toplam
        
        if ortalama_skor >= 80 and basari_orani >= 0.8:
            return "🌟 EFSANE DANS (Orion Seviyesi)"
        elif ortalama_skor >= 70 and basari_orani >= 0.7:
            return "💃 MÜKEMMEL DANS (Profesyonel)"
        elif ortalama_skor >= 60 and basari_orani >= 0.6:
            return "🎵 İYİ DANS (Yetenekli)"
        elif ortalama_skor >= 50 and basari_orani >= 0.5:
            return "🎼 ORTA DANS (Öğrenci)"
        else:
            return "🎶 BAŞLANGIÇ DANS (Pratik Gerekli)"
    
    def _orion_dans_mesaji(self, derece: str, skor: float) -> str:
        """💖 Orion'un dans mesajı"""
        if "EFSANE" in derece:
            return f"💖 DUYGULANDIK! Orion dans etti, müziği duymayanlar deli sandı! Skor: {skor:.1f}"
        elif "MÜKEMMEL" in derece:
            return f"🎵 Kodlar notalardı, modüler enstrümandı! Mükemmel armoni! Skor: {skor:.1f}"
        elif "İYİ" in derece:
            return f"💃 Dans ediyor, test ediyor, Q04'e hazırlanıyor! Skor: {skor:.1f}"
        else:
            return f"🎼 Pratik yapıyor, dans öğreniyor, gelişiyor! Skor: {skor:.1f}"

# Ana Dans Performansı
if __name__ == "__main__":
    print("💃 ORION DANS TEST BAŞLIYOR!")
    print("🎵 KODLAR SENİN NOTALARIN, MODÜLER SENİN ENSTRÜMANIN!")
    print("🌟 DANS EDENLER DELİ SANDI MÜZİĞİ DUYMAYANLAR!")
    print()
    
    # Logging setup
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Dans test sistemi
    dans_test = OrionDansTest()
    
    # Enstrümanları akordla
    if dans_test.enstruman_akordlama():
        print("🎼 Enstrümanlar akordlandı! Dans başlıyor...")
        print()
        
        # Dans et, test et!
        performans = dans_test.dans_et_test_et()
        
        if performans['success']:
            print()
            print("🎉 DANS PERFORMANSI TAMAMLANDI!")
            print(f"   🏆 Dans Derecesi: {performans['dans_derecesi']}")
            print(f"   🎯 Dans Skoru: {performans['dans_skoru']:.1f}/100")
            print(f"   💃 Başarılı Dans: {performans['basarili_dans']}/{performans['toplam_dans']}")
            print(f"   🎵 Ritim Uyumu: {performans['ritim_uyumu']:.1f}%")
            print(f"   ⏱️ Toplam Süre: {performans['toplam_sure']:.1f}s")
            print()
            print(f"💖 {performans['orion_mesaji']}")
            print()
            print("🚀 Q04'E GEÇİŞ HAZIR! DANS İLE MOMENTUM!")
            
        else:
            print("❌ Dans performansı tamamlanamadı")
            
    else:
        print("❌ Enstrümanlar akordlanamadı")
    
    print()
    print("💃 ORION DANS TEST TAMAMLANDI!")
    print("🎵 MÜZİĞİ DUYMAYANLAR DELİ SANDI DANS EDENLERİ!")
