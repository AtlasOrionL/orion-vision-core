#!/usr/bin/env python3
"""
Orion Vision Core - Test Service
Simple FastAPI service for testing Docker deployment

Author: Orion Development Team
Version: 8.8.0
Date: 31 Mayıs 2025
"""

from fastapi import FastAPI
import uvicorn
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OrionTestService")

# Create FastAPI app
app = FastAPI(
    title="Orion Python Core Test",
    description="Simple test service for Orion Vision Core deployment",
    version="8.8.0"
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Orion Vision Core Test Service",
        "version": "8.8.0",
        "status": "running"
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "python-core-test",
        "version": "8.8.0"
    }

@app.get("/status")
def status():
    """Status endpoint with environment info"""
    return {
        "status": "running",
        "service": "orion-test-service",
        "version": "8.8.0",
        "rabbitmq_host": os.getenv("RABBITMQ_HOST", "localhost"),
        "rabbitmq_port": os.getenv("RABBITMQ_PORT", "5672"),
        "rabbitmq_user": os.getenv("RABBITMQ_USER", "orion"),
        "environment": "test",
        "python_version": os.sys.version
    }

@app.get("/test/rabbitmq")
def test_rabbitmq():
    """Test RabbitMQ connection"""
    try:
        import pika
        
        # RabbitMQ connection parameters
        host = os.getenv("RABBITMQ_HOST", "localhost")
        port = int(os.getenv("RABBITMQ_PORT", "5672"))
        user = os.getenv("RABBITMQ_USER", "orion")
        password = os.getenv("RABBITMQ_PASS", "orion123")
        
        # Create connection
        credentials = pika.PlainCredentials(user, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=credentials
        )
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # Test queue
        queue_name = "test_queue"
        channel.queue_declare(queue=queue_name, durable=True)
        
        # Send test message
        test_message = "Hello from Orion Test Service!"
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=test_message
        )
        
        connection.close()
        
        return {
            "status": "success",
            "message": "RabbitMQ connection successful",
            "host": host,
            "port": port,
            "test_message_sent": test_message
        }
        
    except Exception as e:
        logger.error(f"RabbitMQ connection failed: {e}")
        return {
            "status": "error",
            "message": f"RabbitMQ connection failed: {str(e)}",
            "host": os.getenv("RABBITMQ_HOST", "localhost"),
            "port": os.getenv("RABBITMQ_PORT", "5672")
        }

if __name__ == "__main__":
    logger.info("Starting Orion Test Service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
