# 🔌 Gaming AI API Documentation

Complete API reference for Gaming AI system.

## Base URL
```
http://localhost:8080
```

## Authentication
Currently using development mode. Production deployment will include JWT authentication.

## Core API Endpoints

### System Status
```http
GET /api/status
```

**Response:**
```json
{
  "api_version": "1.0.0",
  "features_available": true,
  "ollama_available": true,
  "active_features": ["game_optimization", "team_behaviors"],
  "feature_states": {...},
  "metrics": {...}
}
```

### Test Execution
```http
POST /api/test/{test_type}
```

**Parameters:**
- `test_type`: gaming_ai_core, ollama_connection, performance_monitor

**Response:**
```json
{
  "test_id": "test_123456",
  "status": "started"
}
```

### Test Results
```http
GET /api/tests
```

**Response:**
```json
[
  {
    "test_id": "test_123456",
    "test_name": "gaming_ai_core",
    "status": "success",
    "duration": 0.123,
    "timestamp": 1234567890.0,
    "details": {...}
  }
]
```

## Game Optimization API

### Detect Game
```http
POST /api/game/detect
```

**Request Body:**
```json
{
  "process_name": "csgo.exe",
  "window_title": "Counter-Strike: Global Offensive"
}
```

### Apply Optimizations
```http
POST /api/game/optimize
```

**Request Body:**
```json
{
  "game_type": "csgo",
  "optimization_level": "competitive"
}
```

## Performance Monitoring API

### Start Monitoring
```http
POST /api/performance/start
```

### Get Current Performance
```http
GET /api/performance/current
```

**Response:**
```json
{
  "current_performance": {
    "cpu_usage": {"value": 45.2, "unit": "%"},
    "memory_usage": {"value": 8192, "unit": "MB"},
    "gpu_usage": {"value": 78.5, "unit": "%"}
  }
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');
```

### Message Types
```json
{
  "type": "status_update",
  "timestamp": 1234567890.0,
  "system_status": {...},
  "running_tests": 0,
  "recent_tests": [...]
}
```

## Error Handling

### Error Response Format
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "timestamp": 1234567890.0
}
```

### HTTP Status Codes
- `200`: Success
- `400`: Bad Request
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting
- 100 requests per minute per IP
- WebSocket connections: 10 per IP

## Examples

### Python Client
```python
import requests

# Get system status
response = requests.get('http://localhost:8080/api/status')
status = response.json()

# Run test
response = requests.post('http://localhost:8080/api/test/gaming_ai_core')
test_result = response.json()
```

### JavaScript Client
```javascript
// Fetch system status
fetch('/api/status')
  .then(response => response.json())
  .then(data => console.log(data));

// WebSocket connection
const ws = new WebSocket('ws://localhost:8080/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```
