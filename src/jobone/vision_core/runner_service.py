import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import asyncio
import httpx
import subprocess
import os
import json
import time
from pathlib import Path

app = FastAPI(title="Orion Vision Core API", version="1.0.0")

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Görev Durumu Seçenekleri
TASK_STATES = ["pending", "running", "completed", "failed"]

# Ollama Configuration
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2:1b"

# Ollama Helper Functions
async def send_ollama_request(message: str, model: str = None) -> str:
    """Ollama'ya AI request gönder"""
    try:
        selected_model = model if model else DEFAULT_MODEL

        # Ollama API'ye request gönder
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": selected_model,
                    "prompt": message,
                    "stream": False
                }
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response from Ollama")
            else:
                raise Exception(f"Ollama API error: {response.status_code}")

    except Exception as e:
        logger.error(f"Ollama request failed: {e}")
        raise e

async def check_ollama_connection() -> bool:
    """Ollama bağlantısını kontrol et"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return response.status_code == 200
    except:
        return False

# Yeni API Modelleri
class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = "gpt-4"
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    model: str
    timestamp: str

class TerminalCommand(BaseModel):
    command: str
    workingDirectory: Optional[str] = None
    timeout: Optional[int] = 30

class TerminalResponse(BaseModel):
    output: str
    error: Optional[str] = None
    exitCode: int
    duration: float

class FileOperation(BaseModel):
    operation: str  # "read", "write", "create", "delete", "list"
    path: str
    content: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None

class FileResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    size: Optional[int] = None

# Task modeli
class Task(BaseModel):
    id: str
    description: str
    agent: str  # screen_agent, speech_agent, vb.
    status: str = "pending"
    result: Optional[dict] = None

# Basit Task Manager
class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, description: str, agent: str) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(id=task_id, description=description, agent=agent)
        self.tasks[task_id] = task
        return task

    def update_task(self, task_id: str, status: str, result: Optional[dict] = None):
        if task_id not in self.tasks:
            raise ValueError("Task not found")
        self.tasks[task_id].status = status
        if result:
            self.tasks[task_id].result = result

    def get_task(self, task_id: str) -> Task:
        task = self.tasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task

    def list_tasks(self) -> List[Task]:
        return list(self.tasks.values())

task_manager = TaskManager()

# Agent API çağrıları için soyutlama
class AgentInterface:
    agent_endpoints = {
        "screen_agent": "http://localhost:8001/capture_screen/",
        # Diğer agentlar buraya eklenecek
    }

    async def call_agent(self, agent: str, payload: dict):
        if agent not in self.agent_endpoints:
            raise ValueError("Unknown agent")
        url = self.agent_endpoints[agent]
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

agent_interface = AgentInterface()

@app.post("/tasks/")
async def create_and_run_task(description: str, agent: str):
    try:
        # Görev oluştur
        task = task_manager.create_task(description, agent)
        logger.info(f"Task created with id: {task.id}")

        # Görev durumunu running olarak güncelle
        task_manager.update_task(task.id, "running")
        logger.info(f"Task {task.id} status updated to running")

        # Agent'ı çağır ve sonucu al
        try:
            # Örnek: ekran görüntüsü için bölge bilgisi ya da boş gönderilebilir
            payload = {}
            result = await agent_interface.call_agent(agent, payload)
            task_manager.update_task(task.id, "completed", result)
            logger.info(f"Task {task.id} completed successfully")
        except Exception as e:
            task_manager.update_task(task.id, "failed", {"error": str(e)})
            logger.error(f"Task {task.id} failed: {e}")

        return task_manager.get_task(task.id)
    except Exception as e:
        logger.error(f"Failed to create and run task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/")
def list_all_tasks():
    try:
        tasks = task_manager.list_tasks()
        logger.info("Listing all tasks")
        return tasks
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    try:
        task = task_manager.get_task(task_id)
        logger.info(f"Getting task with id: {task_id}")
        return task
    except Exception as e:
        logger.error(f"Failed to get task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 💬 CHAT API ENDPOINTS
@app.post("/api/chat/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """AI Chat endpoint - VS Code extension'dan gelen mesajları işler"""
    try:
        conversation_id = request.conversation_id or str(uuid.uuid4())
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Ollama ile gerçek AI response al
        try:
            ollama_response = await send_ollama_request(request.message, request.model)
            ai_response = ollama_response
        except Exception as e:
            logger.warning(f"Ollama request failed, using fallback: {e}")
            ai_response = f"AI Response to: {request.message} (Model: {request.model}) [Fallback Mode]"

        logger.info(f"Chat message processed: {request.message[:50]}...")

        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            model=request.model,
            timestamp=timestamp
        )
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Chat geçmişini getir"""
    try:
        # Mock chat history
        history = [
            {"role": "user", "content": "Hello", "timestamp": "2024-01-01 10:00:00"},
            {"role": "assistant", "content": "Hi there!", "timestamp": "2024-01-01 10:00:01"}
        ]
        return {"conversation_id": conversation_id, "messages": history}
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 🖥️ TERMINAL API ENDPOINTS
@app.post("/api/terminal/execute", response_model=TerminalResponse)
async def execute_terminal_command(command_request: TerminalCommand):
    """Terminal komutlarını güvenli şekilde çalıştır"""
    try:
        start_time = time.time()
        working_dir = command_request.workingDirectory or os.getcwd()

        # Güvenlik kontrolü - tehlikeli komutları engelle
        dangerous_commands = ['rm -rf', 'sudo rm', 'format', 'del /f', 'shutdown']
        if any(dangerous in command_request.command.lower() for dangerous in dangerous_commands):
            raise HTTPException(status_code=403, detail="Dangerous command blocked")

        # Komutu çalıştır
        result = subprocess.run(
            command_request.command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=command_request.timeout
        )

        duration = time.time() - start_time

        logger.info(f"Terminal command executed: {command_request.command}")

        return TerminalResponse(
            output=result.stdout,
            error=result.stderr if result.stderr else None,
            exitCode=result.returncode,
            duration=duration
        )

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timeout")
    except Exception as e:
        logger.error(f"Terminal execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 📁 FILE SYSTEM API ENDPOINTS
@app.post("/api/filesystem/operation", response_model=FileResponse)
async def file_system_operation(operation: FileOperation):
    """Güvenli dosya sistemi işlemleri"""
    try:
        file_path = Path(operation.path)

        # Güvenlik kontrolü - sistem dosyalarını koru
        restricted_paths = ['/etc', '/sys', '/proc', '/dev', 'C:\\Windows', 'C:\\System32']
        if any(str(file_path).startswith(restricted) for restricted in restricted_paths):
            raise HTTPException(status_code=403, detail="Access to system files denied")

        if operation.operation == "read":
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")

            content = file_path.read_text(encoding='utf-8')
            size = file_path.stat().st_size

            logger.info(f"File read: {operation.path}")
            return FileResponse(success=True, content=content, size=size)

        elif operation.operation == "write":
            file_path.write_text(operation.content or "", encoding='utf-8')
            size = file_path.stat().st_size

            logger.info(f"File written: {operation.path}")
            return FileResponse(success=True, size=size)

        elif operation.operation == "create":
            if file_path.exists():
                raise HTTPException(status_code=409, detail="File already exists")

            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(operation.content or "", encoding='utf-8')
            size = file_path.stat().st_size

            logger.info(f"File created: {operation.path}")
            return FileResponse(success=True, size=size)

        elif operation.operation == "delete":
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")

            file_path.unlink()
            logger.info(f"File deleted: {operation.path}")
            return FileResponse(success=True)

        elif operation.operation == "list":
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Directory not found")

            if not file_path.is_dir():
                raise HTTPException(status_code=400, detail="Path is not a directory")

            files = []
            for item in file_path.iterdir():
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })

            logger.info(f"Directory listed: {operation.path}")
            return FileResponse(success=True, content=json.dumps(files))

        else:
            raise HTTPException(status_code=400, detail="Invalid operation")

    except Exception as e:
        logger.error(f"File system operation error: {e}")
        return FileResponse(success=False, error=str(e))

# 🔌 API PROVIDER ENDPOINTS
@app.get("/api/providers/list")
async def list_api_providers():
    """Mevcut API provider'ları listele"""
    try:
        # Ollama bağlantısını ve modellerini kontrol et
        ollama_connected = await check_ollama_connection()
        ollama_models = []

        if ollama_connected:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                    if response.status_code == 200:
                        data = response.json()
                        ollama_models = [model["name"] for model in data.get("models", [])]
            except:
                ollama_models = [DEFAULT_MODEL]  # Fallback

        providers = [
            {
                "id": "ollama-local",
                "name": "Ollama (Local)",
                "type": "ollama",
                "baseUrl": OLLAMA_BASE_URL,
                "isConnected": ollama_connected,
                "models": ollama_models if ollama_models else [DEFAULT_MODEL]
            },
            {
                "id": "openrouter",
                "name": "OpenRouter",
                "type": "openrouter",
                "baseUrl": "https://openrouter.ai/api/v1",
                "isConnected": False,
                "models": ["microsoft/wizardlm-2-8x22b", "meta-llama/llama-3-8b-instruct:free"]
            }
        ]
        return {"providers": providers}
    except Exception as e:
        logger.error(f"Provider list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/providers/test/{provider_id}")
async def test_api_provider(provider_id: str):
    """API provider bağlantısını test et"""
    try:
        if provider_id == "ollama-local":
            # Gerçek Ollama bağlantı testi
            is_connected = await check_ollama_connection()

            if is_connected:
                # Test mesajı gönder
                try:
                    test_response = await send_ollama_request("Test message", DEFAULT_MODEL)
                    message = f"Connection successful. Test response: {test_response[:50]}..."
                except Exception as e:
                    is_connected = False
                    message = f"Connection failed during test: {str(e)}"
            else:
                message = "Ollama server not reachable"
        else:
            # Diğer provider'lar için mock test
            is_connected = False
            message = "Provider not implemented yet"

        logger.info(f"Provider test: {provider_id} - {'Connected' if is_connected else 'Failed'}")

        return {
            "provider_id": provider_id,
            "connected": is_connected,
            "message": message
        }
    except Exception as e:
        logger.error(f"Provider test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 🏥 HEALTH CHECK & SYSTEM INFO
@app.get("/api/health")
async def health_check():
    """System health check"""
    try:
        # Ollama bağlantısını kontrol et
        ollama_status = await check_ollama_connection()

        return {
            "status": "healthy",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0.0",
            "services": {
                "chat": "active",
                "terminal": "active",
                "filesystem": "active",
                "providers": "active",
                "ollama": "connected" if ollama_status else "disconnected"
            },
            "ollama": {
                "url": OLLAMA_BASE_URL,
                "default_model": DEFAULT_MODEL,
                "connected": ollama_status
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/system/info")
async def get_system_info():
    """System bilgilerini getir"""
    try:
        import platform
        import psutil

        return {
            "system": {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "python_version": platform.python_version()
            },
            "resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent if platform.system() != 'Windows' else psutil.disk_usage('C:').percent
            },
            "orion": {
                "version": "1.0.0",
                "active_tasks": len(task_manager.tasks),
                "uptime": "Running"
            }
        }
    except Exception as e:
        logger.error(f"System info error: {e}")
        return {"error": str(e)}

# 📚 API DOCUMENTATION
@app.get("/")
async def root():
    """API Ana Sayfa"""
    return {
        "message": "🚀 Orion Vision Core API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "chat": "/api/chat/send",
            "terminal": "/api/terminal/execute",
            "filesystem": "/api/filesystem/operation",
            "providers": "/api/providers/list",
            "health": "/api/health",
            "system": "/api/system/info"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Orion Vision Core API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")