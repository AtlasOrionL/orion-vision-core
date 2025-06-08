#!/usr/bin/env python3
"""
✅ Gaming AI Production Readiness Validator

Validates that Gaming AI system is ready for production deployment.
Checks all components, configurations, and dependencies.

Author: Nexus - Quantum AI Architect
Module: Production Validator
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path
import subprocess

class ProductionValidator:
    """
    Production readiness validator
    
    Features:
    - File structure validation
    - Configuration validation
    - Docker setup validation
    - Documentation validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ProductionValidator")
        self.validation_results = []
        self.errors = []
        self.warnings = []
        
        self.logger.info("✅ Production Validator initialized")
    
    def validate_file_structure(self) -> bool:
        """Validate required file structure"""
        self.logger.info("📁 Validating file structure...")
        
        required_files = [
            "Dockerfile",
            "docker-compose.yml",
            "requirements.txt",
            "deploy.sh",
            "generate_docs.py",
            "debug_dashboard_core.py",
            "unified_gaming_ai_api.py"
        ]
        
        required_dirs = [
            "docs",
            "docker",
            "docker/nginx",
            "docker/grafana"
        ]
        
        missing_files = []
        missing_dirs = []
        
        # Check files
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        # Check directories
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_files:
            self.errors.append(f"Missing required files: {missing_files}")
        
        if missing_dirs:
            self.errors.append(f"Missing required directories: {missing_dirs}")
        
        success = len(missing_files) == 0 and len(missing_dirs) == 0
        self.validation_results.append(("File Structure", success))
        
        if success:
            self.logger.info("✅ File structure validation passed")
        else:
            self.logger.error("❌ File structure validation failed")
        
        return success
    
    def validate_docker_config(self) -> bool:
        """Validate Docker configuration"""
        self.logger.info("🐳 Validating Docker configuration...")
        
        success = True
        
        # Check Dockerfile
        dockerfile_path = Path("Dockerfile")
        if dockerfile_path.exists():
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()
                
            required_dockerfile_elements = [
                "FROM python:",
                "WORKDIR",
                "COPY requirements.txt",
                "RUN pip install",
                "EXPOSE",
                "CMD"
            ]
            
            for element in required_dockerfile_elements:
                if element not in dockerfile_content:
                    self.errors.append(f"Dockerfile missing: {element}")
                    success = False
        else:
            self.errors.append("Dockerfile not found")
            success = False
        
        # Check docker-compose.yml
        compose_path = Path("docker-compose.yml")
        if compose_path.exists():
            with open(compose_path, 'r') as f:
                compose_content = f.read()
                
            required_services = [
                "gaming-ai-core",
                "ollama",
                "redis",
                "postgres",
                "prometheus",
                "grafana"
            ]
            
            for service in required_services:
                if service not in compose_content:
                    self.warnings.append(f"Docker Compose missing service: {service}")
        else:
            self.errors.append("docker-compose.yml not found")
            success = False
        
        self.validation_results.append(("Docker Configuration", success))
        
        if success:
            self.logger.info("✅ Docker configuration validation passed")
        else:
            self.logger.error("❌ Docker configuration validation failed")
        
        return success
    
    def validate_requirements(self) -> bool:
        """Validate requirements.txt"""
        self.logger.info("📦 Validating requirements...")
        
        requirements_path = Path("requirements.txt")
        if not requirements_path.exists():
            self.errors.append("requirements.txt not found")
            self.validation_results.append(("Requirements", False))
            return False
        
        with open(requirements_path, 'r') as f:
            requirements_content = f.read()
        
        critical_packages = [
            "fastapi",
            "uvicorn",
            "requests",
            "numpy",
            "psutil"
        ]
        
        missing_packages = []
        for package in critical_packages:
            if package not in requirements_content.lower():
                missing_packages.append(package)
        
        success = len(missing_packages) == 0
        
        if missing_packages:
            self.errors.append(f"Missing critical packages: {missing_packages}")
        
        self.validation_results.append(("Requirements", success))
        
        if success:
            self.logger.info("✅ Requirements validation passed")
        else:
            self.logger.error("❌ Requirements validation failed")
        
        return success
    
    def validate_documentation(self) -> bool:
        """Validate documentation"""
        self.logger.info("📚 Validating documentation...")
        
        docs_dir = Path("docs")
        if not docs_dir.exists():
            self.errors.append("docs/ directory not found")
            self.validation_results.append(("Documentation", False))
            return False
        
        required_docs = [
            "docs/README.md",
            "docs/API.md",
            "docs/DEPLOYMENT.md",
            "docs/index.md"
        ]
        
        missing_docs = []
        for doc_path in required_docs:
            if not Path(doc_path).exists():
                missing_docs.append(doc_path)
        
        success = len(missing_docs) == 0
        
        if missing_docs:
            self.errors.append(f"Missing documentation: {missing_docs}")
        
        self.validation_results.append(("Documentation", success))
        
        if success:
            self.logger.info("✅ Documentation validation passed")
        else:
            self.logger.error("❌ Documentation validation failed")
        
        return success
    
    def validate_scripts(self) -> bool:
        """Validate deployment scripts"""
        self.logger.info("🚀 Validating deployment scripts...")
        
        deploy_script = Path("deploy.sh")
        if not deploy_script.exists():
            self.errors.append("deploy.sh not found")
            self.validation_results.append(("Scripts", False))
            return False
        
        # Check if script is executable
        if not os.access(deploy_script, os.X_OK):
            self.warnings.append("deploy.sh is not executable (run: chmod +x deploy.sh)")
        
        # Check script content
        with open(deploy_script, 'r') as f:
            script_content = f.read()
        
        required_functions = [
            "check_prerequisites",
            "deploy",
            "stop",
            "restart",
            "backup",
            "check_health"
        ]
        
        missing_functions = []
        for func in required_functions:
            if func not in script_content:
                missing_functions.append(func)
        
        success = len(missing_functions) == 0
        
        if missing_functions:
            self.errors.append(f"deploy.sh missing functions: {missing_functions}")
        
        self.validation_results.append(("Scripts", success))
        
        if success:
            self.logger.info("✅ Scripts validation passed")
        else:
            self.logger.error("❌ Scripts validation failed")
        
        return success
    
    def validate_core_modules(self) -> bool:
        """Validate core Gaming AI modules"""
        self.logger.info("🎮 Validating core modules...")
        
        core_modules = [
            "unified_gaming_ai_api.py",
            "debug_dashboard_core.py",
            "game_optimizations.py",
            "performance_monitor.py",
            "multi_agent_coordinator.py",
            "team_behaviors.py"
        ]
        
        missing_modules = []
        for module in core_modules:
            if not Path(module).exists():
                missing_modules.append(module)
        
        success = len(missing_modules) == 0
        
        if missing_modules:
            self.errors.append(f"Missing core modules: {missing_modules}")
        
        self.validation_results.append(("Core Modules", success))
        
        if success:
            self.logger.info("✅ Core modules validation passed")
        else:
            self.logger.error("❌ Core modules validation failed")
        
        return success
    
    def run_comprehensive_validation(self) -> Tuple[bool, Dict[str, Any]]:
        """Run comprehensive production validation"""
        self.logger.info("🔍 Starting comprehensive production validation...")
        
        # Run all validations
        validations = [
            self.validate_file_structure(),
            self.validate_docker_config(),
            self.validate_requirements(),
            self.validate_documentation(),
            self.validate_scripts(),
            self.validate_core_modules()
        ]
        
        # Calculate results
        total_validations = len(validations)
        passed_validations = sum(validations)
        success_rate = (passed_validations / total_validations) * 100
        
        overall_success = all(validations)
        
        # Generate report
        report = {
            "overall_success": overall_success,
            "success_rate": success_rate,
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": total_validations - passed_validations,
            "validation_results": self.validation_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "production_ready": overall_success and len(self.errors) == 0
        }
        
        # Log summary
        if overall_success:
            self.logger.info(f"🎉 Production validation PASSED ({success_rate:.1f}%)")
        else:
            self.logger.error(f"❌ Production validation FAILED ({success_rate:.1f}%)")
        
        return overall_success, report
    
    def generate_validation_report(self, report: Dict[str, Any]) -> str:
        """Generate detailed validation report"""
        report_content = f"""# 🔍 Gaming AI Production Readiness Report

## 📊 Validation Summary

- **Overall Status**: {'✅ PASSED' if report['overall_success'] else '❌ FAILED'}
- **Success Rate**: {report['success_rate']:.1f}%
- **Validations Passed**: {report['passed_validations']}/{report['total_validations']}
- **Production Ready**: {'✅ YES' if report['production_ready'] else '❌ NO'}

## 📋 Detailed Results

"""
        
        for validation_name, success in report['validation_results']:
            status = "✅ PASSED" if success else "❌ FAILED"
            report_content += f"- **{validation_name}**: {status}\n"
        
        if report['errors']:
            report_content += "\n## ❌ Errors\n\n"
            for error in report['errors']:
                report_content += f"- {error}\n"
        
        if report['warnings']:
            report_content += "\n## ⚠️ Warnings\n\n"
            for warning in report['warnings']:
                report_content += f"- {warning}\n"
        
        report_content += f"""
## 🚀 Next Steps

{'### ✅ Ready for Production' if report['production_ready'] else '### ❌ Fix Issues Before Production'}

"""
        
        if report['production_ready']:
            report_content += """
Your Gaming AI system is ready for production deployment!

**Deployment Commands:**
```bash
# Deploy to production
./deploy.sh deploy

# Check status
./deploy.sh status

# Monitor logs
./deploy.sh logs
```

**Access Points:**
- Dashboard: http://localhost:8080
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
"""
        else:
            report_content += """
Please fix the errors listed above before deploying to production.

**Common Fixes:**
1. Ensure all required files are present
2. Check Docker configuration
3. Verify requirements.txt
4. Generate missing documentation
5. Make scripts executable: `chmod +x deploy.sh`
"""
        
        # Save report
        report_path = Path("PRODUCTION_READINESS_REPORT.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"📄 Validation report saved: {report_path}")
        return str(report_path)

# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run validation
    validator = ProductionValidator()
    success, report = validator.run_comprehensive_validation()
    
    # Generate report
    report_path = validator.generate_validation_report(report)
    
    print("\n🔍 PRODUCTION READINESS VALIDATION")
    print("=" * 50)
    
    for validation_name, validation_success in report['validation_results']:
        status = "✅ PASSED" if validation_success else "❌ FAILED"
        print(f"{status} {validation_name}")
    
    print(f"\n📊 Overall: {report['passed_validations']}/{report['total_validations']} validations passed")
    print(f"🎯 Success Rate: {report['success_rate']:.1f}%")
    print(f"🚀 Production Ready: {'YES' if report['production_ready'] else 'NO'}")
    
    if report['errors']:
        print(f"\n❌ Errors: {len(report['errors'])}")
        for error in report['errors']:
            print(f"  - {error}")
    
    if report['warnings']:
        print(f"\n⚠️ Warnings: {len(report['warnings'])}")
        for warning in report['warnings']:
            print(f"  - {warning}")
    
    print(f"\n📄 Detailed report: {report_path}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
