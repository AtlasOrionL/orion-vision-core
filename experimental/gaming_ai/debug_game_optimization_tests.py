#!/usr/bin/env python3
"""
🎮 Gaming AI Debug Dashboard - Game Optimization Tests Module

Specialized testing module for game optimization features.
Provides detailed testing for VALORANT, CS:GO, and Fortnite optimizations.

Author: Nexus - Quantum AI Architect
Module: Game Optimization Tests
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

@dataclass
class GameOptimizationTestResult:
    """Game optimization test result"""
    test_id: str
    game_type: str
    optimization_type: str
    status: str  # success, failed, warning
    optimizations_applied: int
    execution_time: float
    details: Dict[str, Any]
    timestamp: float
    error_message: Optional[str] = None

class GameOptimizationTester:
    """
    Game optimization testing module
    
    Features:
    - Individual game optimizer testing
    - Comprehensive optimization testing
    - Performance impact analysis
    - Optimization validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger("GameOptimizationTester")
        self.test_results: List[GameOptimizationTestResult] = []
        
        # Import game optimizers (CS:GO focused)
        try:
            from game_optimizations import GameOptimizations, GameType
            from csgo_optimizer import CSGOOptimizer, CSGOWeapon, CSGOMap, CSGORole

            self.game_optimizations = GameOptimizations()
            self.csgo_optimizer = CSGOOptimizer()

            self.optimizers_available = True
            self.logger.info("✅ CS:GO optimizer loaded successfully")

        except ImportError as e:
            self.optimizers_available = False
            self.logger.error(f"❌ Game optimizers import failed: {e}")
    
    async def test_core_optimizations(self) -> GameOptimizationTestResult:
        """Test core optimization system"""
        test_id = f"core_opt_{int(time.time())}"
        start_time = time.time()

        try:
            if not self.optimizers_available:
                raise Exception("Game optimizers not available")

            # Test basic optimization summary
            summary = self.game_optimizations.get_optimization_summary()

            # Test game detection
            detected_game = self.game_optimizations.detect_game("csgo.exe", "Counter-Strike")

            # Test basic optimization application
            basic_optimizations = self.game_optimizations.apply_optimizations(detected_game)

            result = GameOptimizationTestResult(
                test_id=test_id,
                game_type="Core",
                optimization_type="basic",
                status="success",
                optimizations_applied=len(basic_optimizations),
                execution_time=time.time() - start_time,
                details={
                    "summary": summary,
                    "detected_game": detected_game.value,
                    "basic_optimizations": len(basic_optimizations),
                    "optimization_list": basic_optimizations
                },
                timestamp=time.time()
            )

        except Exception as e:
            result = GameOptimizationTestResult(
                test_id=test_id,
                game_type="Core",
                optimization_type="basic",
                status="failed",
                optimizations_applied=0,
                execution_time=time.time() - start_time,
                details={},
                timestamp=time.time(),
                error_message=str(e)
            )

        self.test_results.append(result)
        return result
    
    async def test_csgo_optimizations(self) -> GameOptimizationTestResult:
        """Test CS:GO optimizations"""
        test_id = f"csgo_opt_{int(time.time())}"
        start_time = time.time()
        
        try:
            if not self.optimizers_available:
                raise Exception("Game optimizers not available")
            
            from csgo_optimizer import CSGOWeapon, CSGOMap, CSGORole
            
            # Test weapon optimization
            weapon_results = {}
            test_weapons = [CSGOWeapon.AK47, CSGOWeapon.M4A4, CSGOWeapon.AWP]
            
            for weapon in test_weapons:
                weapon_opt = self.csgo_optimizer.optimize_for_weapon(weapon)
                weapon_results[weapon.value] = len(weapon_opt)
            
            # Test map optimization
            map_results = {}
            test_maps = [CSGOMap.DUST2, CSGOMap.MIRAGE, CSGOMap.INFERNO]
            
            for map_name in test_maps:
                map_opt = self.csgo_optimizer.optimize_for_map(map_name)
                map_results[map_name.value] = len(map_opt)
            
            # Test role optimization
            role_results = {}
            test_roles = [CSGORole.ENTRY_FRAGGER, CSGORole.AWP_PLAYER, CSGORole.SUPPORT]
            
            for role in test_roles:
                role_opt = self.csgo_optimizer.optimize_for_role(role)
                role_results[role.value] = len(role_opt)
            
            total_optimizations = sum(weapon_results.values()) + sum(map_results.values()) + sum(role_results.values())
            
            result = GameOptimizationTestResult(
                test_id=test_id,
                game_type="CS:GO",
                optimization_type="comprehensive",
                status="success",
                optimizations_applied=total_optimizations,
                execution_time=time.time() - start_time,
                details={
                    "weapon_optimizations": weapon_results,
                    "map_optimizations": map_results,
                    "role_optimizations": role_results,
                    "total_weapons_tested": len(test_weapons),
                    "total_maps_tested": len(test_maps),
                    "total_roles_tested": len(test_roles)
                },
                timestamp=time.time()
            )
            
        except Exception as e:
            result = GameOptimizationTestResult(
                test_id=test_id,
                game_type="CS:GO",
                optimization_type="comprehensive",
                status="failed",
                optimizations_applied=0,
                execution_time=time.time() - start_time,
                details={},
                timestamp=time.time(),
                error_message=str(e)
            )
        
        self.test_results.append(result)
        return result
    

    
    async def test_unified_game_optimizations(self) -> GameOptimizationTestResult:
        """Test unified game optimization system (CS:GO focused)"""
        test_id = f"unified_opt_{int(time.time())}"
        start_time = time.time()

        try:
            if not self.optimizers_available:
                raise Exception("Game optimizers not available")

            from game_optimizations import GameType

            # Test CS:GO detection and optimization
            detected = self.game_optimizations.detect_game("csgo.exe", "Counter-Strike: Global Offensive")

            # Test optimization application for CS:GO
            optimizations = self.game_optimizations.apply_optimizations(GameType.CSGO)

            # Test comprehensive optimizations for CS:GO
            comprehensive = self.game_optimizations.apply_comprehensive_optimizations(GameType.CSGO)

            total_optimizations = len(optimizations) + comprehensive.get("total_optimizations", 0)

            result = GameOptimizationTestResult(
                test_id=test_id,
                game_type="Unified",
                optimization_type="csgo_focused",
                status="success",
                optimizations_applied=total_optimizations,
                execution_time=time.time() - start_time,
                details={
                    "detected_game": detected.value,
                    "basic_optimizations": len(optimizations),
                    "comprehensive_optimizations": comprehensive.get("total_optimizations", 0),
                    "optimization_summary": comprehensive
                },
                timestamp=time.time()
            )

        except Exception as e:
            result = GameOptimizationTestResult(
                test_id=test_id,
                game_type="Unified",
                optimization_type="csgo_focused",
                status="failed",
                optimizations_applied=0,
                execution_time=time.time() - start_time,
                details={},
                timestamp=time.time(),
                error_message=str(e)
            )

        self.test_results.append(result)
        return result
    
    async def run_all_optimization_tests(self) -> List[GameOptimizationTestResult]:
        """Run all game optimization tests (CS:GO focused)"""
        self.logger.info("🎮 Starting CS:GO focused optimization tests...")

        results = []

        # Run core optimization test
        core_result = await self.test_core_optimizations()
        results.append(core_result)
        self.logger.info(f"✅ Core test: {core_result.status} ({core_result.optimizations_applied} optimizations)")

        # Run CS:GO specific test
        csgo_result = await self.test_csgo_optimizations()
        results.append(csgo_result)
        self.logger.info(f"✅ CS:GO test: {csgo_result.status} ({csgo_result.optimizations_applied} optimizations)")

        # Run unified system test
        unified_result = await self.test_unified_game_optimizations()
        results.append(unified_result)
        self.logger.info(f"✅ Unified test: {unified_result.status} ({unified_result.optimizations_applied} optimizations)")

        # Calculate summary
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.status == "success")
        total_optimizations = sum(r.optimizations_applied for r in results)

        self.logger.info(f"🎊 Game optimization tests completed: {successful_tests}/{total_tests} successful, {total_optimizations} total optimizations")

        return results
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get test summary statistics"""
        if not self.test_results:
            return {"message": "No tests run yet"}
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.status == "success")
        failed_tests = sum(1 for r in self.test_results if r.status == "failed")
        total_optimizations = sum(r.optimizations_applied for r in self.test_results)
        
        # Game-specific stats
        game_stats = {}
        for result in self.test_results:
            game = result.game_type
            if game not in game_stats:
                game_stats[game] = {"tests": 0, "optimizations": 0, "success_rate": 0}
            
            game_stats[game]["tests"] += 1
            game_stats[game]["optimizations"] += result.optimizations_applied
        
        # Calculate success rates
        for game in game_stats:
            game_tests = [r for r in self.test_results if r.game_type == game]
            successful = sum(1 for r in game_tests if r.status == "success")
            game_stats[game]["success_rate"] = (successful / len(game_tests)) * 100
        
        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / total_tests) * 100,
            "total_optimizations": total_optimizations,
            "game_statistics": game_stats,
            "recent_tests": [asdict(r) for r in self.test_results[-5:]]
        }

# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def main():
        tester = GameOptimizationTester()
        results = await tester.run_all_optimization_tests()
        
        print("\n🎮 GAME OPTIMIZATION TEST RESULTS")
        print("=" * 50)
        
        for result in results:
            status_icon = "✅" if result.status == "success" else "❌"
            print(f"{status_icon} {result.game_type}: {result.optimizations_applied} optimizations ({result.execution_time:.2f}s)")
        
        summary = tester.get_test_summary()
        print(f"\n📊 Summary: {summary['successful_tests']}/{summary['total_tests']} tests successful")
        print(f"🎯 Total optimizations: {summary['total_optimizations']}")
    
    asyncio.run(main())
