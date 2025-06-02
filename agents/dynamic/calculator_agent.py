#!/usr/bin/env python3
"""
Calculator Agent - Dynamic Agent Example
Orion Vision Core - Dinamik Yüklenen Hesap Makinesi Agent'ı

Bu agent, temel matematik işlemlerini gerçekleştiren dinamik bir agent örneğidir.
Dynamic Agent Loader tarafından runtime'da yüklenebilir.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import time
import random
import math
from typing import Dict, Any, List

# Agent core'u import et (dynamic loader tarafından sağlanır)
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'jobone', 'vision_core'))

from agent_core import Agent, AgentConfig, AgentStatus


class CalculatorAgent(Agent):
    """
    Calculator Agent - Dinamik Hesap Makinesi Agent'ı
    
    Bu agent, matematik işlemlerini gerçekleştiren dinamik bir agent'tır.
    Runtime'da yüklenebilir ve çeşitli hesaplama görevlerini yerine getirir.
    """
    
    def __init__(self, config: AgentConfig, auto_register: bool = True):
        """
        Calculator Agent başlatıcı
        
        Args:
            config: Agent konfigürasyon objesi
            auto_register: Otomatik registry'ye kayıt
        """
        super().__init__(config, auto_register)
        
        # Calculator'a özel değişkenler
        self.calculation_count = 0
        self.last_result = 0.0
        self.calculation_history: List[Dict[str, Any]] = []
        self.supported_operations = [
            'add', 'subtract', 'multiply', 'divide',
            'power', 'sqrt', 'sin', 'cos', 'tan',
            'log', 'factorial'
        ]
        
        # Agent yetenekleri ekle
        self.add_capability("mathematical_calculations")
        self.add_capability("basic_arithmetic")
        self.add_capability("advanced_math")
        self.add_capability("calculation_history")
        
        self.logger.info(f"Calculator Agent initialized with {len(self.supported_operations)} operations")
    
    def initialize(self) -> bool:
        """
        Agent'a özel başlatma işlemleri
        
        Returns:
            bool: Başlatma başarılı ise True
        """
        try:
            self.logger.info("Initializing Calculator Agent...")
            
            # Başlatma işlemleri
            self.calculation_count = 0
            self.last_result = 0.0
            self.calculation_history.clear()
            
            # Test hesaplaması
            test_result = self._calculate('add', [2, 2])
            if test_result != 4:
                self.logger.error("Calculator test failed")
                return False
            
            self.logger.info("Calculator Agent initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Calculator Agent initialization failed: {e}")
            return False
    
    def run(self):
        """
        Agent'ın ana çalışma döngüsü
        """
        self.logger.info("Calculator Agent main loop started")
        
        try:
            while not self.stop_event.is_set():
                # Simulated calculation work
                self._do_calculation_work()
                
                # Work interval kadar bekle
                if self.stop_event.wait(3.0):
                    break  # Stop event set edildi
                
        except Exception as e:
            self.logger.error(f"Calculator Agent run error: {e}")
            raise
        finally:
            self.logger.info("Calculator Agent main loop ended")
    
    def cleanup(self):
        """
        Agent'a özel temizlik işlemleri
        """
        try:
            self.logger.info("Cleaning up Calculator Agent...")
            
            # İstatistikleri kaydet
            self.logger.info(f"Total calculations performed: {self.calculation_count}")
            self.logger.info(f"Last result: {self.last_result}")
            self.logger.info(f"History entries: {len(self.calculation_history)}")
            
            # İstatistikleri güncelle
            self.stats['tasks_completed'] = self.calculation_count
            self.stats['last_result'] = self.last_result
            
            self.logger.info("Calculator Agent cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Calculator Agent cleanup error: {e}")
    
    def _do_calculation_work(self):
        """Simulated calculation work"""
        try:
            # Random matematik işlemi yap
            operation = random.choice(['add', 'multiply', 'power', 'sqrt'])
            
            if operation in ['add', 'multiply']:
                # İki sayılı işlemler
                a = random.randint(1, 100)
                b = random.randint(1, 100)
                operands = [a, b]
            elif operation == 'power':
                # Üs alma
                base = random.randint(2, 10)
                exponent = random.randint(2, 5)
                operands = [base, exponent]
            elif operation == 'sqrt':
                # Karekök
                number = random.randint(1, 1000)
                operands = [number]
            else:
                operands = [random.randint(1, 100)]
            
            # Hesaplama yap
            result = self._calculate(operation, operands)
            
            if result is not None:
                self.logger.info(f"Calculation: {operation}({operands}) = {result}")
                self.stats['tasks_completed'] += 1
            else:
                self.logger.warning(f"Calculation failed: {operation}({operands})")
                self.stats['tasks_failed'] += 1
                
        except Exception as e:
            self.logger.error(f"Calculation work error: {e}")
            self.stats['tasks_failed'] += 1
    
    def _calculate(self, operation: str, operands: List[float]) -> float:
        """
        Matematik işlemi gerçekleştir
        
        Args:
            operation: İşlem tipi
            operands: İşlem operandları
            
        Returns:
            float: Hesaplama sonucu
        """
        try:
            if operation not in self.supported_operations:
                raise ValueError(f"Unsupported operation: {operation}")
            
            if operation == 'add':
                result = sum(operands)
            elif operation == 'subtract':
                result = operands[0] - sum(operands[1:])
            elif operation == 'multiply':
                result = 1
                for operand in operands:
                    result *= operand
            elif operation == 'divide':
                result = operands[0]
                for operand in operands[1:]:
                    if operand == 0:
                        raise ValueError("Division by zero")
                    result /= operand
            elif operation == 'power':
                result = operands[0] ** operands[1]
            elif operation == 'sqrt':
                if operands[0] < 0:
                    raise ValueError("Square root of negative number")
                result = math.sqrt(operands[0])
            elif operation == 'sin':
                result = math.sin(math.radians(operands[0]))
            elif operation == 'cos':
                result = math.cos(math.radians(operands[0]))
            elif operation == 'tan':
                result = math.tan(math.radians(operands[0]))
            elif operation == 'log':
                if operands[0] <= 0:
                    raise ValueError("Logarithm of non-positive number")
                result = math.log(operands[0])
            elif operation == 'factorial':
                if operands[0] < 0 or operands[0] != int(operands[0]):
                    raise ValueError("Factorial of negative or non-integer number")
                result = math.factorial(int(operands[0]))
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Sonucu kaydet
            self.last_result = result
            self.calculation_count += 1
            
            # Geçmişe ekle
            calculation_record = {
                'operation': operation,
                'operands': operands,
                'result': result,
                'timestamp': time.time()
            }
            self.calculation_history.append(calculation_record)
            
            # Geçmiş boyutunu sınırla
            if len(self.calculation_history) > 100:
                self.calculation_history.pop(0)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Calculation error: {e}")
            return None
    
    def calculate(self, operation: str, operands: List[float]) -> Dict[str, Any]:
        """
        Public calculation interface
        
        Args:
            operation: İşlem tipi
            operands: İşlem operandları
            
        Returns:
            Dict: Hesaplama sonucu ve metadata
        """
        try:
            result = self._calculate(operation, operands)
            
            return {
                'success': result is not None,
                'operation': operation,
                'operands': operands,
                'result': result,
                'calculation_count': self.calculation_count,
                'timestamp': time.time()
            }
            
        except Exception as e:
            return {
                'success': False,
                'operation': operation,
                'operands': operands,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def get_calculation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Hesaplama geçmişini getir
        
        Args:
            limit: Döndürülecek kayıt sayısı
            
        Returns:
            List: Hesaplama geçmişi
        """
        return self.calculation_history[-limit:] if limit > 0 else self.calculation_history
    
    def get_supported_operations(self) -> List[str]:
        """Desteklenen işlemlerin listesini döndür"""
        return self.supported_operations.copy()
    
    def get_calculator_stats(self) -> Dict[str, Any]:
        """Calculator istatistiklerini getir"""
        return {
            'calculation_count': self.calculation_count,
            'last_result': self.last_result,
            'history_size': len(self.calculation_history),
            'supported_operations': len(self.supported_operations),
            'agent_status': self.status.value,
            'uptime': time.time() - self.start_time if self.start_time else 0
        }
    
    def clear_history(self):
        """Hesaplama geçmişini temizle"""
        self.calculation_history.clear()
        self.logger.info("Calculation history cleared")
    
    def reset_calculator(self):
        """Calculator'ı sıfırla"""
        self.calculation_count = 0
        self.last_result = 0.0
        self.clear_history()
        self.logger.info("Calculator reset completed")
