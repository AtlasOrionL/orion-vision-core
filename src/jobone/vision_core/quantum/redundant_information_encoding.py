"""
🛡️ Redundant Information Encoding & Quorum Sensing - Q3.2 Main Module

Modular design following Q_TASK_ARCHITECTURE (300-line limit)
Main module importing core components and providing unified interface

Author: Orion Vision Core Team
Based on: Orion's Voice Q1-Q5 Advanced Specifications
Priority: CRITICAL - Modular Design Refactoring Phase 5
"""

# Import core components from modular design
from .redundant_copy_core import (
    EncodingType,
    RedundancyLevel,
    QuorumDecision,
    RedundantCopy,
    QuorumVote,
    create_redundant_copy,
    verify_copy_integrity
)

# Import encoder component
from .redundant_encoder import (
    RedundantInformationEncoder,
    create_redundant_information_encoder
)

# Import quorum sensing component
from .quorum_sensing import (
    QuorumSensingSystem,
    create_quorum_sensing_system
)

# Import base components for compatibility
from .planck_information_unit import PlanckInformationUnit
from .information_conservation_law import ZBosonTrigger

# Test function
def test_redundant_information_encoding():
    """Test Redundant Information Encoding & Quorum Sensing system"""
    print("🛡️ Testing Redundant Information Encoding & Quorum Sensing System...")
    
    # Create encoder and quorum system
    encoder = create_redundant_information_encoder(
        encoding_type=EncodingType.REPETITION_CODE,
        redundancy_level=RedundancyLevel.MEDIUM
    )
    quorum = create_quorum_sensing_system(
        decision_type=QuorumDecision.MAJORITY,
        minimum_votes=3
    )
    print("✅ Encoder and Quorum systems created")
    
    # Create test information unit
    from .planck_information_unit import create_planck_information_manager
    
    planck_manager = create_planck_information_manager()
    info_unit = planck_manager.create_unit(coherence_factor=0.8)
    
    print(f"✅ Test information unit created: {info_unit.quality.value}")
    
    # Encode with redundancy
    copies = encoder.encode_information_unit(info_unit)
    print(f"✅ Information unit encoded with {len(copies)} redundant copies")
    
    # Verify all copies
    verification_results = encoder.verify_all_copies(info_unit.unit_id)
    valid_count = sum(1 for result in verification_results.values() if result)
    print(f"✅ Copy verification: {valid_count}/{len(verification_results)} copies valid")
    
    # Test quorum voting
    vote_session_id = quorum.initiate_quorum_vote(info_unit.unit_id, copies)
    winning_hash, consensus, details = quorum.evaluate_quorum_decision(vote_session_id)
    
    print(f"✅ Quorum decision:")
    print(f"    - Consensus reached: {consensus}")
    print(f"    - Winning hash: {winning_hash[:8] if winning_hash else 'None'}...")
    print(f"    - Total votes: {details.get('total_votes', 0)}")
    
    # Test corruption simulation
    encoder.simulate_corruption(info_unit.unit_id, 0)
    print("✅ Corruption simulated in first copy")
    
    # Test recovery
    recovered_unit = encoder.recover_corrupted_unit(info_unit.unit_id)
    print(f"✅ Recovery test: {'Success' if recovered_unit else 'Failed'}")
    
    # Get statistics
    encoder_stats = encoder.get_encoding_statistics()
    quorum_stats = quorum.get_quorum_statistics()
    
    print(f"✅ System statistics:")
    print(f"    - Encoded units: {encoder_stats['total_encoded_units']}")
    print(f"    - Total copies: {encoder_stats['total_copies']}")
    print(f"    - Corruption rate: {encoder_stats['corruption_rate']:.1%}")
    print(f"    - Quorum sessions: {quorum_stats['completed_sessions']}")
    print(f"    - Consensus rate: {quorum_stats['consensus_rate']:.1%}")
    
    print("🚀 Redundant Information Encoding & Quorum Sensing test completed!")

# Export all components for backward compatibility
__all__ = [
    'EncodingType',
    'RedundancyLevel',
    'QuorumDecision',
    'RedundantCopy',
    'QuorumVote',
    'RedundantInformationEncoder',
    'QuorumSensingSystem',
    'create_redundant_copy',
    'verify_copy_integrity',
    'create_redundant_information_encoder',
    'create_quorum_sensing_system',
    'test_redundant_information_encoding'
]

if __name__ == "__main__":
    test_redundant_information_encoding()
