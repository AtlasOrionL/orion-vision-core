#!/usr/bin/env python3
"""
Clean Test Server for Orion Vision Core
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from datetime import datetime

app = FastAPI(
    title="Orion Vision Core - Clean Test Server",
    description="Simple test server for Python Core API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
start_time = time.time()
request_count = 0

@app.get("/")
def root():
    """Root endpoint"""
    global request_count
    request_count += 1
    
    return {
        "message": "🚀 Orion Vision Core - Python API",
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
        "service": "orion-python-core",
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
        "service": "orion-python-core",
        "metrics": {
            "start_time": start_time,
            "uptime_seconds": round(time.time() - start_time, 2),
            "request_count": request_count
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Orion Python Core Test Server...")
    print("📊 Health: http://localhost:8001/health")
    print("📊 Status: http://localhost:8001/status")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info"
    )
