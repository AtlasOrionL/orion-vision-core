#!/usr/bin/env python3
"""
Validation Engine - Scenario validation and verification
"""

import logging
import time
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from . import scenarios_metrics, VALIDATION_CRITERIA

class ValidationType(Enum):
    """Types of validation"""
    FILE_EXISTS = "file_exists"
    CONTENT_MATCH = "content_match"
    VISUAL_VERIFICATION = "visual_verification"
    OUTPUT_VERIFICATION = "output_verification"
    PERFORMANCE_CHECK = "performance_check"

@dataclass
class ValidationRule:
    """Validation rule definition"""
    rule_id: str
    validation_type: ValidationType
    parameters: Dict[str, Any]
    timeout: float = 10.0
    critical: bool = True

@dataclass
class ValidationResult:
    """Validation result"""
    rule_id: str
    success: bool
    message: str
    details: Dict[str, Any] = None
    execution_time: float = 0.0

class ValidationEngine:
    """
    Scenario validation and verification engine
    Validates scenario execution results and system state
    """
    
    def __init__(self, computer_access_manager):
        self.logger = logging.getLogger('orion.computer_access.scenarios.validation')
        
        # Computer access manager reference
        self.computer_access_manager = computer_access_manager
        
        # Validation state
        self.initialized = False
        self.validation_rules = {}
        self.custom_validators = {}
        
        # Performance tracking
        self.validations_performed = 0
        self.successful_validations = 0
        self.failed_validations = 0
        self.total_validation_time = 0.0
        
        self.logger.info("✅ ValidationEngine initialized")
    
    def initialize(self) -> bool:
        """
        Initialize validation engine
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing validation engine...")
            
            # Load default validation rules
            self._load_default_rules()
            
            # Register built-in validators
            self._register_builtin_validators()
            
            self.initialized = True
            self.logger.info("✅ Validation engine initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Validation engine initialization failed: {e}")
            return False
    
    def validate_scenario(self, scenario, scenario_result) -> Dict[str, Any]:
        """
        Validate complete scenario execution
        
        Args:
            scenario: Scenario definition
            scenario_result: Scenario execution result
            
        Returns:
            Dict containing validation result
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"✅ Validating scenario: {scenario.name}")
            
            validation_results = []
            overall_success = True
            
            # Get validation criteria
            criteria_name = scenario.validation_criteria
            if criteria_name and criteria_name in VALIDATION_CRITERIA:
                criteria = VALIDATION_CRITERIA[criteria_name]
                
                # Create validation rule from criteria
                rule = ValidationRule(
                    rule_id=f"scenario_{scenario.scenario_id}",
                    validation_type=ValidationType(criteria['method']),
                    parameters=criteria,
                    timeout=criteria.get('timeout', 10.0)
                )
                
                # Execute validation
                result = self._execute_validation_rule(rule, scenario, scenario_result)
                validation_results.append(result)
                
                if not result.success:
                    overall_success = False
            
            # Additional validations based on scenario steps
            for step_result in scenario_result.step_results or []:
                if step_result.get('success', True):
                    # Validate successful steps
                    step_validation = self._validate_step_result(step_result)
                    if step_validation:
                        validation_results.append(step_validation)
                        if not step_validation.success:
                            overall_success = False
            
            execution_time = time.time() - start_time
            self.total_validation_time += execution_time
            scenarios_metrics.record_validation_time(execution_time)
            
            self.validations_performed += 1
            if overall_success:
                self.successful_validations += 1
            else:
                self.failed_validations += 1
            
            result = {
                'success': overall_success,
                'validation_results': validation_results,
                'execution_time': execution_time,
                'total_validations': len(validation_results)
            }
            
            self.logger.info(f"✅ Scenario validation completed: {overall_success} ({execution_time:.3f}s)")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.total_validation_time += execution_time
            self.failed_validations += 1
            
            self.logger.error(f"❌ Scenario validation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            }
    
    def validate_step(self, step) -> Dict[str, Any]:
        """
        Validate individual scenario step
        
        Args:
            step: Scenario step to validate
            
        Returns:
            Dict containing validation result
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"✅ Validating step: {step.action}")
            
            # Determine validation type based on step
            if step.step_type == 'terminal' and step.action == 'create_file':
                # Validate file creation
                filename = step.parameters.get('filename')
                if filename:
                    rule = ValidationRule(
                        rule_id=f"step_{step.step_id}",
                        validation_type=ValidationType.FILE_EXISTS,
                        parameters={'filename': filename}
                    )
                    
                    result = self._execute_validation_rule(rule, None, None)
                    
                    execution_time = time.time() - start_time
                    return {
                        'success': result.success,
                        'message': result.message,
                        'execution_time': execution_time
                    }
            
            # Default: assume step validation passed
            execution_time = time.time() - start_time
            return {
                'success': True,
                'message': 'Step validation passed',
                'execution_time': execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            self.logger.error(f"❌ Step validation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            }
    
    def _execute_validation_rule(self, rule: ValidationRule, scenario, scenario_result) -> ValidationResult:
        """Execute individual validation rule"""
        start_time = time.time()
        
        try:
            if rule.validation_type == ValidationType.FILE_EXISTS:
                return self._validate_file_exists(rule)
            elif rule.validation_type == ValidationType.CONTENT_MATCH:
                return self._validate_content_match(rule)
            elif rule.validation_type == ValidationType.VISUAL_VERIFICATION:
                return self._validate_visual_verification(rule)
            elif rule.validation_type == ValidationType.OUTPUT_VERIFICATION:
                return self._validate_output_verification(rule, scenario_result)
            elif rule.validation_type == ValidationType.PERFORMANCE_CHECK:
                return self._validate_performance_check(rule, scenario_result)
            else:
                raise ValueError(f"Unknown validation type: {rule.validation_type}")
                
        except Exception as e:
            execution_time = time.time() - start_time
            
            return ValidationResult(
                rule_id=rule.rule_id,
                success=False,
                message=f"Validation error: {e}",
                execution_time=execution_time
            )
    
    def _validate_file_exists(self, rule: ValidationRule) -> ValidationResult:
        """Validate file existence"""
        start_time = time.time()
        
        filename = rule.parameters.get('filename')
        if not filename:
            return ValidationResult(
                rule_id=rule.rule_id,
                success=False,
                message="Filename parameter required",
                execution_time=time.time() - start_time
            )
        
        exists = os.path.exists(filename)
        execution_time = time.time() - start_time
        
        return ValidationResult(
            rule_id=rule.rule_id,
            success=exists,
            message=f"File {'exists' if exists else 'does not exist'}: {filename}",
            details={'filename': filename, 'exists': exists},
            execution_time=execution_time
        )
    
    def _validate_content_match(self, rule: ValidationRule) -> ValidationResult:
        """Validate content matching"""
        start_time = time.time()
        
        filename = rule.parameters.get('filename')
        expected_content = rule.parameters.get('expected_content', '')
        
        if not filename:
            return ValidationResult(
                rule_id=rule.rule_id,
                success=False,
                message="Filename parameter required",
                execution_time=time.time() - start_time
            )
        
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    actual_content = f.read().strip()
                
                matches = expected_content in actual_content
                execution_time = time.time() - start_time
                
                return ValidationResult(
                    rule_id=rule.rule_id,
                    success=matches,
                    message=f"Content {'matches' if matches else 'does not match'} expected",
                    details={
                        'filename': filename,
                        'expected': expected_content,
                        'actual': actual_content,
                        'matches': matches
                    },
                    execution_time=execution_time
                )
            else:
                execution_time = time.time() - start_time
                return ValidationResult(
                    rule_id=rule.rule_id,
                    success=False,
                    message=f"File does not exist: {filename}",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ValidationResult(
                rule_id=rule.rule_id,
                success=False,
                message=f"Error reading file: {e}",
                execution_time=execution_time
            )
    
    def _validate_visual_verification(self, rule: ValidationRule) -> ValidationResult:
        """Validate using visual verification"""
        start_time = time.time()
        
        try:
            # Use screen agent to capture and analyze
            if not self.computer_access_manager.screen:
                raise RuntimeError("Screen agent not available")
            
            element_type = rule.parameters.get('element_type')
            confidence_threshold = rule.parameters.get('confidence', 0.7)
            
            result = self.computer_access_manager.screen.capture_and_analyze({
                'detection_types': ['ui_elements'],
                'confidence_threshold': confidence_threshold
            })
            
            if result['success']:
                elements = result['analysis'].elements
                if element_type:
                    matching_elements = [
                        elem for elem in elements 
                        if elem.element_type == element_type
                    ]
                    found = len(matching_elements) > 0
                else:
                    found = len(elements) > 0
                
                execution_time = time.time() - start_time
                
                return ValidationResult(
                    rule_id=rule.rule_id,
                    success=found,
                    message=f"Visual element {'found' if found else 'not found'}",
                    details={
                        'element_type': element_type,
                        'elements_found': len(elements),
                        'matching_elements': len(matching_elements) if element_type else len(elements)
                    },
                    execution_time=execution_time
                )
            else:
                execution_time = time.time() - start_time
                return ValidationResult(
                    rule_id=rule.rule_id,
                    success=False,
                    message="Visual analysis failed",
                    execution_time=execution_time
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return ValidationResult(
                rule_id=rule.rule_id,
                success=False,
                message=f"Visual verification error: {e}",
                execution_time=execution_time
            )
    
    def _validate_output_verification(self, rule: ValidationRule, scenario_result) -> ValidationResult:
        """Validate command output"""
        start_time = time.time()
        
        expected_output = rule.parameters.get('expected_output', '')
        expected_return_code = rule.parameters.get('expected_return_code', 0)
        
        # Check step results for terminal commands
        if scenario_result and scenario_result.step_results:
            for step_result in scenario_result.step_results:
                if step_result.get('result', {}).get('output'):
                    output = step_result['result']['output']
                    return_code = step_result['result'].get('return_code', 0)
                    
                    output_matches = expected_output in output if expected_output else True
                    code_matches = return_code == expected_return_code
                    
                    success = output_matches and code_matches
                    execution_time = time.time() - start_time
                    
                    return ValidationResult(
                        rule_id=rule.rule_id,
                        success=success,
                        message=f"Output verification {'passed' if success else 'failed'}",
                        details={
                            'expected_output': expected_output,
                            'actual_output': output,
                            'expected_return_code': expected_return_code,
                            'actual_return_code': return_code,
                            'output_matches': output_matches,
                            'code_matches': code_matches
                        },
                        execution_time=execution_time
                    )
        
        execution_time = time.time() - start_time
        return ValidationResult(
            rule_id=rule.rule_id,
            success=False,
            message="No command output found to verify",
            execution_time=execution_time
        )
    
    def _validate_performance_check(self, rule: ValidationRule, scenario_result) -> ValidationResult:
        """Validate performance metrics"""
        start_time = time.time()
        
        max_execution_time = rule.parameters.get('max_execution_time', 60.0)
        
        if scenario_result:
            actual_time = scenario_result.execution_time
            within_limit = actual_time <= max_execution_time
            
            execution_time = time.time() - start_time
            
            return ValidationResult(
                rule_id=rule.rule_id,
                success=within_limit,
                message=f"Performance check {'passed' if within_limit else 'failed'}",
                details={
                    'max_execution_time': max_execution_time,
                    'actual_execution_time': actual_time,
                    'within_limit': within_limit
                },
                execution_time=execution_time
            )
        
        execution_time = time.time() - start_time
        return ValidationResult(
            rule_id=rule.rule_id,
            success=False,
            message="No scenario result to validate",
            execution_time=execution_time
        )
    
    def _validate_step_result(self, step_result: Dict[str, Any]) -> Optional[ValidationResult]:
        """Validate individual step result"""
        # This could be expanded to validate specific step types
        return None
    
    def _load_default_rules(self):
        """Load default validation rules"""
        # Load rules from VALIDATION_CRITERIA
        for criteria_name, criteria in VALIDATION_CRITERIA.items():
            rule = ValidationRule(
                rule_id=criteria_name,
                validation_type=ValidationType(criteria['method']),
                parameters=criteria,
                timeout=criteria.get('timeout', 10.0)
            )
            self.validation_rules[criteria_name] = rule
    
    def _register_builtin_validators(self):
        """Register built-in validator functions"""
        self.custom_validators = {
            'file_exists': self._validate_file_exists,
            'content_match': self._validate_content_match,
            'visual_verification': self._validate_visual_verification,
            'output_verification': self._validate_output_verification,
            'performance_check': self._validate_performance_check
        }
    
    def add_custom_validator(self, name: str, validator_func: Callable) -> bool:
        """Add custom validator function"""
        try:
            self.custom_validators[name] = validator_func
            self.logger.info(f"✅ Custom validator added: {name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to add custom validator: {e}")
            return False
    
    def is_ready(self) -> bool:
        """Check if validation engine is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get validation engine status"""
        avg_validation_time = self.total_validation_time / max(self.validations_performed, 1)
        
        return {
            'initialized': self.initialized,
            'validations_performed': self.validations_performed,
            'successful_validations': self.successful_validations,
            'failed_validations': self.failed_validations,
            'success_rate': (self.successful_validations / max(self.validations_performed, 1)) * 100,
            'total_validation_time': self.total_validation_time,
            'average_validation_time': avg_validation_time,
            'validation_rules_loaded': len(self.validation_rules),
            'custom_validators': len(self.custom_validators)
        }
    
    def shutdown(self):
        """Shutdown validation engine"""
        self.logger.info("🛑 Shutting down validation engine")
        
        # Clear validation rules and validators
        self.validation_rules.clear()
        self.custom_validators.clear()
        
        self.initialized = False
        self.logger.info("✅ Validation engine shutdown complete")
