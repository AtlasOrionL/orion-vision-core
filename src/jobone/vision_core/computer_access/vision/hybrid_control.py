#!/usr/bin/env python3
"""
🔄 Hibrit Yaklaşım Kontrol Paneli
💖 DUYGULANDIK! SEN YAPARSIN! HİBRİT GÜÇLE!

Bu modül Native ve Docker ortamları arasında köprü görevi görür.
Orion'un hibrit vizyonunu gerçekleştirir.

Author: Orion Vision Core Team
Status: 🔄 HYBRID CONTROL ACTIVE
"""

import os
import sys
import time
import subprocess
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

class EnvironmentType(Enum):
    """Environment types"""
    NATIVE = "native"
    DOCKER = "docker"
    HYBRID = "hybrid"

class OperationMode(Enum):
    """Operation modes"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

@dataclass
class HybridStatus:
    """Hybrid environment status"""
    native_active: bool
    docker_active: bool
    sync_status: str
    last_sync: Optional[datetime]
    active_mode: EnvironmentType
    operation_mode: OperationMode

class HybridController:
    """
    🔄 Hibrit Yaklaşım Kontrolcüsü
    
    Native ve Docker ortamları arasında seamless geçiş sağlar
    WAKE UP ORION! HİBRİT GÜÇLE!
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.hybrid.controller')
        
        # Paths
        self.base_path = os.getcwd()
        self.native_path = os.path.join(self.base_path, 'native')
        self.docker_path = os.path.join(self.base_path, 'docker')
        self.shared_path = os.path.join(self.base_path, 'shared')
        self.bridge_path = os.path.join(self.base_path, 'bridge')
        
        # Status
        self.current_env = EnvironmentType.NATIVE
        self.operation_mode = OperationMode.DEVELOPMENT
        
        # Orion'un hibrit mesajı
        self.orion_hybrid_code = "HybridPower2024"
        
        self.logger.info("🔄 Hibrit Controller initialized")
        self.logger.info("💖 DUYGULANDIK! HİBRİT GÜÇLE!")
    
    def get_environment_status(self) -> HybridStatus:
        """Get current hybrid environment status"""
        try:
            # Native status
            native_active = self._check_native_environment()
            
            # Docker status
            docker_active = self._check_docker_environment()
            
            # Sync status
            sync_status = self._check_sync_status()
            
            # Last sync time
            last_sync = self._get_last_sync_time()
            
            return HybridStatus(
                native_active=native_active,
                docker_active=docker_active,
                sync_status=sync_status,
                last_sync=last_sync,
                active_mode=self.current_env,
                operation_mode=self.operation_mode
            )
            
        except Exception as e:
            self.logger.error(f"❌ Status check error: {e}")
            return HybridStatus(
                native_active=False,
                docker_active=False,
                sync_status="error",
                last_sync=None,
                active_mode=self.current_env,
                operation_mode=self.operation_mode
            )
    
    def _check_native_environment(self) -> bool:
        """Check if native environment is active"""
        try:
            # Check virtual environment
            venv_path = os.path.join(self.native_path, 'venv')
            if not os.path.exists(venv_path):
                return False
            
            # Check if packages are installed
            activate_script = os.path.join(venv_path, 'bin', 'activate')
            if not os.path.exists(activate_script):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Native check error: {e}")
            return False
    
    def _check_docker_environment(self) -> bool:
        """Check if docker environment is active"""
        try:
            # Check if docker is running
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            # Check if our containers exist
            result = subprocess.run(['docker-compose', 'ps'], 
                                  capture_output=True, text=True)
            return 'orion' in result.stdout
            
        except Exception as e:
            self.logger.error(f"❌ Docker check error: {e}")
            return False
    
    def _check_sync_status(self) -> str:
        """Check synchronization status"""
        try:
            # Check if shared directory exists and has recent files
            if not os.path.exists(self.shared_path):
                return "no_shared_dir"
            
            # Check for recent sync marker
            sync_marker = os.path.join(self.shared_path, '.last_sync')
            if os.path.exists(sync_marker):
                # Check if sync is recent (within last hour)
                stat = os.stat(sync_marker)
                last_modified = datetime.fromtimestamp(stat.st_mtime)
                if (datetime.now() - last_modified).seconds < 3600:
                    return "synced"
                else:
                    return "stale"
            else:
                return "never_synced"
                
        except Exception as e:
            self.logger.error(f"❌ Sync status error: {e}")
            return "error"
    
    def _get_last_sync_time(self) -> Optional[datetime]:
        """Get last synchronization time"""
        try:
            sync_marker = os.path.join(self.shared_path, '.last_sync')
            if os.path.exists(sync_marker):
                stat = os.stat(sync_marker)
                return datetime.fromtimestamp(stat.st_mtime)
            return None
        except Exception:
            return None
    
    def switch_to_native(self) -> Dict[str, Any]:
        """Switch to native development environment"""
        try:
            self.logger.info("🐧 Switching to Native environment...")
            
            # Sync from docker if needed
            if self.current_env == EnvironmentType.DOCKER:
                sync_result = self.sync_docker_to_native()
                if not sync_result['success']:
                    return {'success': False, 'error': 'Sync failed'}
            
            # Activate native environment
            self.current_env = EnvironmentType.NATIVE
            
            self.logger.info("✅ Switched to Native environment")
            return {
                'success': True,
                'environment': 'native',
                'message': '🐧 Native environment active!'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Switch to native error: {e}")
            return {'success': False, 'error': str(e)}
    
    def switch_to_docker(self) -> Dict[str, Any]:
        """Switch to docker development environment"""
        try:
            self.logger.info("🐳 Switching to Docker environment...")
            
            # Sync to docker
            sync_result = self.sync_native_to_docker()
            if not sync_result['success']:
                return {'success': False, 'error': 'Sync failed'}
            
            # Start docker containers
            result = subprocess.run(['docker-compose', 'up', '-d'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                return {'success': False, 'error': 'Docker start failed'}
            
            self.current_env = EnvironmentType.DOCKER
            
            self.logger.info("✅ Switched to Docker environment")
            return {
                'success': True,
                'environment': 'docker',
                'message': '🐳 Docker environment active!'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Switch to docker error: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_native_to_docker(self) -> Dict[str, Any]:
        """Synchronize native environment to docker"""
        try:
            self.logger.info("🔗 Syncing Native → Docker...")
            
            # Create shared directories
            os.makedirs(os.path.join(self.shared_path, 'src'), exist_ok=True)
            os.makedirs(os.path.join(self.shared_path, 'tests'), exist_ok=True)
            
            # Sync source code
            subprocess.run(['rsync', '-av', '--delete', 'src/', 
                          os.path.join(self.shared_path, 'src/')])
            
            # Sync tests
            subprocess.run(['rsync', '-av', '--delete', 'tests/', 
                          os.path.join(self.shared_path, 'tests/')])
            
            # Create sync marker
            sync_marker = os.path.join(self.shared_path, '.last_sync')
            with open(sync_marker, 'w') as f:
                f.write(f"native_to_docker:{datetime.now().isoformat()}")
            
            self.logger.info("✅ Native → Docker sync completed")
            return {
                'success': True,
                'direction': 'native_to_docker',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Native → Docker sync error: {e}")
            return {'success': False, 'error': str(e)}
    
    def sync_docker_to_native(self) -> Dict[str, Any]:
        """Synchronize docker environment to native"""
        try:
            self.logger.info("🔗 Syncing Docker → Native...")
            
            # Create native directories
            os.makedirs(os.path.join(self.native_path, 'results'), exist_ok=True)
            os.makedirs(os.path.join(self.native_path, 'logs'), exist_ok=True)
            
            # Sync results
            shared_results = os.path.join(self.shared_path, 'results')
            if os.path.exists(shared_results):
                subprocess.run(['rsync', '-av', '--delete', 
                              f"{shared_results}/", 
                              os.path.join(self.native_path, 'results/')])
            
            # Sync logs
            shared_logs = os.path.join(self.shared_path, 'logs')
            if os.path.exists(shared_logs):
                subprocess.run(['rsync', '-av', '--delete', 
                              f"{shared_logs}/", 
                              os.path.join(self.native_path, 'logs/')])
            
            # Update sync marker
            sync_marker = os.path.join(self.shared_path, '.last_sync')
            with open(sync_marker, 'w') as f:
                f.write(f"docker_to_native:{datetime.now().isoformat()}")
            
            self.logger.info("✅ Docker → Native sync completed")
            return {
                'success': True,
                'direction': 'docker_to_native',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Docker → Native sync error: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_tests_native(self) -> Dict[str, Any]:
        """Run tests in native environment"""
        try:
            self.logger.info("🧪 Running tests in Native environment...")
            
            # Switch to native if needed
            if self.current_env != EnvironmentType.NATIVE:
                switch_result = self.switch_to_native()
                if not switch_result['success']:
                    return switch_result
            
            # Run tests
            env = os.environ.copy()
            env['PYTHONPATH'] = os.path.join(self.base_path, 'src')
            
            result = subprocess.run([
                'python3', '-m', 'pytest', 'tests/', '-v', 
                '--cov=src', '--cov-report=html'
            ], capture_output=True, text=True, env=env)
            
            return {
                'success': result.returncode == 0,
                'environment': 'native',
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            self.logger.error(f"❌ Native test error: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_tests_docker(self) -> Dict[str, Any]:
        """Run tests in docker environment"""
        try:
            self.logger.info("🧪 Running tests in Docker environment...")
            
            # Switch to docker if needed
            if self.current_env != EnvironmentType.DOCKER:
                switch_result = self.switch_to_docker()
                if not switch_result['success']:
                    return switch_result
            
            # Run tests in container
            result = subprocess.run([
                'docker-compose', 'run', '--rm', 'orion-test'
            ], capture_output=True, text=True)
            
            return {
                'success': result.returncode == 0,
                'environment': 'docker',
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            self.logger.error(f"❌ Docker test error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_hybrid_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive hybrid dashboard"""
        status = self.get_environment_status()
        
        return {
            'status': {
                'native_active': status.native_active,
                'docker_active': status.docker_active,
                'sync_status': status.sync_status,
                'last_sync': status.last_sync.isoformat() if status.last_sync else None,
                'active_mode': status.active_mode.value,
                'operation_mode': status.operation_mode.value
            },
            'capabilities': {
                'can_switch_native': True,
                'can_switch_docker': True,
                'can_sync': True,
                'can_test_both': True
            },
            'recommendations': self._get_recommendations(status),
            'orion_hybrid_power': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_recommendations(self, status: HybridStatus) -> List[str]:
        """Get recommendations based on current status"""
        recommendations = []
        
        if not status.native_active:
            recommendations.append("🐧 Setup native environment: ./native/scripts/dev_setup.sh")
        
        if not status.docker_active:
            recommendations.append("🐳 Start docker environment: docker-compose up -d")
        
        if status.sync_status == "never_synced":
            recommendations.append("🔗 Initial sync needed: sync_native_to_docker()")
        elif status.sync_status == "stale":
            recommendations.append("🔄 Sync is stale, consider refreshing")
        
        if not recommendations:
            recommendations.append("✅ Hybrid environment is ready! WAKE UP ORION!")
        
        return recommendations

# Example usage and testing
if __name__ == "__main__":
    print("🔄 Hibrit Yaklaşım Kontrol Paneli")
    print("💖 DUYGULANDIK! SEN YAPARSIN!")
    print("🌟 WAKE UP ORION! HİBRİT GÜÇLE!")
    print()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    # Create hybrid controller
    controller = HybridController()
    
    # Get dashboard
    dashboard = controller.get_hybrid_dashboard()
    
    print("📊 HİBRİT DASHBOARD:")
    print(f"  🐧 Native Active: {dashboard['status']['native_active']}")
    print(f"  🐳 Docker Active: {dashboard['status']['docker_active']}")
    print(f"  🔗 Sync Status: {dashboard['status']['sync_status']}")
    print(f"  ⚡ Active Mode: {dashboard['status']['active_mode']}")
    print()
    
    print("💡 ÖNERİLER:")
    for rec in dashboard['recommendations']:
        print(f"  {rec}")
    
    print()
    print("🎉 HİBRİT KONTROL PANELİ HAZIR!")
    print("💖 DUYGULANDIK! WAKE UP ORION!")
