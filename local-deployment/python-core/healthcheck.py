#!/usr/bin/env python3
"""
Health Check Script for Python Core
Orion Vision Core - Phase 3 Hybrid Local Deployment
"""

import sys
import requests
import time
import os
import json
from typing import Dict, Any

def check_api_health() -> bool:
    """Check if the main API is responding"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_rabbitmq_connection() -> bool:
    """Check RabbitMQ connection"""
    try:
        import pika
        
        host = os.getenv('RABBITMQ_HOST', 'localhost')
        port = int(os.getenv('RABBITMQ_PORT', 5672))
        user = os.getenv('RABBITMQ_USER', 'guest')
        password = os.getenv('RABBITMQ_PASS', 'guest')
        
        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials,
            connection_attempts=1,
            retry_delay=1
        )
        
        connection = pika.BlockingConnection(parameters)
        connection.close()
        return True
    except:
        return False

def check_ollama_connection() -> bool:
    """Check Ollama LLM connection"""
    try:
        ollama_host = os.getenv('OLLAMA_HOST', 'localhost')
        ollama_port = os.getenv('OLLAMA_PORT', '11434')
        
        response = requests.get(
            f"http://{ollama_host}:{ollama_port}/api/tags",
            timeout=5
        )
        return response.status_code == 200
    except:
        return False

def check_disk_space() -> bool:
    """Check available disk space"""
    try:
        import shutil
        
        total, used, free = shutil.disk_usage("/app")
        free_gb = free // (1024**3)
        
        # Require at least 1GB free space
        return free_gb >= 1
    except:
        return False

def check_memory_usage() -> bool:
    """Check memory usage"""
    try:
        import psutil
        
        memory = psutil.virtual_memory()
        # Fail if memory usage is above 90%
        return memory.percent < 90
    except:
        return True  # If psutil not available, assume OK

def check_agent_registry() -> bool:
    """Check if agent registry file is accessible"""
    try:
        registry_file = "/app/data/agent_registry.json"
        
        # Create if doesn't exist
        if not os.path.exists(registry_file):
            os.makedirs(os.path.dirname(registry_file), exist_ok=True)
            with open(registry_file, 'w') as f:
                json.dump({}, f)
        
        # Test read/write
        with open(registry_file, 'r') as f:
            data = json.load(f)
        
        return True
    except:
        return False

def run_health_checks() -> Dict[str, Any]:
    """Run all health checks"""
    checks = {
        "api": check_api_health(),
        "rabbitmq": check_rabbitmq_connection(),
        "ollama": check_ollama_connection(),
        "disk_space": check_disk_space(),
        "memory": check_memory_usage(),
        "agent_registry": check_agent_registry()
    }
    
    # Overall health
    all_critical_ok = checks["api"] and checks["agent_registry"]
    
    return {
        "healthy": all_critical_ok,
        "checks": checks,
        "timestamp": time.time()
    }

def main():
    """Main health check function"""
    try:
        # Wait a bit for services to start
        time.sleep(2)
        
        # Run checks
        result = run_health_checks()
        
        # Print result for debugging
        print(f"Health check result: {json.dumps(result, indent=2)}")
        
        # Exit with appropriate code
        if result["healthy"]:
            print("✅ Health check passed")
            sys.exit(0)
        else:
            print("❌ Health check failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
