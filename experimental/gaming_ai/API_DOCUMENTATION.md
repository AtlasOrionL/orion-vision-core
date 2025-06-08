# 🔗 **GAMING AI API DOCUMENTATION**

**RESTful API for Gaming AI System**  
**Version**: 2.0  
**Base URL**: `http://localhost:8080`  

---

## 📋 **API OVERVIEW**

### **Available Endpoints**
- **System Status**: `/api/status` - Get system status
- **Testing**: `/api/test/{test_type}` - Run system tests
- **Game Optimization**: `/api/gaming/optimize` - Optimize game settings
- **AI Assistant**: `/api/ai/ask` - Ask AI for gaming advice
- **Team Management**: `/api/team/*` - Multi-agent team coordination
- **WebSocket**: `/ws` - Real-time updates

---

## 🔍 **SYSTEM STATUS API**

### **GET /api/status**
Get current system status and health metrics.

#### **Response**
```json
{
  "gaming_ai_status": "operational",
  "ollama_status": "connected", 
  "performance_monitor_status": "active",
  "last_updated": "2024-01-15T10:30:00Z",
  "system_health": "excellent"
}
```

#### **Status Values**
- `operational` - System working normally
- `degraded` - Partial functionality
- `error` - System issues detected
- `offline` - Service unavailable

---

## 🧪 **TESTING API**

### **POST /api/test/{test_type}**
Execute system tests for validation.

#### **Parameters**
- `test_type` (path): Test type to execute
  - `gaming_ai_core` - Core gaming AI functionality
  - `ollama_connection` - AI model connectivity
  - `performance_monitor` - Monitoring systems

#### **Request Example**
```bash
curl -X POST http://localhost:8080/api/test/gaming_ai_core
```

#### **Response**
```json
{
  "test_id": "gaming_ai_core_1642248600",
  "status": "started",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🎮 **GAME OPTIMIZATION API**

### **POST /api/gaming/optimize**
Optimize game settings for improved performance.

#### **Request Body**
```json
{
  "game_type": "CS:GO",
  "parameters": {
    "aim_sensitivity": 2.5,
    "crosshair_style": 4,
    "fps_target": 144,
    "fov": 103,
    "mouse_dpi": 800
  }
}
```

#### **Response**
```json
{
  "success": true,
  "optimizations_applied": 5,
  "details": {
    "game_type": "CS:GO",
    "parameters_applied": {
      "aim_sensitivity": 2.5,
      "crosshair_style": 4,
      "fps_target": 144
    },
    "fps_improvement": "15-20%",
    "latency_reduction": "5-10ms",
    "optimization_score": 95.5
  },
  "message": "CS:GO optimization completed successfully!"
}
```

#### **Error Response**
```json
{
  "success": false,
  "error": "Invalid game type specified"
}
```

---

## 🤖 **AI ASSISTANT API**

### **POST /api/ai/ask**
Ask AI for gaming advice and recommendations.

#### **Request Body**
```json
{
  "question": "How can I improve my CS:GO aim?"
}
```

#### **Response**
```json
{
  "success": true,
  "response": "🎯 For better aim: Lower your sensitivity (1.5-3.0), practice crosshair placement, use aim trainers daily, and ensure stable FPS (144+ recommended).",
  "question": "How can I improve my CS:GO aim?"
}
```

#### **AI Response Categories**
- **Aim improvement** (`aim` keyword)
- **FPS optimization** (`fps` keyword)
- **Settings optimization** (`settings` keyword)
- **CS:GO specific** (`csgo` keyword)
- **VALORANT specific** (`valorant` keyword)
- **Performance enhancement** (`performance` keyword)

---

## 👥 **TEAM MANAGEMENT API**

### **POST /api/team/create**
Create a new AI agent team.

#### **Response**
```json
{
  "success": true,
  "team_id": "team_1642248600",
  "max_agents": 8,
  "created_at": 1642248600
}
```

### **POST /api/team/add_agent**
Add an agent to the team.

#### **Request Body**
```json
{
  "agent_type": "gaming_assistant",
  "capabilities": ["game_optimization", "strategy_advice"]
}
```

#### **Response**
```json
{
  "success": true,
  "agent_id": "agent_1642248600",
  "agent_type": "gaming_assistant",
  "capabilities": ["game_optimization", "strategy_advice"]
}
```

### **POST /api/team/start_coordination**
Start team coordination.

#### **Response**
```json
{
  "success": true,
  "active_agents": 3,
  "coordination_mode": "gaming_optimization",
  "status": "active"
}
```

### **GET /api/team/status**
Get current team status.

#### **Response**
```json
{
  "success": true,
  "total_agents": 3,
  "active_agents": 3,
  "coordination_status": "active",
  "performance": "optimal",
  "current_task": "game_optimization"
}
```

---

## 🔌 **WEBSOCKET API**

### **WebSocket /ws**
Real-time updates and live data streaming.

#### **Connection**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onopen = function(event) {
    console.log('Connected to Gaming AI Dashboard');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received update:', data);
};
```

#### **Message Types**
- **System Status Updates**: Real-time system health
- **Test Results**: Live test execution results
- **Performance Metrics**: Real-time performance data
- **Error Notifications**: System error alerts

#### **Example Messages**
```json
{
  "type": "test_result",
  "test_id": "gaming_ai_core_1642248600",
  "status": "completed",
  "result": "success",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

```json
{
  "type": "performance_update",
  "metrics": {
    "aim_accuracy": 85,
    "reaction_time": 175,
    "fps": 144
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 📊 **ERROR HANDLING**

### **HTTP Status Codes**
- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **404 Not Found**: Endpoint not found
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

### **Error Response Format**
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### **Common Error Codes**
- `INVALID_GAME_TYPE`: Unsupported game type
- `INVALID_PARAMETERS`: Invalid optimization parameters
- `AI_SERVICE_UNAVAILABLE`: AI service not available
- `TEAM_CREATION_FAILED`: Team creation error
- `TEST_EXECUTION_FAILED`: Test execution error

---

## 🔧 **RATE LIMITING**

### **Limits**
- **General API**: 100 requests/minute
- **AI Assistant**: 20 requests/minute
- **Game Optimization**: 10 requests/minute
- **WebSocket**: No limit (connection-based)

### **Rate Limit Headers**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248660
```

---

## 🔐 **AUTHENTICATION**

### **Current Status**
- **Development Mode**: No authentication required
- **Production Mode**: API key authentication (planned)

### **Future Authentication**
```bash
# API Key in header (planned)
curl -H "X-API-Key: your-api-key" http://localhost:8080/api/status
```

---

## 📝 **EXAMPLES**

### **Complete Workflow Example**
```bash
# 1. Check system status
curl http://localhost:8080/api/status

# 2. Run system test
curl -X POST http://localhost:8080/api/test/gaming_ai_core

# 3. Optimize game settings
curl -X POST http://localhost:8080/api/gaming/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "game_type": "CS:GO",
    "parameters": {
      "aim_sensitivity": 2.5,
      "fps_target": 144
    }
  }'

# 4. Ask AI for advice
curl -X POST http://localhost:8080/api/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "How to improve aim?"}'

# 5. Create and manage team
curl -X POST http://localhost:8080/api/team/create
curl -X POST http://localhost:8080/api/team/add_agent \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "gaming_assistant",
    "capabilities": ["game_optimization"]
  }'
```

### **JavaScript Integration**
```javascript
class GamingAIClient {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
    }

    async optimizeGame(gameType, parameters) {
        const response = await fetch(`${this.baseUrl}/api/gaming/optimize`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ game_type: gameType, parameters })
        });
        return response.json();
    }

    async askAI(question) {
        const response = await fetch(`${this.baseUrl}/api/ai/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question })
        });
        return response.json();
    }
}

// Usage
const client = new GamingAIClient();
const result = await client.optimizeGame('CS:GO', {
    aim_sensitivity: 2.5,
    fps_target: 144
});
```

---

**🔗 Gaming AI API - Powerful, Fast, Reliable**

*RESTful API for next-generation gaming intelligence* ⚡
