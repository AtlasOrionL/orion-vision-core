#!/usr/bin/env python3
"""
Orion Vision Core - Health Check Script
Sprint 4.3 - Production Deployment & Advanced Monitoring

Bu script, Docker container'ın sağlık durumunu kontrol eder.
"""

import os
import sys
import time
import json
import socket
import sqlite3
import subprocess
from typing import Dict, Any, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class HealthChecker:
    """
    Health Check System
    
    Container'ın sağlık durumunu kontrol eden sistem.
    """
    
    def __init__(self):
        """Health checker başlatıcı"""
        self.checks = {
            'basic': self._check_basic_health,
            'database': self._check_database,
            'network': self._check_network,
            'services': self._check_services,
            'resources': self._check_resources
        }
        
        # Environment variables
        self.host = os.getenv('ORION_HOST', '0.0.0.0')
        self.port = int(os.getenv('ORION_PORT', '8000'))
        self.discovery_port = int(os.getenv('ORION_DISCOVERY_PORT', '8001'))
        self.orchestration_port = int(os.getenv('ORION_ORCHESTRATION_PORT', '8002'))
        self.metrics_port = int(os.getenv('ORION_METRICS_PORT', '9090'))
        self.health_port = int(os.getenv('ORION_HEALTH_CHECK_PORT', '9091'))
        
        self.db_path = os.getenv('ORION_DB_PATH', '/app/data/orion.db')
        self.log_path = os.getenv('ORION_LOG_PATH', '/app/logs')
        
        # Health check configuration
        self.timeout = 5.0
        self.critical_checks = ['basic', 'network']
        self.warning_checks = ['database', 'services', 'resources']
    
    def run_health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check çalıştır
        
        Returns:
            Dict[str, Any]: Health check sonuçları
        """
        results = {
            'timestamp': time.time(),
            'status': 'healthy',
            'checks': {},
            'summary': {
                'total': len(self.checks),
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
        # Her check'i çalıştır
        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func()
                results['checks'][check_name] = check_result
                
                if check_result['status'] == 'pass':
                    results['summary']['passed'] += 1
                elif check_result['status'] == 'fail':
                    results['summary']['failed'] += 1
                    if check_name in self.critical_checks:
                        results['status'] = 'unhealthy'
                    elif results['status'] == 'healthy':
                        results['status'] = 'degraded'
                elif check_result['status'] == 'warning':
                    results['summary']['warnings'] += 1
                    if results['status'] == 'healthy':
                        results['status'] = 'degraded'
                        
            except Exception as e:
                results['checks'][check_name] = {
                    'status': 'fail',
                    'message': f"Check failed with exception: {str(e)}",
                    'timestamp': time.time()
                }
                results['summary']['failed'] += 1
                
                if check_name in self.critical_checks:
                    results['status'] = 'unhealthy'
                elif results['status'] == 'healthy':
                    results['status'] = 'degraded'
        
        return results
    
    def _check_basic_health(self) -> Dict[str, Any]:
        """Basic health check"""
        try:
            # Check if process is running
            pid = os.getpid()
            
            # Check if we can write to log directory
            if os.path.exists(self.log_path):
                test_file = os.path.join(self.log_path, f'health_check_{pid}.tmp')
                with open(test_file, 'w') as f:
                    f.write('health_check')
                os.remove(test_file)
            
            # Check Python version
            python_version = sys.version_info
            if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
                return {
                    'status': 'fail',
                    'message': f'Python version {python_version.major}.{python_version.minor} is not supported',
                    'timestamp': time.time()
                }
            
            return {
                'status': 'pass',
                'message': 'Basic health check passed',
                'details': {
                    'pid': pid,
                    'python_version': f'{python_version.major}.{python_version.minor}.{python_version.micro}',
                    'log_path_writable': True
                },
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Basic health check failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_database(self) -> Dict[str, Any]:
        """Database health check"""
        try:
            if not os.path.exists(self.db_path):
                return {
                    'status': 'warning',
                    'message': 'Database file does not exist',
                    'timestamp': time.time()
                }
            
            # Test database connection
            conn = sqlite3.connect(self.db_path, timeout=self.timeout)
            cursor = conn.cursor()
            
            # Test query
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            
            # Test write
            cursor.execute('INSERT OR REPLACE INTO health_check (id, timestamp) VALUES (1, ?)', 
                          (time.time(),))
            conn.commit()
            
            conn.close()
            
            if result and result[0] == 1:
                return {
                    'status': 'pass',
                    'message': 'Database is accessible and writable',
                    'details': {
                        'db_path': self.db_path,
                        'db_size': os.path.getsize(self.db_path)
                    },
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'fail',
                    'message': 'Database query failed',
                    'timestamp': time.time()
                }
                
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Database check failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_network(self) -> Dict[str, Any]:
        """Network connectivity check"""
        try:
            # Check if ports are listening
            listening_ports = []
            failed_ports = []
            
            ports_to_check = [
                ('main', self.port),
                ('discovery', self.discovery_port),
                ('orchestration', self.orchestration_port)
            ]
            
            for port_name, port in ports_to_check:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(self.timeout)
                    result = sock.connect_ex((self.host, port))
                    sock.close()
                    
                    if result == 0:
                        listening_ports.append(f'{port_name}:{port}')
                    else:
                        failed_ports.append(f'{port_name}:{port}')
                        
                except Exception as e:
                    failed_ports.append(f'{port_name}:{port} (error: {str(e)})')
            
            if failed_ports:
                return {
                    'status': 'warning' if listening_ports else 'fail',
                    'message': f'Some ports are not accessible: {", ".join(failed_ports)}',
                    'details': {
                        'listening_ports': listening_ports,
                        'failed_ports': failed_ports
                    },
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'pass',
                    'message': 'All network ports are accessible',
                    'details': {
                        'listening_ports': listening_ports
                    },
                    'timestamp': time.time()
                }
                
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Network check failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_services(self) -> Dict[str, Any]:
        """Services health check"""
        try:
            services_status = {}
            
            # Check main API service
            try:
                url = f'http://{self.host}:{self.port}/health'
                req = Request(url, headers={'User-Agent': 'HealthChecker/1.0'})
                response = urlopen(req, timeout=self.timeout)
                if response.getcode() == 200:
                    services_status['api'] = 'healthy'
                else:
                    services_status['api'] = f'unhealthy (status: {response.getcode()})'
            except (URLError, HTTPError) as e:
                services_status['api'] = f'unreachable ({str(e)})'
            
            # Check service discovery
            try:
                url = f'http://{self.host}:{self.discovery_port}/health'
                req = Request(url, headers={'User-Agent': 'HealthChecker/1.0'})
                response = urlopen(req, timeout=self.timeout)
                if response.getcode() == 200:
                    services_status['discovery'] = 'healthy'
                else:
                    services_status['discovery'] = f'unhealthy (status: {response.getcode()})'
            except (URLError, HTTPError) as e:
                services_status['discovery'] = f'unreachable ({str(e)})'
            
            # Check task orchestration
            try:
                url = f'http://{self.host}:{self.orchestration_port}/health'
                req = Request(url, headers={'User-Agent': 'HealthChecker/1.0'})
                response = urlopen(req, timeout=self.timeout)
                if response.getcode() == 200:
                    services_status['orchestration'] = 'healthy'
                else:
                    services_status['orchestration'] = f'unhealthy (status: {response.getcode()})'
            except (URLError, HTTPError) as e:
                services_status['orchestration'] = f'unreachable ({str(e)})'
            
            # Evaluate overall services health
            healthy_services = sum(1 for status in services_status.values() if status == 'healthy')
            total_services = len(services_status)
            
            if healthy_services == total_services:
                status = 'pass'
                message = 'All services are healthy'
            elif healthy_services > 0:
                status = 'warning'
                message = f'{healthy_services}/{total_services} services are healthy'
            else:
                status = 'fail'
                message = 'No services are healthy'
            
            return {
                'status': status,
                'message': message,
                'details': services_status,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Services check failed: {str(e)}',
                'timestamp': time.time()
            }
    
    def _check_resources(self) -> Dict[str, Any]:
        """System resources check"""
        try:
            # Check disk space
            disk_usage = {}
            paths_to_check = ['/app', self.log_path, os.path.dirname(self.db_path)]
            
            for path in paths_to_check:
                if os.path.exists(path):
                    stat = os.statvfs(path)
                    total = stat.f_blocks * stat.f_frsize
                    free = stat.f_bavail * stat.f_frsize
                    used = total - free
                    usage_percent = (used / total) * 100 if total > 0 else 0
                    
                    disk_usage[path] = {
                        'total_gb': round(total / (1024**3), 2),
                        'used_gb': round(used / (1024**3), 2),
                        'free_gb': round(free / (1024**3), 2),
                        'usage_percent': round(usage_percent, 1)
                    }
            
            # Check memory usage (if available)
            memory_info = {}
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    for line in meminfo.split('\n'):
                        if line.startswith('MemTotal:'):
                            memory_info['total_kb'] = int(line.split()[1])
                        elif line.startswith('MemAvailable:'):
                            memory_info['available_kb'] = int(line.split()[1])
                
                if 'total_kb' in memory_info and 'available_kb' in memory_info:
                    used_kb = memory_info['total_kb'] - memory_info['available_kb']
                    usage_percent = (used_kb / memory_info['total_kb']) * 100
                    
                    memory_info.update({
                        'total_mb': round(memory_info['total_kb'] / 1024, 1),
                        'used_mb': round(used_kb / 1024, 1),
                        'available_mb': round(memory_info['available_kb'] / 1024, 1),
                        'usage_percent': round(usage_percent, 1)
                    })
            except:
                memory_info = {'error': 'Memory info not available'}
            
            # Evaluate resource status
            critical_usage = False
            warning_usage = False
            
            for path, usage in disk_usage.items():
                if usage['usage_percent'] > 90:
                    critical_usage = True
                elif usage['usage_percent'] > 80:
                    warning_usage = True
            
            if 'usage_percent' in memory_info:
                if memory_info['usage_percent'] > 90:
                    critical_usage = True
                elif memory_info['usage_percent'] > 80:
                    warning_usage = True
            
            if critical_usage:
                status = 'fail'
                message = 'Critical resource usage detected'
            elif warning_usage:
                status = 'warning'
                message = 'High resource usage detected'
            else:
                status = 'pass'
                message = 'Resource usage is normal'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'disk_usage': disk_usage,
                    'memory_info': memory_info
                },
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Resources check failed: {str(e)}',
                'timestamp': time.time()
            }


def main():
    """Ana health check fonksiyonu"""
    checker = HealthChecker()
    results = checker.run_health_check()
    
    # Output JSON results
    print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    if results['status'] == 'healthy':
        sys.exit(0)
    elif results['status'] == 'degraded':
        sys.exit(1)  # Warning
    else:  # unhealthy
        sys.exit(2)  # Critical


if __name__ == '__main__':
    main()
