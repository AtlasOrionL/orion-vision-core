#!/usr/bin/env python3
"""
Simple test server for Orion Vision Core dashboard testing
"""

import json
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Mock data
mock_agents = [
    {
        "agent_id": "comm_agent_1",
        "config": {
            "name": "Communication Agent 1",
            "description": "Handles inter-agent communication"
        },
        "status": "running",
        "metrics": {
            "uptime": 3600,
            "messages_processed": 150,
            "llm_calls": 25
        }
    },
    {
        "agent_id": "task_orchestrator",
        "config": {
            "name": "Task Orchestrator",
            "description": "Manages and distributes tasks"
        },
        "status": "running",
        "metrics": {
            "uptime": 3500,
            "messages_processed": 89,
            "llm_calls": 12
        }
    }
]

class OrionTestHandler(BaseHTTPRequestHandler):
    """Root endpoint"""
    global request_count
    request_count += 1

    return {
        "message": "🚀 Orion Vision Core - Hybrid Local Deployment",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round(time.time() - start_time, 2),
        "request_count": request_count
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    global request_count
    request_count += 1

    return {
        "status": "healthy",
        "service": "orion-python-core-test",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": round(time.time() - start_time, 2)
    }

@app.get("/status")
def status():
    """Detailed status endpoint"""
    global request_count
    request_count += 1

    return {
        "status": "running",
        "service": "orion-python-core-test",
        "environment": {
            "rabbitmq_host": os.getenv('RABBITMQ_HOST', 'localhost'),
            "rabbitmq_port": os.getenv('RABBITMQ_PORT', '5672'),
            "python_version": os.sys.version,
            "working_directory": os.getcwd()
        },
        "metrics": {
            "start_time": start_time,
            "uptime_seconds": round(time.time() - start_time, 2),
            "request_count": request_count
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test-rabbitmq")
def test_rabbitmq():
    """Test RabbitMQ connection"""
    global request_count
    request_count += 1

    try:
        import pika

        # Try to connect to RabbitMQ
        connection_params = pika.ConnectionParameters(
            host=os.getenv('RABBITMQ_HOST', 'localhost'),
            port=int(os.getenv('RABBITMQ_PORT', 5672)),
            virtual_host='/',
            credentials=pika.PlainCredentials('guest', 'guest')
        )

        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()

        # Test queue
        queue_name = "orion_test_queue"
        channel.queue_declare(queue=queue_name, durable=False)

        # Send test message
        test_message = {
            "test": "deployment_validation",
            "timestamp": datetime.now().isoformat(),
            "source": "python-test-server"
        }

        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(test_message)
        )

        connection.close()

        return {
            "status": "success",
            "message": "RabbitMQ connection successful",
            "queue": queue_name,
            "test_message": test_message
        }

    except ImportError:
        return {
            "status": "error",
            "message": "pika library not installed",
            "suggestion": "pip install pika"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"RabbitMQ connection failed: {str(e)}",
            "rabbitmq_host": os.getenv('RABBITMQ_HOST', 'localhost'),
            "rabbitmq_port": os.getenv('RABBITMQ_PORT', '5672')
        }

@app.post("/api/message")
def handle_message(message_data: dict):
    """Handle incoming messages (bridge simulation)"""
    global request_count
    request_count += 1

    return {
        "status": "received",
        "message": "Message processed successfully",
        "received_data": message_data,
        "processed_at": datetime.now().isoformat(),
        "processor": "python-test-server"
    }

@app.get("/api/agents")
def list_agents():
    """List available agents (mock)"""
    global request_count
    request_count += 1

    mock_agents = [
        {
            "id": "test_agent_1",
            "name": "Test Agent 1",
            "status": "running",
            "type": "communication"
        },
        {
            "id": "test_agent_2",
            "name": "Test Agent 2",
            "status": "running",
            "type": "llm_router"
        }
    ]

    return {
        "agents": mock_agents,
        "count": len(mock_agents),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Orion Vision Core Test Server...")
    print("📊 Endpoints:")
    print("   • Health: http://localhost:8001/health")
    print("   • Status: http://localhost:8001/status")
    print("   • RabbitMQ Test: http://localhost:8001/test-rabbitmq")
    print("   • API Docs: http://localhost:8001/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
