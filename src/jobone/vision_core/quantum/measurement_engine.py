"""
👁️ Measurement Engine - Q4.1 Engine Component

Non-Demolitional Measurement Unit (NDMU) engine implementation
Modular design following Q_TASK_ARCHITECTURE (300-line limit)

Author: Orion Vision Core Team
Based on: Q4.1 Non-Demolitional Measurement Units
Priority: CRITICAL - Modular Design Refactoring Phase 6
"""

import logging
import copy
import time
from typing import Dict, List, Any, Optional, Tuple

# Import core components
from .measurement_core import (
    MeasurementType, MeasurementMode, ObserverType, MeasurementResult,
    create_measurement_result, calculate_measurement_uncertainty, calculate_measurement_confidence
)

# Import base components
from .planck_information_unit import PlanckInformationUnit
from .lepton_phase_space import LeptonPhaseSpace

class NonDemolitionalMeasurementUnit:
    """
    Non-Demolitional Measurement Unit (NDMU)
    
    Lepton'ları ve QCB'leri durumlarını değiştirmeden ölçme sistemi.
    """
    
    def __init__(self, 
                 measurement_type: MeasurementType = MeasurementType.NON_DEMOLITIONAL,
                 default_mode: MeasurementMode = MeasurementMode.COPY_ONLY):
        self.logger = logging.getLogger(__name__)
        self.measurement_type = measurement_type
        self.default_mode = default_mode
        
        # Measurement registry
        self.measurement_history: List[MeasurementResult] = []
        self.active_measurements: Dict[str, MeasurementResult] = {}
        
        # NDMU configuration
        self.coherence_threshold = 0.7               # Yüksek koherans eşiği
        self.max_disturbance = 0.05                  # Maksimum izin verilen bozulma
        self.measurement_precision = 0.001           # Ölçüm hassasiyeti
        
        # Statistics
        self.total_measurements = 0
        self.successful_ndm_count = 0
        self.state_preservation_rate = 1.0
        
        self.logger.info(f"👁️ NonDemolitionalMeasurementUnit initialized - Q4.1 Implementation "
                        f"({measurement_type.value}, {default_mode.value})")
    
    def measure_information_unit(self, 
                                information_unit: PlanckInformationUnit,
                                observer_id: str = "",
                                observer_type: ObserverType = ObserverType.S_EHP,
                                measurement_mode: Optional[MeasurementMode] = None) -> MeasurementResult:
        """Measure information unit non-demolitionally"""
        
        start_time = time.time()
        mode = measurement_mode or self.default_mode
        
        # Create measurement result
        result = create_measurement_result(
            target_id=information_unit.unit_id,
            target_type="PlanckInformationUnit",
            measurement_type=self.measurement_type,
            measurement_mode=mode,
            observer_id=observer_id,
            observer_type=observer_type
        )
        
        try:
            # Check if NDMU mode should be used
            use_ndm = self._should_use_ndm_mode(information_unit)
            
            if use_ndm and mode == MeasurementMode.COPY_ONLY:
                # Non-demolitional measurement via copying
                measured_value, disturbance = self._measure_via_copy(information_unit)
                result.original_state_preserved = True
                result.state_disturbance = disturbance
                
            elif use_ndm and mode == MeasurementMode.SHADOW_MEASUREMENT:
                # Shadow measurement technique
                measured_value, disturbance = self._measure_via_shadow(information_unit)
                result.original_state_preserved = True
                result.state_disturbance = disturbance
                
            elif use_ndm and mode == MeasurementMode.ENTANGLED_PROBE:
                # Entangled probe measurement
                measured_value, disturbance = self._measure_via_entangled_probe(information_unit)
                result.original_state_preserved = True
                result.state_disturbance = disturbance
                
            else:
                # Classical measurement (potentially demolitional)
                measured_value, disturbance = self._measure_classical(information_unit)
                result.original_state_preserved = disturbance < self.max_disturbance
                result.state_disturbance = disturbance
            
            # Set measurement results
            result.measured_value = measured_value
            result.measurement_uncertainty = calculate_measurement_uncertainty(
                self.measurement_precision, mode, information_unit.coherence_factor
            )
            result.measurement_confidence = calculate_measurement_confidence(disturbance)
            result.coherence_loss = disturbance * 0.5  # Coherence loss proportional to disturbance
            
            # Update statistics
            self.total_measurements += 1
            if result.original_state_preserved:
                self.successful_ndm_count += 1
            
            self._update_preservation_rate()
            
        except Exception as e:
            self.logger.error(f"❌ NDMU measurement failed: {e}")
            result.measured_value = None
            result.original_state_preserved = False
            result.state_disturbance = 1.0
            result.measurement_confidence = 0.0
        
        # Finalize measurement
        result.measurement_duration = time.time() - start_time
        self.measurement_history.append(result)
        
        # Limit history size
        if len(self.measurement_history) > 1000:
            self.measurement_history = self.measurement_history[-500:]
        
        self.logger.debug(f"👁️ NDMU measurement: {result.target_id[:8]}... "
                         f"(preserved: {result.original_state_preserved}, "
                         f"quality: {result.calculate_measurement_quality():.3f})")
        
        return result
    
    def measure_lepton_phase_space(self, 
                                  lepton: LeptonPhaseSpace,
                                  observer_id: str = "",
                                  observer_type: ObserverType = ObserverType.OBSERVER_AI,
                                  measurement_mode: Optional[MeasurementMode] = None) -> MeasurementResult:
        """Measure lepton phase space non-demolitionally"""
        
        start_time = time.time()
        mode = measurement_mode or self.default_mode
        
        # Create measurement result
        result = create_measurement_result(
            target_id=lepton.lepton_id,
            target_type="LeptonPhaseSpace",
            measurement_type=self.measurement_type,
            measurement_mode=mode,
            observer_id=observer_id,
            observer_type=observer_type
        )
        
        try:
            # Check coherence for NDMU eligibility
            coherence = lepton.polarization_vector.coherence_factor
            use_ndm = coherence >= self.coherence_threshold
            
            if use_ndm:
                # Non-demolitional measurement of lepton
                measured_data, disturbance = self._measure_lepton_ndm(lepton, mode)
                result.original_state_preserved = True
                result.state_disturbance = disturbance
            else:
                # Classical measurement (may cause collapse)
                measured_data, disturbance = self._measure_lepton_classical(lepton)
                result.original_state_preserved = disturbance < self.max_disturbance
                result.state_disturbance = disturbance
            
            # Set measurement results
            result.measured_value = measured_data
            result.measurement_uncertainty = calculate_measurement_uncertainty(
                self.measurement_precision, mode, coherence
            )
            result.measurement_confidence = calculate_measurement_confidence(disturbance)
            result.coherence_loss = disturbance * coherence  # Coherence-dependent loss
            
            # Update statistics
            self.total_measurements += 1
            if result.original_state_preserved:
                self.successful_ndm_count += 1
            
            self._update_preservation_rate()
            
        except Exception as e:
            self.logger.error(f"❌ Lepton NDMU measurement failed: {e}")
            result.measured_value = None
            result.original_state_preserved = False
            result.state_disturbance = 1.0
            result.measurement_confidence = 0.0
        
        # Finalize measurement
        result.measurement_duration = time.time() - start_time
        self.measurement_history.append(result)
        
        return result
    
    def _should_use_ndm_mode(self, information_unit: PlanckInformationUnit) -> bool:
        """Determine if NDM mode should be used"""
        # Use NDM for high-coherence, high-content units
        return (information_unit.coherence_factor >= self.coherence_threshold and
                information_unit.information_content >= information_unit.planck_constant)
    
    def _measure_via_copy(self, information_unit: PlanckInformationUnit) -> Tuple[Dict[str, Any], float]:
        """Measure via creating a copy (minimal disturbance)"""
        unit_copy = copy.deepcopy(information_unit)
        measured_data = {
            'information_content': unit_copy.information_content,
            'coherence_factor': unit_copy.coherence_factor,
            'entropy_level': unit_copy.entropy_level,
            'effective_mass': unit_copy.get_effective_mass(),
            'quality': unit_copy.quality.value
        }
        return measured_data, 0.001

    def _measure_via_shadow(self, information_unit: PlanckInformationUnit) -> Tuple[Dict[str, Any], float]:
        """Measure via shadow measurement technique"""
        measured_data = {
            'information_content_estimate': information_unit.information_content * 0.99,
            'coherence_estimate': information_unit.coherence_factor * 0.98,
            'entropy_estimate': information_unit.entropy_level * 1.01,
            'measurement_method': 'shadow'
        }
        return measured_data, 0.005

    def _measure_via_entangled_probe(self, information_unit: PlanckInformationUnit) -> Tuple[Dict[str, Any], float]:
        """Measure via entangled probe"""
        measured_data = {
            'correlated_information': information_unit.information_content,
            'entangled_coherence': information_unit.coherence_factor,
            'quantum_correlation': 0.95,
            'measurement_method': 'entangled_probe'
        }
        return measured_data, 0.002

    def _measure_classical(self, information_unit: PlanckInformationUnit) -> Tuple[Dict[str, Any], float]:
        """Classical measurement (potentially demolitional)"""
        measured_data = {
            'information_content': information_unit.information_content,
            'coherence_factor': information_unit.coherence_factor,
            'direct_measurement': True
        }
        disturbance = 0.1 * (1.0 - information_unit.coherence_factor)
        return measured_data, disturbance

    def _measure_lepton_ndm(self, lepton: LeptonPhaseSpace, mode: MeasurementMode) -> Tuple[Dict[str, Any], float]:
        """Non-demolitional measurement of lepton"""
        if mode == MeasurementMode.COPY_ONLY:
            polarization_copy = copy.deepcopy(lepton.polarization_vector)
            measured_data = {
                'coherence_factor': polarization_copy.coherence_factor,
                'phase_angle': polarization_copy.phase_angle,
                'entropy': polarization_copy.get_entropy(),
                'effective_mass': lepton.effective_mass,
                'measurement_method': 'copy'
            }
            return measured_data, 0.001
        else:
            measured_data = {
                'coherence_estimate': lepton.polarization_vector.coherence_factor * 0.99,
                'phase_estimate': lepton.polarization_vector.phase_angle,
                'energy_estimate': lepton.energy,
                'measurement_method': mode.value
            }
            return measured_data, 0.005

    def _measure_lepton_classical(self, lepton: LeptonPhaseSpace) -> Tuple[Dict[str, Any], float]:
        """Classical measurement of lepton (may cause collapse)"""
        measurement_value, collapsed = lepton.polarization_vector.measure_polarization("z")
        measured_data = {
            'polarization_measurement': measurement_value,
            'collapsed': collapsed,
            'coherence_after': lepton.polarization_vector.coherence_factor,
            'measurement_method': 'classical'
        }
        disturbance = 0.5 if collapsed else 0.1
        return measured_data, disturbance
    
    def _update_preservation_rate(self):
        """Update state preservation rate"""
        if self.total_measurements > 0:
            self.state_preservation_rate = self.successful_ndm_count / self.total_measurements

# Export engine components
__all__ = [
    'NonDemolitionalMeasurementUnit'
]
