#!/usr/bin/env python3
"""
Enhanced Agent System with LLM Integration
Orion Vision Core - Phase 4: Enhanced Agent Integration

Bu sistem mevcut agent_core.py'yi Ollama LLM ile entegre ederek
intelligent agent communication sağlar.

Author: Orion Development Team
Version: 2.0.0
Date: 30 Mayıs 2025
"""

import asyncio
import json
import logging
import os
import time
import uuid
import requests
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import pika
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Agent Status ve Priority (mevcut sistemden)
class AgentStatus(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    THINKING = "thinking"  # LLM processing
    RESPONDING = "responding"  # LLM response


class AgentPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class LLMConfig:
    """LLM Configuration"""
    model_name: str = "llama3.2:1b"
    base_url: str = "http://localhost:11434"
    timeout: float = 30.0
    max_tokens: int = 500
    temperature: float = 0.7
    system_prompt: str = "You are Orion, an intelligent AI agent assistant."


@dataclass
class AgentConfig:
    """Enhanced Agent Configuration"""
    agent_id: str
    name: str
    description: str
    priority: AgentPriority
    llm_enabled: bool = True
    auto_start: bool = True
    heartbeat_interval: float = 30.0
    max_retries: int = 3
    timeout: float = 300.0


class LLMRouter:
    """LLM Router for Ollama Integration"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.logger = logging.getLogger("LLMRouter")
        self.session_history: Dict[str, List[Dict]] = {}

    async def generate_response(self, prompt: str, agent_id: str = None, context: Dict = None) -> str:
        """Generate LLM response"""
        try:
            # Prepare request
            messages = []

            # Add system prompt
            messages.append({
                "role": "system",
                "content": self.config.system_prompt
            })

            # Add context if provided
            if context:
                context_str = f"Context: {json.dumps(context, indent=2)}"
                messages.append({
                    "role": "system",
                    "content": context_str
                })

            # Add user prompt
            messages.append({
                "role": "user",
                "content": prompt
            })

            # API request to Ollama
            response = requests.post(
                f"{self.config.base_url}/api/chat",
                json={
                    "model": self.config.model_name,
                    "messages": messages,
                    "options": {
                        "temperature": self.config.temperature,
                        "num_predict": self.config.max_tokens
                    },
                    "stream": False
                },
                timeout=self.config.timeout
            )

            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("message", {}).get("content", "")

                # Store in session history
                if agent_id:
                    if agent_id not in self.session_history:
                        self.session_history[agent_id] = []

                    self.session_history[agent_id].append({
                        "timestamp": datetime.now().isoformat(),
                        "prompt": prompt,
                        "response": llm_response,
                        "context": context
                    })

                return llm_response
            else:
                raise Exception(f"LLM API error: {response.status_code}")

        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return f"LLM Error: {str(e)}"

    def get_session_history(self, agent_id: str) -> List[Dict]:
        """Get agent's LLM session history"""
        return self.session_history.get(agent_id, [])

    def clear_session_history(self, agent_id: str):
        """Clear agent's session history"""
        if agent_id in self.session_history:
            del self.session_history[agent_id]


class EnhancedAgent(ABC):
    """Enhanced Agent with LLM Integration"""

    def __init__(self, config: AgentConfig, llm_router: LLMRouter):
        self.config = config
        self.agent_id = config.agent_id
        self.status = AgentStatus.INITIALIZING
        self.llm_router = llm_router
        self.logger = logging.getLogger(f"Agent.{self.agent_id}")

        # Metrics
        self.metrics = {
            "start_time": None,
            "uptime": 0,
            "messages_processed": 0,
            "llm_calls": 0,
            "errors": 0,
            "last_activity": None
        }

        # Message queue
        self.message_queue = asyncio.Queue()
        self.running = False

        self.logger.info(f"Enhanced agent {self.agent_id} initialized")

    async def start(self):
        """Start the enhanced agent"""
        try:
            self.status = AgentStatus.RUNNING
            self.metrics["start_time"] = time.time()
            self.running = True

            # Start main loop
            asyncio.create_task(self._main_loop())

            self.logger.info(f"Enhanced agent {self.agent_id} started")

        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Failed to start agent: {e}")
            raise

    async def stop(self):
        """Stop the enhanced agent"""
        self.status = AgentStatus.STOPPING
        self.running = False
        self.logger.info(f"Enhanced agent {self.agent_id} stopped")

    async def _main_loop(self):
        """Main agent processing loop"""
        while self.running:
            try:
                # Process messages from queue
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self._process_message(message)

                # Execute agent-specific logic
                await self.execute()

                # Update metrics
                self.metrics["uptime"] = time.time() - self.metrics["start_time"]
                self.metrics["last_activity"] = time.time()

                await asyncio.sleep(1)  # Prevent busy loop

            except Exception as e:
                self.metrics["errors"] += 1
                self.logger.error(f"Main loop error: {e}")
                await asyncio.sleep(5)  # Error backoff

    async def _process_message(self, message: Dict[str, Any]):
        """Process incoming message"""
        try:
            self.metrics["messages_processed"] += 1

            # If LLM enabled, use AI to process message
            if self.config.llm_enabled:
                await self._process_with_llm(message)
            else:
                await self._process_without_llm(message)

        except Exception as e:
            self.logger.error(f"Message processing error: {e}")

    async def _process_with_llm(self, message: Dict[str, Any]):
        """Process message with LLM assistance"""
        try:
            self.status = AgentStatus.THINKING
            self.metrics["llm_calls"] += 1

            # Prepare prompt for LLM
            prompt = f"""
            Agent: {self.agent_id}
            Message Type: {message.get('type', 'unknown')}
            Content: {message.get('content', '')}

            Please analyze this message and provide an appropriate response or action.
            """

            # Get LLM response
            config_dict = asdict(self.config)
            config_dict["priority"] = self.config.priority.value  # Convert enum to value

            llm_response = await self.llm_router.generate_response(
                prompt=prompt,
                agent_id=self.agent_id,
                context={
                    "agent_config": config_dict,
                    "current_status": self.status.value,
                    "metrics": self.metrics
                }
            )

            self.status = AgentStatus.RESPONDING

            # Process LLM response
            await self._handle_llm_response(message, llm_response)

            self.status = AgentStatus.RUNNING

        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"LLM processing error: {e}")

    async def _process_without_llm(self, message: Dict[str, Any]):
        """Process message without LLM (traditional logic)"""
        # Default message processing
        self.logger.info(f"Processing message: {message}")

    async def _handle_llm_response(self, original_message: Dict, llm_response: str):
        """Handle LLM response"""
        self.logger.info(f"LLM Response: {llm_response}")

        # Here you can implement specific logic based on LLM response
        # For example, extract actions, send responses, etc.

    async def send_message(self, target_agent: str, message: Dict[str, Any]):
        """Send message to another agent"""
        # This would integrate with RabbitMQ or direct agent communication
        self.logger.info(f"Sending message to {target_agent}: {message}")

    async def add_message_to_queue(self, message: Dict[str, Any]):
        """Add message to processing queue"""
        await self.message_queue.put(message)

    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "config": asdict(self.config),
            "metrics": self.metrics,
            "llm_enabled": self.config.llm_enabled,
            "queue_size": self.message_queue.qsize()
        }

    @abstractmethod
    async def execute(self):
        """Agent-specific execution logic"""
        pass


class CommunicationAgent(EnhancedAgent):
    """Enhanced Communication Agent"""

    async def execute(self):
        """Communication agent specific logic"""
        # Check for new messages, handle communication protocols, etc.
        pass


class TaskOrchestratorAgent(EnhancedAgent):
    """Enhanced Task Orchestrator Agent"""

    def __init__(self, config: AgentConfig, llm_router: LLMRouter):
        super().__init__(config, llm_router)
        self.active_tasks: Dict[str, Dict] = {}

    async def execute(self):
        """Task orchestrator specific logic"""
        # Manage tasks, distribute work, coordinate agents
        if self.active_tasks:
            self.logger.info(f"Managing {len(self.active_tasks)} active tasks")


class AgentManager:
    """Enhanced Agent Manager"""

    def __init__(self):
        self.agents: Dict[str, EnhancedAgent] = {}
        self.llm_router = LLMRouter(LLMConfig())
        self.logger = logging.getLogger("AgentManager")

    async def create_agent(self, agent_type: str, agent_id: str, name: str, description: str) -> EnhancedAgent:
        """Create a new enhanced agent"""
        config = AgentConfig(
            agent_id=agent_id,
            name=name,
            description=description,
            priority=AgentPriority.NORMAL
        )

        if agent_type == "communication":
            agent = CommunicationAgent(config, self.llm_router)
        elif agent_type == "orchestrator":
            agent = TaskOrchestratorAgent(config, self.llm_router)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        self.agents[agent_id] = agent
        await agent.start()

        self.logger.info(f"Created and started {agent_type} agent: {agent_id}")
        return agent

    async def get_agent(self, agent_id: str) -> Optional[EnhancedAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents"""
        return [agent.get_status() for agent in self.agents.values()]

    async def send_message_to_agent(self, agent_id: str, message: Dict[str, Any]):
        """Send message to specific agent"""
        agent = self.agents.get(agent_id)
        if agent:
            await agent.add_message_to_queue(message)
        else:
            raise ValueError(f"Agent not found: {agent_id}")

    async def stop_all_agents(self):
        """Stop all agents"""
        for agent in self.agents.values():
            await agent.stop()
        self.agents.clear()


# FastAPI Integration
app = FastAPI(title="Enhanced Agent System", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_manager = AgentManager()

@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    # Create default agents
    await agent_manager.create_agent("communication", "comm_agent_1", "Communication Agent 1", "Handles inter-agent communication")
    await agent_manager.create_agent("orchestrator", "orchestrator_1", "Task Orchestrator", "Manages and distributes tasks")

@app.get("/")
async def root():
    return {
        "message": "🤖 Enhanced Agent System with LLM Integration",
        "version": "2.0.0",
        "agents_count": len(agent_manager.agents),
        "llm_model": agent_manager.llm_router.config.model_name
    }

@app.get("/agents")
async def list_agents():
    """List all agents"""
    return await agent_manager.list_agents()

@app.post("/agents/{agent_id}/message")
async def send_message_to_agent(agent_id: str, message: dict):
    """Send message to agent"""
    try:
        await agent_manager.send_message_to_agent(agent_id, message)
        return {"status": "sent", "agent_id": agent_id, "message": message}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """Get agent status"""
    agent = await agent_manager.get_agent(agent_id)
    if agent:
        return agent.get_status()
    else:
        raise HTTPException(status_code=404, detail="Agent not found")

@app.get("/llm/test")
async def test_llm():
    """Test LLM functionality"""
    response = await agent_manager.llm_router.generate_response(
        "Hello! Please introduce yourself as Orion AI agent.",
        context={"test": True}
    )
    return {"llm_response": response}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("🚀 Starting Enhanced Agent System with LLM Integration...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
