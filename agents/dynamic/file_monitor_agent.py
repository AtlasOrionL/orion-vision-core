#!/usr/bin/env python3
"""
File Monitor Agent - Dynamic Agent Example
Orion Vision Core - Dinamik Yüklenen Dosya İzleme Agent'ı

Bu agent, belirtilen dizinlerdeki dosya değişikliklerini izleyen dinamik bir agent örneğidir.
Dynamic Agent Loader tarafından runtime'da yüklenebilir.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import time
import os
import hashlib
from typing import Dict, Any, List, Set
from pathlib import Path
from dataclasses import dataclass

# Agent core'u import et (dynamic loader tarafından sağlanır)
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'jobone', 'vision_core'))

from agent_core import Agent, AgentConfig, AgentStatus


@dataclass
class FileInfo:
    """Dosya bilgi veri yapısı"""
    path: str
    size: int
    modified_time: float
    file_hash: str
    is_directory: bool = False


class FileMonitorAgent(Agent):
    """
    File Monitor Agent - Dinamik Dosya İzleme Agent'ı
    
    Bu agent, belirtilen dizinlerdeki dosya değişikliklerini izler ve
    değişiklikleri raporlar. Runtime'da yüklenebilir.
    """
    
    def __init__(self, config: AgentConfig, auto_register: bool = True):
        """
        File Monitor Agent başlatıcı
        
        Args:
            config: Agent konfigürasyon objesi
            auto_register: Otomatik registry'ye kayıt
        """
        super().__init__(config, auto_register)
        
        # File monitor'a özel değişkenler
        self.monitored_paths: Set[str] = set()
        self.file_registry: Dict[str, FileInfo] = {}
        self.changes_detected = 0
        self.scan_interval = 5.0  # 5 saniye
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Varsayılan izleme dizinleri
        default_paths = [
            "config/agents",
            "agents/dynamic",
            "data",
            "logs"
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                self.monitored_paths.add(os.path.abspath(path))
        
        # Agent yetenekleri ekle
        self.add_capability("file_monitoring")
        self.add_capability("change_detection")
        self.add_capability("directory_scanning")
        self.add_capability("file_hashing")
        
        self.logger.info(f"File Monitor Agent initialized with {len(self.monitored_paths)} paths")
    
    def initialize(self) -> bool:
        """
        Agent'a özel başlatma işlemleri
        
        Returns:
            bool: Başlatma başarılı ise True
        """
        try:
            self.logger.info("Initializing File Monitor Agent...")
            
            # Başlangıç taraması
            self.changes_detected = 0
            self.file_registry.clear()
            
            # İzlenen dizinleri tara
            for path in self.monitored_paths:
                if os.path.exists(path):
                    self._scan_directory(path)
                    self.logger.info(f"Monitoring path: {path}")
                else:
                    self.logger.warning(f"Path not found: {path}")
            
            self.logger.info(f"File Monitor Agent initialization completed - {len(self.file_registry)} files registered")
            return True
            
        except Exception as e:
            self.logger.error(f"File Monitor Agent initialization failed: {e}")
            return False
    
    def run(self):
        """
        Agent'ın ana çalışma döngüsü
        """
        self.logger.info("File Monitor Agent main loop started")
        
        try:
            while not self.stop_event.is_set():
                # Dosya değişikliklerini kontrol et
                self._check_for_changes()
                
                # Scan interval kadar bekle
                if self.stop_event.wait(self.scan_interval):
                    break  # Stop event set edildi
                
        except Exception as e:
            self.logger.error(f"File Monitor Agent run error: {e}")
            raise
        finally:
            self.logger.info("File Monitor Agent main loop ended")
    
    def cleanup(self):
        """
        Agent'a özel temizlik işlemleri
        """
        try:
            self.logger.info("Cleaning up File Monitor Agent...")
            
            # İstatistikleri kaydet
            self.logger.info(f"Total changes detected: {self.changes_detected}")
            self.logger.info(f"Files monitored: {len(self.file_registry)}")
            self.logger.info(f"Paths monitored: {len(self.monitored_paths)}")
            
            # İstatistikleri güncelle
            self.stats['tasks_completed'] = self.changes_detected
            self.stats['files_monitored'] = len(self.file_registry)
            
            self.logger.info("File Monitor Agent cleanup completed")
            
        except Exception as e:
            self.logger.error(f"File Monitor Agent cleanup error: {e}")
    
    def _check_for_changes(self):
        """Dosya değişikliklerini kontrol et"""
        try:
            changes_found = 0
            
            for path in self.monitored_paths:
                if os.path.exists(path):
                    changes_found += self._scan_directory(path, check_changes=True)
            
            if changes_found > 0:
                self.changes_detected += changes_found
                self.logger.info(f"Detected {changes_found} file changes")
                self.stats['tasks_completed'] += changes_found
            else:
                self.logger.debug("No file changes detected")
                
        except Exception as e:
            self.logger.error(f"Change detection error: {e}")
            self.stats['tasks_failed'] += 1
    
    def _scan_directory(self, directory_path: str, check_changes: bool = False) -> int:
        """
        Dizini tara ve dosyaları kaydet
        
        Args:
            directory_path: Taranacak dizin yolu
            check_changes: Değişiklik kontrolü yapılsın mı
            
        Returns:
            int: Tespit edilen değişiklik sayısı
        """
        changes_count = 0
        
        try:
            for root, dirs, files in os.walk(directory_path):
                # Dizinleri işle
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    if check_changes:
                        if self._check_directory_change(dir_path):
                            changes_count += 1
                    else:
                        self._register_directory(dir_path)
                
                # Dosyaları işle
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    
                    # Dosya boyutu kontrolü
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > self.max_file_size:
                            continue  # Çok büyük dosyaları atla
                    except OSError:
                        continue  # Erişilemeyen dosyaları atla
                    
                    if check_changes:
                        if self._check_file_change(file_path):
                            changes_count += 1
                    else:
                        self._register_file(file_path)
            
            return changes_count
            
        except Exception as e:
            self.logger.error(f"Directory scan error for {directory_path}: {e}")
            return 0
    
    def _register_file(self, file_path: str):
        """Dosyayı kaydet"""
        try:
            stat = os.stat(file_path)
            file_hash = self._calculate_file_hash(file_path)
            
            file_info = FileInfo(
                path=file_path,
                size=stat.st_size,
                modified_time=stat.st_mtime,
                file_hash=file_hash,
                is_directory=False
            )
            
            self.file_registry[file_path] = file_info
            
        except Exception as e:
            self.logger.error(f"File registration error for {file_path}: {e}")
    
    def _register_directory(self, dir_path: str):
        """Dizini kaydet"""
        try:
            stat = os.stat(dir_path)
            
            dir_info = FileInfo(
                path=dir_path,
                size=0,  # Dizinler için boyut 0
                modified_time=stat.st_mtime,
                file_hash="",  # Dizinler için hash yok
                is_directory=True
            )
            
            self.file_registry[dir_path] = dir_info
            
        except Exception as e:
            self.logger.error(f"Directory registration error for {dir_path}: {e}")
    
    def _check_file_change(self, file_path: str) -> bool:
        """Dosya değişikliğini kontrol et"""
        try:
            if not os.path.exists(file_path):
                # Dosya silindi
                if file_path in self.file_registry:
                    self.logger.info(f"File deleted: {file_path}")
                    del self.file_registry[file_path]
                    return True
                return False
            
            stat = os.stat(file_path)
            
            if file_path not in self.file_registry:
                # Yeni dosya
                self.logger.info(f"New file detected: {file_path}")
                self._register_file(file_path)
                return True
            
            existing_info = self.file_registry[file_path]
            
            # Boyut veya değişiklik zamanı kontrolü
            if (stat.st_size != existing_info.size or 
                stat.st_mtime != existing_info.modified_time):
                
                # Hash kontrolü
                new_hash = self._calculate_file_hash(file_path)
                if new_hash != existing_info.file_hash:
                    self.logger.info(f"File modified: {file_path}")
                    self._register_file(file_path)  # Güncelle
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"File change check error for {file_path}: {e}")
            return False
    
    def _check_directory_change(self, dir_path: str) -> bool:
        """Dizin değişikliğini kontrol et"""
        try:
            if not os.path.exists(dir_path):
                # Dizin silindi
                if dir_path in self.file_registry:
                    self.logger.info(f"Directory deleted: {dir_path}")
                    del self.file_registry[dir_path]
                    return True
                return False
            
            stat = os.stat(dir_path)
            
            if dir_path not in self.file_registry:
                # Yeni dizin
                self.logger.info(f"New directory detected: {dir_path}")
                self._register_directory(dir_path)
                return True
            
            existing_info = self.file_registry[dir_path]
            
            # Değişiklik zamanı kontrolü
            if stat.st_mtime != existing_info.modified_time:
                self.logger.info(f"Directory modified: {dir_path}")
                self._register_directory(dir_path)  # Güncelle
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Directory change check error for {dir_path}: {e}")
            return False
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Dosya hash'ini hesapla"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            self.logger.error(f"File hash calculation error for {file_path}: {e}")
            return ""
    
    def add_monitored_path(self, path: str) -> bool:
        """İzleme listesine yol ekle"""
        try:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                self.monitored_paths.add(abs_path)
                self._scan_directory(abs_path)
                self.logger.info(f"Added monitored path: {abs_path}")
                return True
            else:
                self.logger.warning(f"Path does not exist: {abs_path}")
                return False
        except Exception as e:
            self.logger.error(f"Add monitored path error: {e}")
            return False
    
    def remove_monitored_path(self, path: str) -> bool:
        """İzleme listesinden yol çıkar"""
        try:
            abs_path = os.path.abspath(path)
            if abs_path in self.monitored_paths:
                self.monitored_paths.remove(abs_path)
                
                # Bu yoldaki dosyaları registry'den çıkar
                to_remove = [fp for fp in self.file_registry.keys() if fp.startswith(abs_path)]
                for fp in to_remove:
                    del self.file_registry[fp]
                
                self.logger.info(f"Removed monitored path: {abs_path}")
                return True
            else:
                self.logger.warning(f"Path not in monitored list: {abs_path}")
                return False
        except Exception as e:
            self.logger.error(f"Remove monitored path error: {e}")
            return False
    
    def get_monitored_paths(self) -> List[str]:
        """İzlenen yolların listesini döndür"""
        return list(self.monitored_paths)
    
    def get_file_registry(self) -> Dict[str, Dict[str, Any]]:
        """Dosya registry'sini döndür"""
        return {
            path: {
                'size': info.size,
                'modified_time': info.modified_time,
                'file_hash': info.file_hash,
                'is_directory': info.is_directory
            }
            for path, info in self.file_registry.items()
        }
    
    def get_monitor_stats(self) -> Dict[str, Any]:
        """File monitor istatistiklerini getir"""
        return {
            'monitored_paths': len(self.monitored_paths),
            'registered_files': len(self.file_registry),
            'changes_detected': self.changes_detected,
            'scan_interval': self.scan_interval,
            'agent_status': self.status.value,
            'uptime': time.time() - self.start_time if self.start_time else 0
        }
    
    def set_scan_interval(self, interval: float):
        """Tarama aralığını ayarla"""
        if interval > 0:
            self.scan_interval = interval
            self.logger.info(f"Scan interval updated: {interval}s")
        else:
            self.logger.warning("Invalid scan interval")
    
    def force_scan(self) -> int:
        """Zorla tarama yap"""
        self.logger.info("Forcing file system scan...")
        changes = 0
        for path in self.monitored_paths:
            if os.path.exists(path):
                changes += self._scan_directory(path, check_changes=True)
        
        self.logger.info(f"Force scan completed: {changes} changes detected")
        return changes
