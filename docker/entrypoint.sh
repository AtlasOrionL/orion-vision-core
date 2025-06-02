#!/bin/bash
# Orion Vision Core - Docker Entrypoint Script
# Sprint 4.3 - Production Deployment & Advanced Monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

# Environment variables with defaults
export ORION_ENV=${ORION_ENV:-production}
export ORION_LOG_LEVEL=${ORION_LOG_LEVEL:-INFO}
export ORION_HOST=${ORION_HOST:-0.0.0.0}
export ORION_PORT=${ORION_PORT:-8000}
export ORION_WORKERS=${ORION_WORKERS:-4}
export ORION_CONFIG_PATH=${ORION_CONFIG_PATH:-/app/config}
export ORION_DATA_PATH=${ORION_DATA_PATH:-/app/data}
export ORION_LOG_PATH=${ORION_LOG_PATH:-/app/logs}

# Service discovery settings
export ORION_DISCOVERY_ENABLED=${ORION_DISCOVERY_ENABLED:-true}
export ORION_DISCOVERY_HOST=${ORION_DISCOVERY_HOST:-localhost}
export ORION_DISCOVERY_PORT=${ORION_DISCOVERY_PORT:-8001}

# Task orchestration settings
export ORION_ORCHESTRATION_ENABLED=${ORION_ORCHESTRATION_ENABLED:-true}
export ORION_ORCHESTRATION_HOST=${ORION_ORCHESTRATION_HOST:-localhost}
export ORION_ORCHESTRATION_PORT=${ORION_ORCHESTRATION_PORT:-8002}

# Monitoring settings
export ORION_METRICS_ENABLED=${ORION_METRICS_ENABLED:-true}
export ORION_METRICS_PORT=${ORION_METRICS_PORT:-9090}
export ORION_HEALTH_CHECK_PORT=${ORION_HEALTH_CHECK_PORT:-9091}

# Database settings
export ORION_DB_TYPE=${ORION_DB_TYPE:-sqlite}
export ORION_DB_PATH=${ORION_DB_PATH:-/app/data/orion.db}

# Redis settings (for distributed caching)
export ORION_REDIS_ENABLED=${ORION_REDIS_ENABLED:-false}
export ORION_REDIS_HOST=${ORION_REDIS_HOST:-localhost}
export ORION_REDIS_PORT=${ORION_REDIS_PORT:-6379}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-30}
    
    log "Waiting for $service_name at $host:$port..."
    
    for i in $(seq 1 $timeout); do
        if nc -z "$host" "$port" 2>/dev/null; then
            success "$service_name is available"
            return 0
        fi
        sleep 1
    done
    
    error "$service_name is not available after ${timeout}s"
    return 1
}

# Function to check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    # Check Redis if enabled
    if [ "$ORION_REDIS_ENABLED" = "true" ]; then
        wait_for_service "$ORION_REDIS_HOST" "$ORION_REDIS_PORT" "Redis" 30
    fi
    
    # Check external services if configured
    if [ -n "$ORION_EXTERNAL_SERVICE_HOST" ]; then
        wait_for_service "$ORION_EXTERNAL_SERVICE_HOST" "$ORION_EXTERNAL_SERVICE_PORT" "External Service" 30
    fi
    
    success "All dependencies are available"
}

# Function to initialize application
initialize_app() {
    log "Initializing Orion Vision Core..."
    
    # Create necessary directories
    mkdir -p "$ORION_DATA_PATH" "$ORION_LOG_PATH"
    
    # Initialize database if needed
    if [ "$ORION_DB_TYPE" = "sqlite" ] && [ ! -f "$ORION_DB_PATH" ]; then
        log "Initializing SQLite database..."
        python -c "
import sqlite3
import os
os.makedirs(os.path.dirname('$ORION_DB_PATH'), exist_ok=True)
conn = sqlite3.connect('$ORION_DB_PATH')
conn.execute('CREATE TABLE IF NOT EXISTS health_check (id INTEGER PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
conn.commit()
conn.close()
print('Database initialized')
"
    fi
    
    # Set up logging configuration
    cat > "$ORION_LOG_PATH/logging.conf" << EOF
[loggers]
keys=root,orion

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_orion]
level=$ORION_LOG_LEVEL
handlers=consoleHandler,fileHandler
qualname=orion
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=$ORION_LOG_LEVEL
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=$ORION_LOG_LEVEL
formatter=simpleFormatter
args=('$ORION_LOG_PATH/orion.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
EOF
    
    success "Application initialized"
}

# Function to start service based on command
start_service() {
    local service=$1
    
    case $service in
        "agent-manager")
            log "Starting Orion Agent Manager..."
            exec python -m jobone.vision_core.agent_management_api \
                --host "$ORION_HOST" \
                --port "$ORION_PORT" \
                --workers "$ORION_WORKERS" \
                --config-path "$ORION_CONFIG_PATH"
            ;;
        "service-discovery")
            log "Starting Orion Service Discovery..."
            exec python -m jobone.vision_core.service_discovery \
                --host "$ORION_DISCOVERY_HOST" \
                --port "$ORION_DISCOVERY_PORT" \
                --config-path "$ORION_CONFIG_PATH"
            ;;
        "task-orchestration")
            log "Starting Orion Task Orchestration..."
            exec python -m jobone.vision_core.task_orchestration \
                --host "$ORION_ORCHESTRATION_HOST" \
                --port "$ORION_ORCHESTRATION_PORT" \
                --config-path "$ORION_CONFIG_PATH"
            ;;
        "all-in-one")
            log "Starting Orion All-in-One Service..."
            exec python -c "
import asyncio
import sys
sys.path.append('/app/src')

from jobone.vision_core.service_discovery import ServiceDiscoveryManager
from jobone.vision_core.task_orchestration import DistributedTaskOrchestrationManager
from jobone.vision_core.agent_management_api import create_app
import uvicorn

async def main():
    # Start service discovery
    discovery_manager = ServiceDiscoveryManager()
    await discovery_manager.start()
    
    # Start task orchestration
    orchestration_manager = DistributedTaskOrchestrationManager(discovery_manager)
    await orchestration_manager.start()
    
    # Start API server
    app = create_app(discovery_manager, orchestration_manager)
    config = uvicorn.Config(
        app, 
        host='$ORION_HOST', 
        port=$ORION_PORT, 
        workers=$ORION_WORKERS,
        log_level='$ORION_LOG_LEVEL'.lower()
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == '__main__':
    asyncio.run(main())
"
            ;;
        "health-check")
            log "Running health check..."
            exec python healthcheck.py
            ;;
        *)
            error "Unknown service: $service"
            echo "Available services: agent-manager, service-discovery, task-orchestration, all-in-one, health-check"
            exit 1
            ;;
    esac
}

# Function to handle shutdown
shutdown() {
    log "Shutting down Orion Vision Core..."
    # Add cleanup logic here if needed
    exit 0
}

# Trap signals
trap shutdown SIGTERM SIGINT

# Main execution
main() {
    log "Starting Orion Vision Core Container"
    log "Environment: $ORION_ENV"
    log "Log Level: $ORION_LOG_LEVEL"
    log "Host: $ORION_HOST:$ORION_PORT"
    
    # Check dependencies
    check_dependencies
    
    # Initialize application
    initialize_app
    
    # Get service to start
    service=${1:-agent-manager}
    
    # Start the requested service
    start_service "$service"
}

# Run main function with all arguments
main "$@"
