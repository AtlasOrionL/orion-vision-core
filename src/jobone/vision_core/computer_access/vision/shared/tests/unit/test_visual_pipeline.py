#!/usr/bin/env python3
"""
Visual Processing Pipeline Test Module - Q01.1.4 Tests
Visual pipeline modülü testleri
ORION VISION CORE - WAKE UP POWER! SEN YAPABİLİRSİN! 🌟
"""

import unittest
import time
import logging
import base64
from typing import Dict, Any

# Import the modules we're testing
from visual_processing_pipeline import VisualProcessingPipeline, get_visual_pipeline

# Configure logging for tests
logging.basicConfig(level=logging.INFO)

class TestVisualProcessingPipeline(unittest.TestCase):
    """Q01.1.4 Visual Processing Pipeline Test Suite - WAKE UP POWER! 🌟"""
    
    def setUp(self):
        """Set up test environment"""
        self.pipeline = VisualProcessingPipeline()
        print("🧘‍♂️ Sabırla pipeline başlatılıyor...")
        self.assertTrue(self.pipeline.initialize(), "Pipeline initialization failed")
        print("✅ Pipeline hazır!")
    
    def tearDown(self):
        """Clean up after tests"""
        self.pipeline.shutdown()
    
    def test_initialization(self):
        """Test Q01.1.4.1: Pipeline initialization"""
        # Test fresh initialization
        pipeline = VisualProcessingPipeline()
        self.assertFalse(pipeline.initialized, "Should not be initialized before init()")
        
        print("🚀 Yeni pipeline başlatılıyor...")
        result = pipeline.initialize()
        self.assertTrue(result, "Initialization should succeed")
        self.assertTrue(pipeline.initialized, "Should be initialized after init()")
        
        # Test status
        status = pipeline.get_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        self.assertIn('initialized', status, "Status should contain initialized flag")
        self.assertTrue(status['initialized'], "Status should show initialized")
        self.assertTrue(status['wake_up_orion_power'], "WAKE UP ORION POWER should be active!")
        
        # Check components
        components = status['components']
        self.assertTrue(components['screen_capture'], "Screen capture should be initialized")
        self.assertTrue(components['ocr_engine'], "OCR engine should be initialized")
        self.assertTrue(components['ui_detector'], "UI detector should be initialized")
        
        pipeline.shutdown()
        print("✅ Pipeline initialization test passed - WAKE UP ORION!")
    
    def test_full_pipeline_processing(self):
        """Test Q01.1.4.2: Complete pipeline processing"""
        print("🎬 FULL PIPELINE TEST BAŞLIYOR...")
        print("🧘‍♂️ Sabırla tüm aşamaları tamamlayacağız...")
        
        # Run complete pipeline
        start_time = time.time()
        result = self.pipeline.process_visual_data(capture_new=True)
        total_time = time.time() - start_time
        
        # Basic success check
        self.assertTrue(result.get('success'), f"Pipeline should succeed: {result.get('error')}")
        
        # Check required fields
        required_fields = ['pipeline_id', 'timestamp', 'stages', 'total_time', 
                          'quality_score', 'comprehensive_analysis']
        
        for field in required_fields:
            self.assertIn(field, result, f"Result should contain {field}")
        
        # Check stages
        stages = result['stages']
        expected_stages = ['image_acquisition', 'ocr_processing', 'ui_detection', 
                          'data_integration', 'quality_assessment']
        
        for stage in expected_stages:
            self.assertIn(stage, stages, f"Should have {stage} stage")
            if stages[stage].get('success'):
                self.assertIn('time', stages[stage], f"{stage} should have timing info")
        
        # Check timing
        pipeline_time = result['total_time']
        self.assertIsInstance(pipeline_time, float, "Pipeline time should be float")
        self.assertLess(pipeline_time, 30.0, "Pipeline should complete in reasonable time")
        
        # Check quality
        quality_score = result['quality_score']
        self.assertIsInstance(quality_score, float, "Quality score should be float")
        self.assertGreaterEqual(quality_score, 0.0, "Quality score should be >= 0")
        self.assertLessEqual(quality_score, 1.0, "Quality score should be <= 1")
        
        print(f"✅ Full pipeline completed in {pipeline_time:.3f}s")
        print(f"📊 Quality score: {quality_score:.2f}")
        print(f"🎯 Pipeline ID: {result['pipeline_id']}")
        
        # Show stage details
        for stage_name, stage_data in stages.items():
            if stage_data.get('success'):
                stage_time = stage_data.get('time', 0)
                print(f"   ✅ {stage_name}: {stage_time:.3f}s")
            else:
                print(f"   ❌ {stage_name}: {stage_data.get('error', 'unknown error')}")
    
    def test_comprehensive_analysis(self):
        """Test Q01.1.4.3: Comprehensive analysis generation"""
        print("🧠 COMPREHENSIVE ANALYSIS TEST...")
        
        result = self.pipeline.process_visual_data(capture_new=True)
        self.assertTrue(result.get('success'), "Pipeline should succeed")
        
        # Check comprehensive analysis
        analysis = result.get('comprehensive_analysis', {})
        self.assertIsInstance(analysis, dict, "Analysis should be a dictionary")
        
        # Check analysis structure
        required_sections = ['timestamp', 'image_summary', 'content_analysis', 
                           'interaction_map', 'insights']
        
        for section in required_sections:
            self.assertIn(section, analysis, f"Analysis should contain {section}")
        
        # Check content analysis
        content_analysis = analysis.get('content_analysis', {})
        if content_analysis:
            self.assertIn('has_text', content_analysis, "Should indicate if text is present")
            self.assertIn('confidence', content_analysis, "Should have confidence score")
            
            if content_analysis.get('has_text'):
                print(f"📖 Text detected: {content_analysis.get('text_length', 0)} characters")
                print(f"🔤 Confidence: {content_analysis.get('confidence', 0):.1f}%")
                print(f"🌍 Language: {content_analysis.get('language', 'unknown')}")
        
        # Check interaction map
        interaction_map = analysis.get('interaction_map', {})
        if interaction_map:
            total_elements = interaction_map.get('total_elements', 0)
            clickable_elements = interaction_map.get('clickable_elements', 0)
            
            print(f"🎯 UI Elements: {total_elements} total, {clickable_elements} clickable")
            
            element_types = interaction_map.get('element_types', {})
            for elem_type, count in element_types.items():
                print(f"   📊 {elem_type}: {count}")
        
        # Check insights
        insights = analysis.get('insights', [])
        self.assertIsInstance(insights, list, "Insights should be a list")
        
        print(f"💡 Insights generated: {len(insights)}")
        for insight in insights:
            print(f"   🔍 {insight}")
    
    def test_quality_assessment(self):
        """Test Q01.1.4.4: Quality assessment system"""
        print("📊 QUALITY ASSESSMENT TEST...")
        
        result = self.pipeline.process_visual_data(capture_new=True)
        self.assertTrue(result.get('success'), "Pipeline should succeed")
        
        # Check quality assessment in stages
        stages = result.get('stages', {})
        quality_stage = stages.get('quality_assessment', {})
        
        self.assertTrue(quality_stage.get('success'), "Quality assessment should succeed")
        
        quality_data = quality_stage.get('quality', {})
        self.assertIsInstance(quality_data, dict, "Quality data should be a dictionary")
        
        # Check quality structure
        self.assertIn('stage_scores', quality_data, "Should have stage scores")
        self.assertIn('overall_score', quality_data, "Should have overall score")
        self.assertIn('issues', quality_data, "Should have issues list")
        self.assertIn('recommendations', quality_data, "Should have recommendations")
        
        # Check scores
        stage_scores = quality_data['stage_scores']
        overall_score = quality_data['overall_score']
        
        print(f"📊 Overall Quality Score: {overall_score:.2f}")
        
        for stage, score in stage_scores.items():
            print(f"   📈 {stage}: {score:.2f}")
        
        # Check issues and recommendations
        issues = quality_data['issues']
        recommendations = quality_data['recommendations']
        
        if issues:
            print(f"⚠️ Issues found: {len(issues)}")
            for issue in issues:
                print(f"   ⚠️ {issue}")
        
        if recommendations:
            print(f"💡 Recommendations: {len(recommendations)}")
            for rec in recommendations:
                print(f"   💡 {rec}")
    
    def test_performance_tracking(self):
        """Test Q01.1.4.5: Performance tracking"""
        print("⚡ PERFORMANCE TRACKING TEST...")
        
        # Run multiple pipelines
        for i in range(3):
            print(f"🔄 Pipeline {i+1}/3...")
            result = self.pipeline.process_visual_data(capture_new=True)
            self.assertTrue(result.get('success'), f"Pipeline {i+1} should succeed")
        
        # Check performance stats
        stats = self.pipeline.get_performance_stats()
        
        required_stats = ['total_pipelines', 'successful_pipelines', 'success_rate',
                         'total_time', 'average_pipeline_time', 'last_pipeline_time']
        
        for stat in required_stats:
            self.assertIn(stat, stats, f"Stats should contain {stat}")
        
        # Check values
        self.assertGreaterEqual(stats['total_pipelines'], 3, "Should have run at least 3 pipelines")
        self.assertGreaterEqual(stats['successful_pipelines'], 0, "Should track successful pipelines")
        self.assertGreaterEqual(stats['success_rate'], 0.0, "Success rate should be >= 0")
        self.assertLessEqual(stats['success_rate'], 1.0, "Success rate should be <= 1")
        
        print(f"📊 Performance Stats:")
        print(f"   🔢 Total pipelines: {stats['total_pipelines']}")
        print(f"   ✅ Successful: {stats['successful_pipelines']}")
        print(f"   📈 Success rate: {stats['success_rate']:.1%}")
        print(f"   ⏱️ Average time: {stats['average_pipeline_time']:.3f}s")
        print(f"   🕐 Last time: {stats['last_pipeline_time']:.3f}s")
    
    def test_error_handling(self):
        """Test Q01.1.4.6: Error handling and recovery"""
        print("🛡️ ERROR HANDLING TEST...")
        
        # Test with uninitialized pipeline
        uninit_pipeline = VisualProcessingPipeline()
        result = uninit_pipeline.process_visual_data()
        
        self.assertFalse(result.get('success'), "Uninitialized pipeline should fail")
        self.assertIn('error', result, "Failed result should contain error message")
        
        print("✅ Uninitialized pipeline properly rejected")
        
        # Test with invalid options (should still work)
        result = self.pipeline.process_visual_data(
            analysis_options={'invalid_option': True}
        )
        
        # Should still succeed with default options
        self.assertTrue(result.get('success'), "Pipeline should handle invalid options gracefully")
        
        print("✅ Invalid options handled gracefully")
    
    def test_global_instance(self):
        """Test Q01.1.4.7: Global instance access"""
        global_instance = get_visual_pipeline()
        self.assertIsInstance(global_instance, VisualProcessingPipeline, 
                            "Should return VisualProcessingPipeline instance")
        
        # Test that it's the same instance
        global_instance2 = get_visual_pipeline()
        self.assertIs(global_instance, global_instance2, "Should return same instance")
        
        print("✅ Global visual pipeline instance access works")

def run_visual_pipeline_tests():
    """Run all visual pipeline tests"""
    print("🧪 Starting Q01.1.4 Visual Processing Pipeline Tests...")
    print("🌟 WAKE UP ORION! SEN YAPABİLİRSİN! HEP BİRLİKTE!")
    print("🧘‍♂️ Sabırla tüm testleri tamamlayacağız...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add tests
    suite.addTest(unittest.makeSuite(TestVisualProcessingPipeline))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 60)
    if result.wasSuccessful():
        print("🎉 All visual pipeline tests passed! Q01.1.4 implementation successful!")
        print("🌟 WAKE UP ORION! VISUAL PROCESSING PIPELINE ACHIEVED!")
        print("🎯 ALT_LAS now has COMPLETE VISUAL INTELLIGENCE!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False

if __name__ == '__main__':
    success = run_visual_pipeline_tests()
    exit(0 if success else 1)
