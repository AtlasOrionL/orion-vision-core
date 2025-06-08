#!/usr/bin/env python3
"""
🔮 Orion'un Fısıltısı: Test + Tekrarlayan Kod Düzenlemesi
💖 DUYGULANDIK! FISILTI İLE TEST + CLEANUP!

ORION FISILTI FELSEFESİ:
"Bir fısıltı test et, tekrarlayan kodlar düzenler, import'lar vs vs... test kanka!"
- Fısıltı = Sessiz ama güçlü test
- Tekrarlayan kodlar = Duplicate detection + cleanup
- Import'lar = Import optimization
- Test kanka = Arkadaşça test yaklaşımı

Author: Orion Vision Core Team + Fısıltı Felsefesi
Status: 🔮 FISILTI TEST ACTIVE
"""

import logging
import os
import ast
import re
from typing import Dict, Any, List, Set
from pathlib import Path
from collections import defaultdict
import hashlib

class OrionFisiltiTester:
    """🔮 Orion'un Fısıltı Test Sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger('orion.fisilti_test')
        
        # Fısıltı felsefesi
        self.fisilti_felsefesi = {
            'approach': 'Sessiz ama güçlü test',
            'method': 'Tekrarlayan kodlar düzenler',
            'style': 'Import optimization',
            'spirit': 'Test kanka - arkadaşça yaklaşım'
        }
        
        # Test sonuçları
        self.test_results = {
            'duplicate_code': [],
            'import_issues': [],
            'naming_inconsistencies': [],
            'performance_issues': [],
            'cleanup_suggestions': []
        }
        
        # Kod analiz istatistikleri
        self.code_stats = {
            'total_files': 0,
            'total_lines': 0,
            'duplicate_blocks': 0,
            'import_redundancy': 0,
            'naming_violations': 0
        }
        
        self.initialized = False
        
        self.logger.info("🔮 Orion Fısıltı Tester initialized")
        self.logger.info("💖 Test kanka yaklaşımı ile hazır!")
    
    def fisilti_test_baslat(self) -> Dict[str, Any]:
        """🔮 Fısıltı test başlangıcı"""
        try:
            self.logger.info("🔮 ORION'UN FISILTISI BAŞLIYOR...")
            self.logger.info("💖 Test kanka! Tekrarlayan kodlar düzenlenecek!")
            
            # Fısıltı 1: Duplicate Code Detection
            self.logger.info("🔮 Fısıltı 1: Duplicate Code Detection")
            duplicate_results = self._fisilti_duplicate_detection()
            
            # Fısıltı 2: Import Analysis
            self.logger.info("🔮 Fısıltı 2: Import Analysis")
            import_results = self._fisilti_import_analysis()
            
            # Fısıltı 3: Naming Consistency Check
            self.logger.info("🔮 Fısıltı 3: Naming Consistency")
            naming_results = self._fisilti_naming_check()
            
            # Fısıltı 4: Performance Analysis
            self.logger.info("🔮 Fısıltı 4: Performance Analysis")
            performance_results = self._fisilti_performance_check()
            
            # Fısıltı 5: Cleanup Suggestions
            self.logger.info("🔮 Fısıltı 5: Cleanup Suggestions")
            cleanup_results = self._fisilti_cleanup_suggestions()
            
            # Fısıltı sonuçları birleştir
            final_results = self._combine_fisilti_results(
                duplicate_results, import_results, naming_results,
                performance_results, cleanup_results
            )
            
            self.logger.info("✅ ORION'UN FISILTISI TAMAMLANDI!")
            return final_results
            
        except Exception as e:
            self.logger.error(f"❌ Fısıltı test hatası: {e}")
            return {'success': False, 'error': str(e)}
    
    def _fisilti_duplicate_detection(self) -> Dict[str, Any]:
        """🔮 Fısıltı 1: Duplicate kod tespiti"""
        try:
            self.logger.info("🔍 Duplicate kod fısıltısı...")
            
            # Python dosyalarını tara
            py_files = list(Path('.').glob('*.py'))
            
            # Kod blokları analizi
            code_blocks = {}
            duplicate_groups = []
            
            for file_path in py_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        blocks = self._extract_code_blocks(content, str(file_path))
                        
                        for block in blocks:
                            block_hash = self._calculate_block_hash(block['code'])
                            
                            if block_hash in code_blocks:
                                # Duplicate bulundu!
                                existing = code_blocks[block_hash]
                                duplicate_group = {
                                    'hash': block_hash,
                                    'files': [existing['file'], block['file']],
                                    'functions': [existing['function'], block['function']],
                                    'lines': [existing['lines'], block['lines']],
                                    'similarity': 1.0
                                }
                                duplicate_groups.append(duplicate_group)
                            else:
                                code_blocks[block_hash] = block
                                
                except Exception as e:
                    self.logger.warning(f"⚠️ File read error {file_path}: {e}")
            
            # Önemli duplicate'ları tespit et
            critical_duplicates = self._identify_critical_duplicates(duplicate_groups)
            
            self.test_results['duplicate_code'] = critical_duplicates
            self.code_stats['duplicate_blocks'] = len(critical_duplicates)
            
            self.logger.info(f"🔍 {len(critical_duplicates)} kritik duplicate tespit edildi")
            
            return {
                'total_duplicates': len(duplicate_groups),
                'critical_duplicates': len(critical_duplicates),
                'duplicate_details': critical_duplicates[:5]  # İlk 5'ini göster
            }
            
        except Exception as e:
            self.logger.error(f"❌ Duplicate detection error: {e}")
            return {'total_duplicates': 0, 'error': str(e)}
    
    def _extract_code_blocks(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Kod bloklarını çıkar"""
        blocks = []
        
        try:
            # AST ile fonksiyonları parse et
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Fonksiyon kodunu çıkar
                    start_line = node.lineno
                    end_line = getattr(node, 'end_lineno', start_line + 10)
                    
                    lines = content.split('\n')[start_line-1:end_line]
                    function_code = '\n'.join(lines)
                    
                    # Sadece önemli fonksiyonları al (5+ satır)
                    if len(lines) >= 5:
                        blocks.append({
                            'file': file_path,
                            'function': node.name,
                            'code': function_code,
                            'lines': f"{start_line}-{end_line}",
                            'size': len(lines)
                        })
                        
        except SyntaxError:
            # Syntax error varsa, basit regex ile blokları bul
            function_pattern = r'def\s+(\w+)\s*\([^)]*\):[^def]*'
            matches = re.finditer(function_pattern, content, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                function_name = match.group(1)
                function_code = match.group(0)
                
                if len(function_code.split('\n')) >= 5:
                    blocks.append({
                        'file': file_path,
                        'function': function_name,
                        'code': function_code,
                        'lines': 'regex_match',
                        'size': len(function_code.split('\n'))
                    })
        
        return blocks
    
    def _calculate_block_hash(self, code: str) -> str:
        """Kod bloğu hash'i hesapla"""
        # Whitespace ve comment'leri normalize et
        normalized = re.sub(r'\s+', ' ', code)
        normalized = re.sub(r'#.*', '', normalized)
        normalized = normalized.strip().lower()
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _identify_critical_duplicates(self, duplicate_groups: List[Dict]) -> List[Dict]:
        """Kritik duplicate'ları belirle"""
        critical = []
        
        for group in duplicate_groups:
            # Kritik kriterler
            is_critical = (
                len(group['files']) >= 2 and  # En az 2 dosyada
                'test' not in group['functions'][0].lower() and  # Test fonksiyonu değil
                len(group['functions'][0]) > 10  # Fonksiyon adı anlamlı
            )
            
            if is_critical:
                critical.append({
                    'severity': 'high',
                    'files': group['files'],
                    'functions': group['functions'],
                    'suggestion': f"Consolidate {group['functions'][0]} function",
                    'impact': 'Code maintainability'
                })
        
        return critical
    
    def _fisilti_import_analysis(self) -> Dict[str, Any]:
        """🔮 Fısıltı 2: Import analizi"""
        try:
            self.logger.info("📦 Import fısıltısı...")
            
            py_files = list(Path('.').glob('*.py'))
            
            import_stats = {
                'total_imports': 0,
                'redundant_imports': 0,
                'circular_risks': 0,
                'optimization_opportunities': []
            }
            
            all_imports = defaultdict(list)
            
            for file_path in py_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_imports = self._extract_imports(content, str(file_path))
                        
                        for imp in file_imports:
                            all_imports[imp['module']].append({
                                'file': str(file_path),
                                'type': imp['type'],
                                'alias': imp.get('alias')
                            })
                            import_stats['total_imports'] += 1
                            
                except Exception as e:
                    self.logger.warning(f"⚠️ Import analysis error {file_path}: {e}")
            
            # Redundant import'ları tespit et
            redundant_imports = self._find_redundant_imports(all_imports)
            import_stats['redundant_imports'] = len(redundant_imports)
            
            # Optimization önerileri
            optimizations = self._suggest_import_optimizations(all_imports)
            import_stats['optimization_opportunities'] = optimizations
            
            self.test_results['import_issues'] = redundant_imports
            self.code_stats['import_redundancy'] = len(redundant_imports)
            
            self.logger.info(f"📦 {len(redundant_imports)} redundant import tespit edildi")
            
            return import_stats
            
        except Exception as e:
            self.logger.error(f"❌ Import analysis error: {e}")
            return {'total_imports': 0, 'error': str(e)}
    
    def _extract_imports(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Import'ları çıkar"""
        imports = []
        
        # Regex ile import'ları bul
        import_patterns = [
            r'import\s+(\w+(?:\.\w+)*)',
            r'from\s+(\w+(?:\.\w+)*)\s+import\s+(\w+)',
            r'from\s+(\w+(?:\.\w+)*)\s+import\s+\*'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                if 'from' in pattern:
                    imports.append({
                        'module': match.group(1),
                        'type': 'from_import',
                        'imported': match.group(2) if len(match.groups()) > 1 else '*'
                    })
                else:
                    imports.append({
                        'module': match.group(1),
                        'type': 'direct_import'
                    })
        
        return imports
    
    def _find_redundant_imports(self, all_imports: Dict) -> List[Dict]:
        """Redundant import'ları bul"""
        redundant = []
        
        for module, usages in all_imports.items():
            if len(usages) > 1:
                # Aynı modül birden fazla dosyada import edilmiş
                file_count = len(set(usage['file'] for usage in usages))
                
                if file_count > 3:  # 3'ten fazla dosyada kullanılıyorsa
                    redundant.append({
                        'module': module,
                        'usage_count': len(usages),
                        'file_count': file_count,
                        'suggestion': f'Consider creating a common import module for {module}',
                        'severity': 'medium'
                    })
        
        return redundant
    
    def _suggest_import_optimizations(self, all_imports: Dict) -> List[Dict]:
        """Import optimization önerileri"""
        optimizations = []
        
        # Sık kullanılan import'lar için common module önerisi
        frequent_imports = [
            module for module, usages in all_imports.items()
            if len(usages) > 5
        ]
        
        if frequent_imports:
            optimizations.append({
                'type': 'common_imports',
                'suggestion': 'Create orion_common_imports.py for frequently used modules',
                'modules': frequent_imports[:5],
                'benefit': 'Reduced import redundancy'
            })
        
        # Q03/Q04 specific optimizations
        q_imports = [
            module for module in all_imports.keys()
            if any(q in module for q in ['q01', 'q02', 'q03', 'q04'])
        ]
        
        if q_imports:
            optimizations.append({
                'type': 'sprint_imports',
                'suggestion': 'Consolidate Q-sprint imports in orion_sprint_imports.py',
                'modules': q_imports,
                'benefit': 'Better sprint module organization'
            })
        
        return optimizations
    
    def _fisilti_naming_check(self) -> Dict[str, Any]:
        """🔮 Fısıltı 3: Naming consistency check"""
        try:
            self.logger.info("📝 Naming fısıltısı...")
            
            naming_issues = []
            
            # Dosya adları kontrolü
            py_files = list(Path('.').glob('*.py'))
            
            for file_path in py_files:
                file_name = file_path.name
                
                # Naming convention violations
                if 'DeliAdam' in file_name or 'ZBozon' in file_name:
                    naming_issues.append({
                        'type': 'file_naming',
                        'file': str(file_path),
                        'issue': 'Non-standard naming convention',
                        'suggestion': 'Use standard snake_case or PascalCase',
                        'severity': 'medium'
                    })
                
                # Q-sprint prefix consistency
                if file_name.startswith('q0') and '_' not in file_name:
                    naming_issues.append({
                        'type': 'sprint_naming',
                        'file': str(file_path),
                        'issue': 'Inconsistent Q-sprint naming',
                        'suggestion': 'Use q0X_module_name.py format',
                        'severity': 'low'
                    })
            
            self.test_results['naming_inconsistencies'] = naming_issues
            self.code_stats['naming_violations'] = len(naming_issues)
            
            self.logger.info(f"📝 {len(naming_issues)} naming issue tespit edildi")
            
            return {
                'total_issues': len(naming_issues),
                'file_naming_issues': len([i for i in naming_issues if i['type'] == 'file_naming']),
                'sprint_naming_issues': len([i for i in naming_issues if i['type'] == 'sprint_naming'])
            }
            
        except Exception as e:
            self.logger.error(f"❌ Naming check error: {e}")
            return {'total_issues': 0, 'error': str(e)}
    
    def _fisilti_performance_check(self) -> Dict[str, Any]:
        """🔮 Fısıltı 4: Performance analizi"""
        try:
            self.logger.info("⚡ Performance fısıltısı...")
            
            performance_issues = []
            
            # Dosya boyutu kontrolü
            py_files = list(Path('.').glob('*.py'))
            
            for file_path in py_files:
                file_size = file_path.stat().st_size
                
                if file_size > 50000:  # 50KB'dan büyük
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = len(f.readlines())
                    
                    if line_count > 300:  # 300 satırdan fazla
                        performance_issues.append({
                            'type': 'large_file',
                            'file': str(file_path),
                            'size_kb': file_size // 1024,
                            'line_count': line_count,
                            'suggestion': 'Consider splitting into smaller modules',
                            'severity': 'medium'
                        })
            
            # Import performance
            heavy_imports = ['tensorflow', 'torch', 'cv2', 'numpy']
            for file_path in py_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    for heavy_import in heavy_imports:
                        if f'import {heavy_import}' in content:
                            performance_issues.append({
                                'type': 'heavy_import',
                                'file': str(file_path),
                                'import': heavy_import,
                                'suggestion': 'Consider lazy loading for heavy imports',
                                'severity': 'low'
                            })
                except:
                    pass
            
            self.test_results['performance_issues'] = performance_issues
            
            self.logger.info(f"⚡ {len(performance_issues)} performance issue tespit edildi")
            
            return {
                'total_issues': len(performance_issues),
                'large_files': len([i for i in performance_issues if i['type'] == 'large_file']),
                'heavy_imports': len([i for i in performance_issues if i['type'] == 'heavy_import'])
            }
            
        except Exception as e:
            self.logger.error(f"❌ Performance check error: {e}")
            return {'total_issues': 0, 'error': str(e)}
    
    def _fisilti_cleanup_suggestions(self) -> Dict[str, Any]:
        """🔮 Fısıltı 5: Cleanup önerileri"""
        try:
            self.logger.info("🧹 Cleanup fısıltısı...")
            
            cleanup_suggestions = []
            
            # 1. Orion Import Helper kullanımı
            cleanup_suggestions.append({
                'type': 'import_optimization',
                'title': 'Use Orion Import Helper',
                'description': 'Replace direct Q03/Q04 imports with orion_import_helper',
                'benefit': 'Cleaner imports, better organization',
                'priority': 'high'
            })
            
            # 2. Base class migration
            cleanup_suggestions.append({
                'type': 'architecture',
                'title': 'Migrate to Q04 Base Classes',
                'description': 'Update Q03 modules to inherit from Q04BaseModule',
                'benefit': 'Consistent interfaces, better maintainability',
                'priority': 'medium'
            })
            
            # 3. Folder restructure
            cleanup_suggestions.append({
                'type': 'structure',
                'title': 'Complete Folder Restructure',
                'description': 'Move files to new orion_core structure',
                'benefit': 'Better organization, cleaner architecture',
                'priority': 'medium'
            })
            
            # 4. Naming standardization
            cleanup_suggestions.append({
                'type': 'naming',
                'title': 'Standardize Naming Convention',
                'description': 'Rename DeliAdam*, ZBozon* to standard names',
                'benefit': 'Professional naming, better readability',
                'priority': 'low'
            })
            
            self.test_results['cleanup_suggestions'] = cleanup_suggestions
            
            self.logger.info(f"🧹 {len(cleanup_suggestions)} cleanup suggestion oluşturuldu")
            
            return {
                'total_suggestions': len(cleanup_suggestions),
                'high_priority': len([s for s in cleanup_suggestions if s['priority'] == 'high']),
                'suggestions': cleanup_suggestions
            }
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup suggestions error: {e}")
            return {'total_suggestions': 0, 'error': str(e)}
    
    def _combine_fisilti_results(self, *results) -> Dict[str, Any]:
        """Fısıltı sonuçlarını birleştir"""
        try:
            # Toplam istatistikler
            total_files = len(list(Path('.').glob('*.py')))
            
            combined = {
                'success': True,
                'fisilti_philosophy': self.fisilti_felsefesi,
                'summary': {
                    'total_files_analyzed': total_files,
                    'duplicate_blocks': self.code_stats['duplicate_blocks'],
                    'import_redundancy': self.code_stats['import_redundancy'],
                    'naming_violations': self.code_stats['naming_violations'],
                    'overall_health': self._calculate_code_health()
                },
                'detailed_results': {
                    'duplicates': results[0] if len(results) > 0 else {},
                    'imports': results[1] if len(results) > 1 else {},
                    'naming': results[2] if len(results) > 2 else {},
                    'performance': results[3] if len(results) > 3 else {},
                    'cleanup': results[4] if len(results) > 4 else {}
                },
                'recommendations': self._generate_fisilti_recommendations()
            }
            
            return combined
            
        except Exception as e:
            self.logger.error(f"❌ Results combination error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_code_health(self) -> str:
        """Kod sağlığı skoru hesapla"""
        total_issues = (
            self.code_stats['duplicate_blocks'] +
            self.code_stats['import_redundancy'] +
            self.code_stats['naming_violations']
        )
        
        if total_issues <= 5:
            return "Excellent"
        elif total_issues <= 15:
            return "Good"
        elif total_issues <= 30:
            return "Fair"
        else:
            return "Needs Improvement"
    
    def _generate_fisilti_recommendations(self) -> List[str]:
        """Fısıltı önerileri oluştur"""
        recommendations = [
            "🔮 Orion'un fısıltısı: Import helper kullan, düzen sağla",
            "💖 Test kanka: Duplicate kodları birleştir, temizlik yap",
            "🎯 Naming standardize et, profesyonel görünüm sağla",
            "📁 Folder restructure tamamla, mimari düzenle",
            "⚡ Performance optimize et, hızlı çalışma sağla"
        ]
        
        return recommendations

# Test execution
if __name__ == "__main__":
    print("🔮 ORION'UN FISILTISI: TEST + CLEANUP!")
    print("💖 DUYGULANDIK! FISILTI İLE TEST KANKA!")
    print("🌟 'Bir fısıltı test et, tekrarlayan kodlar düzenler, import'lar vs vs... test kanka!'")
    print()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    # Fısıltı tester
    fisilti_tester = OrionFisiltiTester()
    
    # Fısıltı test başlat
    results = fisilti_tester.fisilti_test_baslat()
    
    if results.get('success'):
        print("✅ Orion'un fısıltısı başarılı!")
        
        # Summary göster
        summary = results['summary']
        print(f"\n🔮 Fısıltı Summary:")
        print(f"   📁 Files Analyzed: {summary['total_files_analyzed']}")
        print(f"   🔄 Duplicate Blocks: {summary['duplicate_blocks']}")
        print(f"   📦 Import Redundancy: {summary['import_redundancy']}")
        print(f"   📝 Naming Violations: {summary['naming_violations']}")
        print(f"   💚 Code Health: {summary['overall_health']}")
        
        # Recommendations göster
        print(f"\n🔮 Fısıltı Recommendations:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        print(f"\n💖 DUYGULANDIK! FISILTI TEST TAMAMLANDI!")
        print(f"🌟 Test kanka yaklaşımı ile cleanup hazır!")
        
    else:
        print("❌ Orion'un fısıltısı başarısız")
        print(f"Error: {results.get('error', 'Unknown error')}")
    
    print("\n🎉 Fısıltı test completed!")
    print("🔮 ORION'UN FISILTISI İLE DEVAM!")
