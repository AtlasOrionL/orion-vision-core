#!/usr/bin/env python3
"""
Agent Management API - Atlas Prompt 3.1.2
Orion Vision Core - Agent Yönetim RESTful API'leri

Bu modül, dinamik agent'ları programatik olarak kontrol etmek için
RESTful API endpoints sağlar. FastAPI framework kullanılarak
geliştirilmiştir.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import time
import uvicorn
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from pathlib import Path

# Agent modüllerini import et
import sys
import os
sys.path.append(os.path.dirname(__file__))

from dynamic_agent_loader import DynamicAgentLoader, get_global_loader, AgentModuleInfo
from agent_registry import get_global_registry
from agent_core import AgentStatus


# Pydantic modelleri
class AgentCreateRequest(BaseModel):
    """Agent oluşturma isteği"""
    module_name: str = Field(..., description="Agent modül adı")
    agent_id: str = Field(..., description="Benzersiz agent ID")
    config_path: Optional[str] = Field(None, description="Konfigürasyon dosyası yolu")
    auto_start: bool = Field(False, description="Otomatik başlatma")


class AgentActionRequest(BaseModel):
    """Agent aksiyon isteği"""
    agent_id: str = Field(..., description="Agent ID")


class ModuleLoadRequest(BaseModel):
    """Modül yükleme isteği"""
    module_name: str = Field(..., description="Yüklenecek modül adı")


class AgentResponse(BaseModel):
    """Agent yanıt modeli"""
    agent_id: str
    agent_name: str
    agent_type: str
    status: str
    uptime: float
    is_healthy: bool
    capabilities: List[str]
    stats: Dict[str, Any]


class ModuleResponse(BaseModel):
    """Modül yanıt modeli"""
    module_name: str
    module_path: str
    is_loaded: bool
    agent_class_name: str
    last_modified: Optional[float]
    load_time: Optional[float]
    error_message: Optional[str]


class APIResponse(BaseModel):
    """Genel API yanıt modeli"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: float = Field(default_factory=time.time)


# Global değişkenler
loader: Optional[DynamicAgentLoader] = None
registry = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifecycle manager"""
    global loader, registry

    # Startup
    print("🚀 Starting Agent Management API...")

    # Loader ve registry'yi başlat
    loader = get_global_loader()
    registry = get_global_registry()

    # İlk modül taraması
    loader.scan_modules()

    print("✅ Agent Management API started successfully")

    yield

    # Shutdown
    print("🛑 Shutting down Agent Management API...")
    if loader:
        loader.shutdown()
    print("✅ Agent Management API shutdown completed")


# FastAPI uygulaması
app = FastAPI(
    title="Orion Agent Management API",
    description="RESTful API for managing dynamic agents in Orion Vision Core",
    version="1.0.0",
    lifespan=lifespan
)

# Static files ve templates
current_dir = os.path.dirname(__file__)
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da kısıtlanmalı
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_loader() -> DynamicAgentLoader:
    """Loader dependency"""
    if loader is None:
        raise HTTPException(status_code=500, detail="Agent loader not initialized")
    return loader


def get_registry():
    """Registry dependency"""
    if registry is None:
        raise HTTPException(status_code=500, detail="Agent registry not initialized")
    return registry


# Web Dashboard endpoint
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Web Dashboard ana sayfası"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


# Health check endpoint
@app.get("/health", response_model=APIResponse)
async def health_check():
    """API sağlık kontrolü"""
    return APIResponse(
        success=True,
        message="Agent Management API is healthy",
        data={
            "status": "healthy",
            "loader_status": loader.status.value if loader else "not_initialized",
            "registry_status": "online" if registry else "not_initialized"
        }
    )


# Module management endpoints
@app.get("/modules", response_model=APIResponse)
async def list_modules(loader: DynamicAgentLoader = Depends(get_loader)):
    """Tüm modülleri listele"""
    try:
        modules = loader.get_all_modules()
        module_list = []

        for module_name, module_info in modules.items():
            module_list.append(ModuleResponse(
                module_name=module_info.module_name,
                module_path=module_info.module_path,
                is_loaded=module_info.is_loaded,
                agent_class_name=module_info.agent_class_name or "",
                last_modified=module_info.last_modified,
                load_time=module_info.load_time,
                error_message=module_info.error_message
            ))

        return APIResponse(
            success=True,
            message=f"Found {len(module_list)} modules",
            data=module_list
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list modules: {str(e)}")


@app.post("/modules/scan", response_model=APIResponse)
async def scan_modules(loader: DynamicAgentLoader = Depends(get_loader)):
    """Modülleri tara"""
    try:
        found_modules = loader.scan_modules()

        return APIResponse(
            success=True,
            message=f"Scan completed: {len(found_modules)} modules found",
            data={"modules": found_modules}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scan modules: {str(e)}")


@app.post("/modules/load", response_model=APIResponse)
async def load_module(request: ModuleLoadRequest, loader: DynamicAgentLoader = Depends(get_loader)):
    """Modül yükle"""
    try:
        success = loader.load_module(request.module_name)

        if success:
            module_info = loader.get_module_info(request.module_name)
            return APIResponse(
                success=True,
                message=f"Module {request.module_name} loaded successfully",
                data={
                    "module_name": request.module_name,
                    "agent_class": module_info.agent_class_name if module_info else None
                }
            )
        else:
            module_info = loader.get_module_info(request.module_name)
            error_msg = module_info.error_message if module_info else "Unknown error"
            raise HTTPException(status_code=400, detail=f"Failed to load module: {error_msg}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Module loading error: {str(e)}")


@app.post("/modules/{module_name}/reload", response_model=APIResponse)
async def reload_module(module_name: str, loader: DynamicAgentLoader = Depends(get_loader)):
    """Modülü yeniden yükle"""
    try:
        success = loader.reload_module(module_name)

        if success:
            return APIResponse(
                success=True,
                message=f"Module {module_name} reloaded successfully"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Failed to reload module: {module_name}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Module reload error: {str(e)}")


@app.get("/modules/{module_name}", response_model=APIResponse)
async def get_module_info(module_name: str, loader: DynamicAgentLoader = Depends(get_loader)):
    """Modül bilgilerini getir"""
    try:
        module_info = loader.get_module_info(module_name)

        if module_info:
            return APIResponse(
                success=True,
                message=f"Module info for {module_name}",
                data=ModuleResponse(
                    module_name=module_info.module_name,
                    module_path=module_info.module_path,
                    is_loaded=module_info.is_loaded,
                    agent_class_name=module_info.agent_class_name or "",
                    last_modified=module_info.last_modified,
                    load_time=module_info.load_time,
                    error_message=module_info.error_message
                )
            )
        else:
            raise HTTPException(status_code=404, detail=f"Module not found: {module_name}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get module info: {str(e)}")


# Agent management endpoints
@app.get("/agents", response_model=APIResponse)
async def list_agents(loader: DynamicAgentLoader = Depends(get_loader)):
    """Tüm agent'ları listele"""
    try:
        agents = loader.get_loaded_agents()
        agent_list = []

        for agent_id, agent in agents.items():
            status = agent.get_status()
            agent_list.append(AgentResponse(
                agent_id=status['agent_id'],
                agent_name=status['agent_name'],
                agent_type=status['agent_type'],
                status=status['status'],
                uptime=status['uptime'],
                is_healthy=status['is_healthy'],
                capabilities=status['capabilities'],
                stats=status['stats']
            ))

        return APIResponse(
            success=True,
            message=f"Found {len(agent_list)} agents",
            data=agent_list
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@app.post("/agents", response_model=APIResponse)
async def create_agent(request: AgentCreateRequest, loader: DynamicAgentLoader = Depends(get_loader)):
    """Yeni agent oluştur"""
    try:
        # Agent oluştur
        agent = loader.create_agent(
            module_name=request.module_name,
            agent_id=request.agent_id,
            config_path=request.config_path
        )

        if agent:
            # Otomatik başlatma
            if request.auto_start:
                start_success = loader.start_agent(request.agent_id)
                if not start_success:
                    return APIResponse(
                        success=True,
                        message=f"Agent {request.agent_id} created but failed to start",
                        data={"agent_id": request.agent_id, "started": False}
                    )

            return APIResponse(
                success=True,
                message=f"Agent {request.agent_id} created successfully",
                data={
                    "agent_id": request.agent_id,
                    "agent_type": agent.agent_type,
                    "started": request.auto_start
                }
            )
        else:
            raise HTTPException(status_code=400, detail=f"Failed to create agent: {request.agent_id}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent creation error: {str(e)}")


@app.get("/agents/{agent_id}", response_model=APIResponse)
async def get_agent_status(agent_id: str, loader: DynamicAgentLoader = Depends(get_loader)):
    """Agent durumunu getir"""
    try:
        agents = loader.get_loaded_agents()

        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

        agent = agents[agent_id]
        status = agent.get_status()

        return APIResponse(
            success=True,
            message=f"Status for agent {agent_id}",
            data=AgentResponse(
                agent_id=status['agent_id'],
                agent_name=status['agent_name'],
                agent_type=status['agent_type'],
                status=status['status'],
                uptime=status['uptime'],
                is_healthy=status['is_healthy'],
                capabilities=status['capabilities'],
                stats=status['stats']
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@app.post("/agents/{agent_id}/start", response_model=APIResponse)
async def start_agent(agent_id: str, loader: DynamicAgentLoader = Depends(get_loader)):
    """Agent'ı başlat"""
    try:
        success = loader.start_agent(agent_id)

        if success:
            return APIResponse(
                success=True,
                message=f"Agent {agent_id} started successfully"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Failed to start agent: {agent_id}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent start error: {str(e)}")


@app.post("/agents/{agent_id}/stop", response_model=APIResponse)
async def stop_agent(agent_id: str, loader: DynamicAgentLoader = Depends(get_loader)):
    """Agent'ı durdur"""
    try:
        success = loader.stop_agent(agent_id)

        if success:
            return APIResponse(
                success=True,
                message=f"Agent {agent_id} stopped successfully"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Failed to stop agent: {agent_id}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent stop error: {str(e)}")


@app.delete("/agents/{agent_id}", response_model=APIResponse)
async def delete_agent(agent_id: str, loader: DynamicAgentLoader = Depends(get_loader)):
    """Agent'ı sil"""
    try:
        # Önce durdur
        loader.stop_agent(agent_id)

        # Agent'ı kaldır
        agents = loader.get_loaded_agents()
        if agent_id in agents:
            loader._stop_and_remove_agent(agent_id)

            return APIResponse(
                success=True,
                message=f"Agent {agent_id} deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent deletion error: {str(e)}")


# System endpoints
@app.get("/system/stats", response_model=APIResponse)
async def get_system_stats(
    loader: DynamicAgentLoader = Depends(get_loader),
    registry = Depends(get_registry)
):
    """Sistem istatistiklerini getir"""
    try:
        loader_stats = loader.get_loader_stats()
        registry_stats = registry.get_registry_stats()

        return APIResponse(
            success=True,
            message="System statistics",
            data={
                "loader": loader_stats,
                "registry": registry_stats,
                "timestamp": time.time()
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system stats: {str(e)}")


@app.get("/system/health", response_model=APIResponse)
async def get_system_health(
    loader: DynamicAgentLoader = Depends(get_loader),
    registry = Depends(get_registry)
):
    """Sistem sağlık durumunu getir"""
    try:
        healthy_agents = registry.get_healthy_agents()
        running_agents = loader.get_loaded_agents()

        running_count = sum(1 for agent in running_agents.values() if agent.is_running())

        health_status = {
            "overall_health": "healthy" if len(healthy_agents) > 0 else "warning",
            "total_agents": len(running_agents),
            "running_agents": running_count,
            "healthy_agents": len(healthy_agents),
            "loader_status": loader.status.value,
            "registry_status": "online"
        }

        return APIResponse(
            success=True,
            message="System health status",
            data=health_status
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system health: {str(e)}")


# Utility function to run the API server
def run_api_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """API sunucusunu çalıştır"""
    print(f"🚀 Starting Agent Management API on {host}:{port}")
    uvicorn.run(
        "agent_management_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    run_api_server(reload=True)
