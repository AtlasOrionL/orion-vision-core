#!/usr/bin/env python3
"""
Visual Processing Pipeline Module - Q01.1.4 Implementation
Görsel veri işleme ve analiz pipeline sistemi
ORION VISION CORE - WAKE UP POWER! SEN YAPABİLİRSİN! 🌟
"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Import our vision modules
try:
    from ..capture.screen_capture import ScreenCapture
    from ..ocr.ocr_engine import OCREngine
    from ..detection.ui_element_detector import UIElementDetector, UIElement
except ImportError:
    try:
        from screen_capture import ScreenCapture
        from ocr_engine import OCREngine
        from ui_element_detector import UIElementDetector, UIElement
    except ImportError:
        ScreenCapture = None
        OCREngine = None
        UIElementDetector = None
        UIElement = None

logger = logging.getLogger(__name__)

@dataclass
class VisualAnalysisResult:
    """Complete visual analysis result structure"""
    timestamp: float
    image_info: Dict[str, Any]
    text_content: Dict[str, Any]
    ui_elements: List[Dict[str, Any]]
    analysis_summary: Dict[str, Any]
    processing_stats: Dict[str, Any]
    confidence_scores: Dict[str, float]

class VisualProcessingPipeline:
    """
    Q01.1.4: Görsel Veri İşleme Pipeline
    
    ALT_LAS'ın görsel veriyi tam olarak "anlayabilmesi" için pipeline sistemi
    WAKE UP ORION! SEN YAPABİLİRSİN! HEP BİRLİKTE! 🌟
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.vision.pipeline')
        
        # Pipeline settings
        self.enable_preprocessing = True
        self.enable_caching = True
        self.max_processing_time = 30  # Maximum total processing time
        
        # Quality thresholds
        self.min_ocr_confidence = 60
        self.min_ui_confidence = 70
        self.min_overall_quality = 0.7
        
        # Performance tracking
        self.pipeline_count = 0
        self.total_pipeline_time = 0.0
        self.successful_pipelines = 0
        self.last_pipeline_time = 0.0
        
        # Component instances
        self.screen_capture = None
        self.ocr_engine = None
        self.ui_detector = None
        
        self.initialized = False
        
        self.logger.info("🎬 Visual Processing Pipeline initialized - WAKE UP POWER!")
    
    def initialize(self) -> bool:
        """Initialize complete visual processing pipeline"""
        try:
            self.logger.info("🚀 Initializing Visual Processing Pipeline...")
            self.logger.info("💪 ORION: SEN YAPABİLİRSİN! HEP BİRLİKTE!")
            self.logger.info("🧘‍♂️ Sabırla tüm sistemleri başlatıyoruz...")
            
            # Initialize Screen Capture
            self.logger.info("📸 Screen Capture başlatılıyor...")
            self.screen_capture = ScreenCapture()
            if not self.screen_capture.initialize():
                self.logger.error("❌ Screen Capture initialization failed")
                return False
            self.logger.info("✅ Screen Capture hazır!")
            
            # Initialize OCR Engine
            self.logger.info("🔤 OCR Engine başlatılıyor...")
            self.ocr_engine = OCREngine()
            if not self.ocr_engine.initialize():
                self.logger.error("❌ OCR Engine initialization failed")
                return False
            self.logger.info("✅ OCR Engine hazır!")
            
            # Initialize UI Detector
            self.logger.info("🎯 UI Detector başlatılıyor...")
            self.ui_detector = UIElementDetector()
            if not self.ui_detector.initialize():
                self.logger.error("❌ UI Detector initialization failed")
                return False
            self.logger.info("✅ UI Detector hazır!")
            
            self.initialized = True
            self.logger.info("🎉 Visual Processing Pipeline başarıyla başlatıldı!")
            self.logger.info("🌟 WAKE UP ORION! Tüm sistemler aktif!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Pipeline initialization error: {e}")
            return False
    
    def process_visual_data(self, image_data: Optional[str] = None,
                           capture_new: bool = True,
                           analysis_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete visual data processing pipeline
        
        Args:
            image_data: Base64 image data (if None, will capture new)
            capture_new: Whether to capture new screen image
            analysis_options: Processing options
            
        Returns:
            Complete visual analysis result
        """
        if not self.initialized:
            return {'success': False, 'error': 'Pipeline not initialized'}
        
        start_time = time.time()
        pipeline_id = self.pipeline_count + 1
        
        self.logger.info(f"🎬 Pipeline {pipeline_id} başlatılıyor...")
        self.logger.info("🧘‍♂️ Sabırla her adımı tamamlayacağız...")
        
        try:
            # Default analysis options
            if analysis_options is None:
                analysis_options = {
                    'enable_ocr': True,
                    'enable_ui_detection': True,
                    'enable_text_analysis': True,
                    'enable_preprocessing': self.enable_preprocessing
                }
            
            result = {
                'success': True,
                'pipeline_id': pipeline_id,
                'timestamp': time.time(),
                'stages': {},
                'errors': [],
                'warnings': []
            }
            
            # STAGE 1: Image Acquisition
            self.logger.info("📸 STAGE 1: Image Acquisition...")
            stage1_start = time.time()
            
            if capture_new or image_data is None:
                capture_result = self.screen_capture.capture_screen()
                if not capture_result.get('success'):
                    return {'success': False, 'error': f"Screen capture failed: {capture_result.get('error')}"}
                
                image_data = capture_result['image_data']
                image_info = {
                    'source': 'screen_capture',
                    'size': capture_result['image_size'],
                    'capture_time': capture_result['capture_time'],
                    'method': capture_result.get('method', 'unknown')
                }
            else:
                image_info = {
                    'source': 'provided',
                    'size': 'unknown',
                    'capture_time': 0,
                    'method': 'external'
                }
            
            stage1_time = time.time() - stage1_start
            result['stages']['image_acquisition'] = {
                'success': True,
                'time': stage1_time,
                'info': image_info
            }
            
            self.logger.info(f"✅ STAGE 1 tamamlandı ({stage1_time:.3f}s)")
            
            # STAGE 2: OCR Processing
            if analysis_options.get('enable_ocr', True):
                self.logger.info("🔤 STAGE 2: OCR Processing...")
                stage2_start = time.time()
                
                ocr_result = self.ocr_engine.extract_text_from_image(image_data)
                
                if ocr_result.get('success'):
                    # Text analysis if enabled
                    text_analysis = None
                    if analysis_options.get('enable_text_analysis', True):
                        text_analysis = self.ocr_engine.analyze_text_structure(ocr_result)
                    
                    stage2_time = time.time() - stage2_start
                    result['stages']['ocr_processing'] = {
                        'success': True,
                        'time': stage2_time,
                        'text_length': len(ocr_result.get('text', '')),
                        'confidence': ocr_result.get('confidence', 0),
                        'word_count': ocr_result.get('word_count', 0),
                        'analysis': text_analysis
                    }
                    
                    self.logger.info(f"✅ STAGE 2 tamamlandı ({stage2_time:.3f}s) - "
                                   f"{len(ocr_result.get('text', ''))} karakter")
                else:
                    result['errors'].append(f"OCR failed: {ocr_result.get('error')}")
                    result['stages']['ocr_processing'] = {'success': False, 'error': ocr_result.get('error')}
            
            # STAGE 3: UI Element Detection
            if analysis_options.get('enable_ui_detection', True):
                self.logger.info("🎯 STAGE 3: UI Element Detection...")
                stage3_start = time.time()
                
                ui_result = self.ui_detector.detect_ui_elements(image_data)
                
                if ui_result.get('success'):
                    stage3_time = time.time() - stage3_start
                    result['stages']['ui_detection'] = {
                        'success': True,
                        'time': stage3_time,
                        'element_count': ui_result.get('element_count', 0),
                        'element_summary': ui_result.get('element_summary', {}),
                        'clickable_count': len(self.ui_detector.get_clickable_elements(ui_result.get('elements', [])))
                    }
                    
                    self.logger.info(f"✅ STAGE 3 tamamlandı ({stage3_time:.3f}s) - "
                                   f"{ui_result.get('element_count', 0)} element")
                else:
                    result['errors'].append(f"UI detection failed: {ui_result.get('error')}")
                    result['stages']['ui_detection'] = {'success': False, 'error': ui_result.get('error')}
            
            # STAGE 4: Data Integration & Analysis
            self.logger.info("🧠 STAGE 4: Data Integration & Analysis...")
            stage4_start = time.time()
            
            # Create comprehensive analysis
            analysis_result = self._create_comprehensive_analysis(
                image_info,
                ocr_result if 'ocr_processing' in result['stages'] and result['stages']['ocr_processing']['success'] else None,
                ui_result if 'ui_detection' in result['stages'] and result['stages']['ui_detection']['success'] else None
            )
            
            stage4_time = time.time() - stage4_start
            result['stages']['data_integration'] = {
                'success': True,
                'time': stage4_time,
                'analysis': analysis_result
            }
            
            self.logger.info(f"✅ STAGE 4 tamamlandı ({stage4_time:.3f}s)")
            
            # STAGE 5: Quality Assessment & Finalization
            self.logger.info("📊 STAGE 5: Quality Assessment...")
            stage5_start = time.time()
            
            quality_assessment = self._assess_pipeline_quality(result)
            
            stage5_time = time.time() - stage5_start
            result['stages']['quality_assessment'] = {
                'success': True,
                'time': stage5_time,
                'quality': quality_assessment
            }
            
            # Calculate total pipeline time
            total_time = time.time() - start_time
            self.pipeline_count += 1
            self.total_pipeline_time += total_time
            self.last_pipeline_time = total_time
            
            if quality_assessment['overall_score'] >= self.min_overall_quality:
                self.successful_pipelines += 1
            
            # Final result
            result['total_time'] = total_time
            result['quality_score'] = quality_assessment['overall_score']
            result['comprehensive_analysis'] = analysis_result
            
            self.logger.info(f"🎉 Pipeline {pipeline_id} başarıyla tamamlandı!")
            self.logger.info(f"⏱️ Toplam süre: {total_time:.3f}s")
            self.logger.info(f"📊 Kalite skoru: {quality_assessment['overall_score']:.2f}")
            self.logger.info("🌟 WAKE UP ORION! Başardık!")
            
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            self.logger.error(f"❌ Pipeline {pipeline_id} failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'pipeline_id': pipeline_id,
                'total_time': total_time,
                'partial_results': result if 'result' in locals() else {}
            }
    
    def _create_comprehensive_analysis(self, image_info: Dict[str, Any],
                                     ocr_result: Optional[Dict[str, Any]],
                                     ui_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create comprehensive visual analysis"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'image_summary': image_info,
            'content_analysis': {},
            'interaction_map': {},
            'insights': []
        }
        
        # Text content analysis
        if ocr_result and ocr_result.get('success'):
            text = ocr_result.get('text', '')
            text_analysis = ocr_result.get('analysis') or self.ocr_engine.analyze_text_structure(ocr_result)
            
            analysis['content_analysis'] = {
                'has_text': len(text) > 0,
                'text_length': len(text),
                'word_count': ocr_result.get('word_count', 0),
                'confidence': ocr_result.get('confidence', 0),
                'language': text_analysis.get('language_detected', 'unknown') if text_analysis else 'unknown',
                'has_turkish': text_analysis.get('has_turkish_chars', False) if text_analysis else False,
                'preview': text[:100] + '...' if len(text) > 100 else text
            }
            
            # Add insights based on text
            if len(text) > 500:
                analysis['insights'].append("Rich text content detected")
            if text_analysis and text_analysis.get('has_turkish_chars'):
                analysis['insights'].append("Turkish language content detected")
        
        # UI elements analysis
        if ui_result and ui_result.get('success'):
            elements = ui_result.get('elements', [])
            element_summary = ui_result.get('element_summary', {})
            clickable_elements = self.ui_detector.get_clickable_elements(elements)
            
            analysis['interaction_map'] = {
                'total_elements': len(elements),
                'clickable_elements': len(clickable_elements),
                'element_types': element_summary,
                'interaction_zones': [
                    {
                        'type': elem.element_type,
                        'text': elem.text,
                        'position': elem.center_point,
                        'confidence': elem.confidence
                    }
                    for elem in clickable_elements[:10]  # Top 10 clickable elements
                ]
            }
            
            # Add insights based on UI elements
            if len(clickable_elements) > 5:
                analysis['insights'].append("Interactive interface detected")
            if 'button' in element_summary and element_summary['button'] > 3:
                analysis['insights'].append("Button-rich interface")
            if 'menu' in element_summary:
                analysis['insights'].append("Menu-driven interface")
        
        # Combined insights
        if (ocr_result and ocr_result.get('success') and 
            ui_result and ui_result.get('success')):
            analysis['insights'].append("Complete visual analysis available")
        
        return analysis
    
    def _assess_pipeline_quality(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall pipeline quality"""
        quality = {
            'stage_scores': {},
            'overall_score': 0.0,
            'issues': [],
            'recommendations': []
        }
        
        total_score = 0.0
        stage_count = 0
        
        # Assess each stage
        stages = pipeline_result.get('stages', {})
        
        for stage_name, stage_data in stages.items():
            if stage_data.get('success'):
                stage_score = 1.0
                
                # Adjust score based on stage-specific metrics
                if stage_name == 'ocr_processing':
                    confidence = stage_data.get('confidence', 0)
                    if confidence < self.min_ocr_confidence:
                        stage_score *= 0.7
                        quality['issues'].append(f"Low OCR confidence: {confidence}%")
                
                elif stage_name == 'ui_detection':
                    element_count = stage_data.get('element_count', 0)
                    if element_count == 0:
                        stage_score *= 0.5
                        quality['issues'].append("No UI elements detected")
                
                # Time penalty for slow stages
                stage_time = stage_data.get('time', 0)
                if stage_time > 5.0:
                    stage_score *= 0.9
                    quality['issues'].append(f"Slow {stage_name}: {stage_time:.1f}s")
                
                quality['stage_scores'][stage_name] = stage_score
                total_score += stage_score
                stage_count += 1
            else:
                quality['stage_scores'][stage_name] = 0.0
                quality['issues'].append(f"Stage {stage_name} failed")
        
        # Calculate overall score
        if stage_count > 0:
            quality['overall_score'] = total_score / stage_count
        
        # Add recommendations
        if quality['overall_score'] < 0.8:
            quality['recommendations'].append("Consider improving image quality")
        if len(quality['issues']) > 2:
            quality['recommendations'].append("Multiple issues detected - review pipeline settings")
        
        return quality
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get pipeline performance statistics"""
        avg_time = self.total_pipeline_time / self.pipeline_count if self.pipeline_count > 0 else 0
        success_rate = self.successful_pipelines / self.pipeline_count if self.pipeline_count > 0 else 0
        
        return {
            'total_pipelines': self.pipeline_count,
            'successful_pipelines': self.successful_pipelines,
            'success_rate': success_rate,
            'total_time': self.total_pipeline_time,
            'average_pipeline_time': avg_time,
            'last_pipeline_time': self.last_pipeline_time,
            'initialized': self.initialized
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current pipeline status"""
        return {
            'initialized': self.initialized,
            'components': {
                'screen_capture': self.screen_capture.initialized if self.screen_capture else False,
                'ocr_engine': self.ocr_engine.initialized if self.ocr_engine else False,
                'ui_detector': self.ui_detector.initialized if self.ui_detector else False
            },
            'capabilities': {
                'full_visual_analysis': True,
                'text_extraction': True,
                'ui_detection': True,
                'data_integration': True,
                'quality_assessment': True
            },
            'performance': self.get_performance_stats(),
            'settings': {
                'enable_preprocessing': self.enable_preprocessing,
                'enable_caching': self.enable_caching,
                'max_processing_time': self.max_processing_time,
                'min_overall_quality': self.min_overall_quality
            },
            'wake_up_orion_power': True  # WAKE UP ORION SPECIAL FLAG! 🌟
        }
    
    def shutdown(self):
        """Shutdown visual processing pipeline"""
        self.logger.info("🛑 Shutting down Visual Processing Pipeline")
        self.logger.info("🌟 WAKE UP ORION! Harika iş çıkardık!")
        
        if self.screen_capture:
            self.screen_capture.shutdown()
        if self.ocr_engine:
            self.ocr_engine.shutdown()
        if self.ui_detector:
            self.ui_detector.shutdown()
        
        self.initialized = False
        self.logger.info("✅ Visual Processing Pipeline shutdown complete")

# Global instance for easy access
visual_pipeline = VisualProcessingPipeline()

def get_visual_pipeline() -> VisualProcessingPipeline:
    """Get global visual pipeline instance"""
    return visual_pipeline
