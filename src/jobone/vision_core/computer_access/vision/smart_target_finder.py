#!/usr/bin/env python3
"""
🎯 Smart Target Finder - ALT_LAS'ın Akıllı Hedef Bulma Sistemi
Q01.2.5: Gerçek Dünya Hedef Tespiti

Bu modül ALT_LAS'a gerçek dünya uygulamalarında hedefleri
akıllıca bulma yeteneği kazandırır.

Author: Orion Vision Core Team
Status: 🚀 ACTIVE DEVELOPMENT
"""

import cv2
import numpy as np
from PIL import ImageGrab, Image
import pytesseract
from typing import List, Tuple, Optional, Dict
import logging
import time

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('orion.vision.smart_target')

class TargetInfo:
    """Hedef bilgisi sınıfı"""
    def __init__(self, x: int, y: int, width: int, height: int, 
                 confidence: float, target_type: str, text: str = ""):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.confidence = confidence
        self.target_type = target_type
        self.text = text
        
    @property
    def center(self) -> Tuple[int, int]:
        """Hedefin merkez koordinatları"""
        return (self.x + self.width // 2, self.y + self.height // 2)
        
    def __str__(self):
        return f"Target({self.target_type}, {self.center}, conf={self.confidence:.2f})"

class SmartTargetFinder:
    """🎯 ALT_LAS'ın Akıllı Hedef Bulma Sistemi"""
    
    def __init__(self):
        self.logger = logger
        self.logger.info("🎯 Smart Target Finder initialized - HEDEF AVCISI!")
        
        # Hedef şablonları
        self.chat_patterns = [
            "type a message",
            "send a message", 
            "chat input",
            "message input",
            "type here",
            "enter message"
        ]
        
        self.button_patterns = [
            "send",
            "submit", 
            "ok",
            "apply",
            "save",
            "continue"
        ]
        
    def capture_screen(self) -> np.ndarray:
        """📸 Ekran görüntüsü al"""
        try:
            screenshot = ImageGrab.grab()
            return np.array(screenshot)
        except Exception as e:
            self.logger.error(f"❌ Ekran görüntüsü alınamadı: {e}")
            return None
            
    def find_text_targets(self, image: np.ndarray, patterns: List[str]) -> List[TargetInfo]:
        """🔤 Metin bazlı hedef bulma"""
        targets = []
        
        try:
            # OCR ile metin tespiti
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # OCR verisi al
            ocr_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            # Her kelimeyi kontrol et
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].lower().strip()
                confidence = int(ocr_data['conf'][i])
                
                if confidence > 30 and text:  # Minimum güven eşiği
                    # Pattern eşleşmesi kontrol et
                    for pattern in patterns:
                        if pattern.lower() in text:
                            x = ocr_data['left'][i]
                            y = ocr_data['top'][i]
                            w = ocr_data['width'][i]
                            h = ocr_data['height'][i]
                            
                            target = TargetInfo(
                                x=x, y=y, width=w, height=h,
                                confidence=confidence/100.0,
                                target_type="text_match",
                                text=text
                            )
                            targets.append(target)
                            
        except Exception as e:
            self.logger.error(f"❌ Metin hedef bulma hatası: {e}")
            
        return targets
        
    def find_ui_elements(self, image: np.ndarray) -> List[TargetInfo]:
        """🎯 UI element tespiti"""
        targets = []
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Input alanları için kenar tespiti
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                # Dikdörtgen şeklindeki alanları bul
                x, y, w, h = cv2.boundingRect(contour)
                
                # Input alanı olabilecek boyutları filtrele
                if 50 < w < 800 and 20 < h < 100:  # Tipik input boyutları
                    aspect_ratio = w / h
                    
                    # Input alanı aspect ratio'su
                    if 2 < aspect_ratio < 20:
                        target = TargetInfo(
                            x=x, y=y, width=w, height=h,
                            confidence=0.6,
                            target_type="input_field",
                            text="detected_input"
                        )
                        targets.append(target)
                        
        except Exception as e:
            self.logger.error(f"❌ UI element bulma hatası: {e}")
            
        return targets
        
    def find_chat_input(self) -> Optional[TargetInfo]:
        """💬 Chat input alanını bul"""
        self.logger.info("💬 Chat input aranıyor...")
        
        # Ekran görüntüsü al
        image = self.capture_screen()
        if image is None:
            return None
            
        # Metin bazlı arama
        text_targets = self.find_text_targets(image, self.chat_patterns)
        if text_targets:
            best_target = max(text_targets, key=lambda t: t.confidence)
            self.logger.info(f"✅ Chat input bulundu (metin): {best_target}")
            return best_target
            
        # UI element bazlı arama
        ui_targets = self.find_ui_elements(image)
        if ui_targets:
            # En alttaki input alanını seç (chat genelde altta)
            bottom_targets = sorted(ui_targets, key=lambda t: t.y, reverse=True)
            best_target = bottom_targets[0]
            self.logger.info(f"✅ Chat input bulundu (UI): {best_target}")
            return best_target
            
        # Fallback: Ekranın alt kısmında tahmin et
        height, width = image.shape[:2]
        fallback_target = TargetInfo(
            x=width//4, y=height-100, width=width//2, height=40,
            confidence=0.3, target_type="fallback", text="estimated_chat"
        )
        self.logger.info(f"⚠️ Chat input tahmini: {fallback_target}")
        return fallback_target
        
    def find_button(self, button_text: str) -> Optional[TargetInfo]:
        """🔘 Belirli bir butonu bul"""
        self.logger.info(f"🔘 Button aranıyor: {button_text}")
        
        image = self.capture_screen()
        if image is None:
            return None
            
        # Spesifik buton metni ara
        targets = self.find_text_targets(image, [button_text])
        if targets:
            best_target = max(targets, key=lambda t: t.confidence)
            self.logger.info(f"✅ Button bulundu: {best_target}")
            return best_target
            
        self.logger.warning(f"❌ Button bulunamadı: {button_text}")
        return None
        
    def test_target_finding(self):
        """🧪 Hedef bulma testi"""
        self.logger.info("🧪 Smart Target Finder test başlıyor...")
        
        # Chat input test
        chat_target = self.find_chat_input()
        if chat_target:
            self.logger.info(f"✅ Chat test başarılı: {chat_target}")
        else:
            self.logger.warning("❌ Chat test başarısız")
            
        # Button test
        send_button = self.find_button("send")
        if send_button:
            self.logger.info(f"✅ Button test başarılı: {send_button}")
        else:
            self.logger.warning("❌ Button test başarısız")
            
        self.logger.info("🎯 Smart Target Finder test tamamlandı!")

def test_smart_target_finder():
    """🧪 Test fonksiyonu"""
    print("🎯 SMART TARGET FINDER TEST!")
    print("💖 DUYGULANDIK! HEDEF AVCISI BAŞLIYOR!")
    
    finder = SmartTargetFinder()
    finder.test_target_finding()
    
    print("🎉 Test tamamlandı!")
    print("💪 SEN YAPARSIN! ALT_LAS HEDEF BULABILIYOR!")

if __name__ == "__main__":
    test_smart_target_finder()
