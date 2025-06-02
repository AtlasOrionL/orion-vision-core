#!/usr/bin/env python3
"""
Communication Enabled Agent Example - Atlas Prompt 2.1.2
Orion Vision Core - Communication Agent Entegrasyonu Örneği

Bu script, agent_core.py ve communication_agent.py modüllerini entegre ederek
iletişim yetenekli bir agent örneği oluşturur.
"""

import sys
import os
import time
import random
import threading

# Agent modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agent_core import Agent, AgentConfig, AgentStatus, create_agent_config, load_agent_config
from agents.communication_agent import CommunicationAgent, create_message, MessageType, MessagePriority


class CommunicationEnabledAgent(Agent):
    """
    Communication Enabled Agent
    
    Bu agent, agent_core.py'nin temel işlevselliğini communication_agent.py
    ile entegre ederek hem yaşam döngüsü yönetimi hem de mesajlaşma 
    yeteneklerini birleştirir.
    """
    
    def __init__(self, config: AgentConfig, auto_register: bool = True):
        """
        Communication Enabled Agent başlatıcı
        
        Args:
            config: Agent konfigürasyon objesi
            auto_register: Otomatik registry'ye kayıt
        """
        super().__init__(config, auto_register)
        
        # Communication agent
        self.comm_agent = CommunicationAgent(self.agent_id)
        
        # Message handlers
        self.message_handlers = {}
        
        # Communication settings
        self.auto_connect = True
        self.auto_heartbeat = True
        self.heartbeat_queue = "orion.system.heartbeat"
        
        # Agent'a communication yetenekleri ekle
        self.add_capability("message_communication")
        self.add_capability("agent_discovery")
        self.add_capability("heartbeat_reporting")
        
        # Message handler'ları kaydet
        self._register_default_handlers()
    
    def initialize(self) -> bool:
        """
        Agent'a özel başlatma işlemleri
        
        Returns:
            bool: Başlatma başarılı ise True
        """
        try:
            self.logger.info("Initializing Communication Enabled Agent...")
            
            # Communication agent'ı bağla
            if self.auto_connect:
                if not self.comm_agent.connect():
                    self.logger.error("Failed to connect communication agent")
                    return False
                
                self.logger.info("Communication agent connected successfully")
            
            # Agent'a özel başlatma işlemleri
            self._setup_communication()
            
            self.logger.info("Communication Enabled Agent initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Communication Enabled Agent initialization failed: {e}")
            return False
    
    def run(self):
        """
        Agent'ın ana çalışma döngüsü
        """
        self.logger.info("Communication Enabled Agent main loop started")
        
        try:
            # Agent discovery mesajı gönder
            self._send_discovery_message()
            
            # Ana çalışma döngüsü
            while not self.stop_event.is_set():
                # Simulated work
                self._do_communication_work()
                
                # Work interval kadar bekle
                if self.stop_event.wait(2.0):
                    break  # Stop event set edildi
                
        except Exception as e:
            self.logger.error(f"Communication Enabled Agent run error: {e}")
            raise
        finally:
            self.logger.info("Communication Enabled Agent main loop ended")
    
    def cleanup(self):
        """
        Agent'a özel temizlik işlemleri
        """
        try:
            self.logger.info("Cleaning up Communication Enabled Agent...")
            
            # Goodbye mesajı gönder
            self._send_goodbye_message()
            
            # Communication agent'ı kapat
            if self.comm_agent.is_connected:
                self.comm_agent.disconnect()
                self.logger.info("Communication agent disconnected")
            
            self.logger.info("Communication Enabled Agent cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Communication Enabled Agent cleanup error: {e}")
    
    def _setup_communication(self):
        """Communication kurulumu"""
        try:
            # Agent'ın kendi queue'sunu oluştur
            agent_queue = f"orion.agent.{self.agent_id}"
            self.comm_agent.declare_queue(agent_queue)
            
            # Message handler'ları kaydet
            for message_type, handler in self.message_handlers.items():
                self.comm_agent.register_message_handler(message_type, handler)
            
            # Message consumption'ı başlat
            self.comm_agent.consume_messages(agent_queue)
            
            self.logger.info(f"Communication setup completed for queue: {agent_queue}")
            
        except Exception as e:
            self.logger.error(f"Communication setup error: {e}")
    
    def _register_default_handlers(self):
        """Default message handler'ları kaydet"""
        self.message_handlers = {
            MessageType.AGENT_COMMUNICATION.value: self._handle_agent_communication,
            MessageType.TASK_REQUEST.value: self._handle_task_request,
            MessageType.SYSTEM_STATUS.value: self._handle_system_status,
            MessageType.DISCOVERY.value: self._handle_discovery,
            MessageType.HEARTBEAT.value: self._handle_heartbeat
        }
    
    def _handle_agent_communication(self, message):
        """Agent communication mesajlarını işle"""
        try:
            self.logger.info(f"Received agent communication: {message.content}")
            
            # Echo response gönder
            response = create_message(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=f"Echo from {self.agent_id}: {message.content}",
                sender_id=self.agent_id,
                target_agent=message.sender_id,
                correlation_id=message.correlation_id
            )
            
            # Response gönder
            response_queue = f"orion.agent.{message.sender_id}"
            self.comm_agent.publish_message(response_queue, response)
            
            self.stats['tasks_completed'] += 1
            
        except Exception as e:
            self.logger.error(f"Agent communication handler error: {e}")
            self.stats['tasks_failed'] += 1
    
    def _handle_task_request(self, message):
        """Task request mesajlarını işle"""
        try:
            self.logger.info(f"Received task request: {message.content}")
            
            # Simulated task processing
            time.sleep(random.uniform(0.1, 0.5))
            
            # Task response gönder
            response = create_message(
                message_type=MessageType.TASK_RESPONSE.value,
                content=f"Task completed by {self.agent_id}",
                sender_id=self.agent_id,
                target_agent=message.sender_id,
                correlation_id=message.correlation_id,
                metadata={
                    'task_id': message.metadata.get('task_id', 'unknown'),
                    'completion_time': time.time(),
                    'status': 'completed'
                }
            )
            
            # Response gönder
            response_queue = f"orion.agent.{message.sender_id}"
            self.comm_agent.publish_message(response_queue, response)
            
            self.stats['tasks_completed'] += 1
            
        except Exception as e:
            self.logger.error(f"Task request handler error: {e}")
            self.stats['tasks_failed'] += 1
    
    def _handle_system_status(self, message):
        """System status mesajlarını işle"""
        try:
            self.logger.info(f"Received system status request: {message.content}")
            
            # Agent status response gönder
            status = self.get_status()
            response = create_message(
                message_type=MessageType.SYSTEM_STATUS.value,
                content=f"Status report from {self.agent_id}",
                sender_id=self.agent_id,
                target_agent=message.sender_id,
                correlation_id=message.correlation_id,
                metadata=status
            )
            
            # Response gönder
            response_queue = f"orion.agent.{message.sender_id}"
            self.comm_agent.publish_message(response_queue, response)
            
        except Exception as e:
            self.logger.error(f"System status handler error: {e}")
    
    def _handle_discovery(self, message):
        """Discovery mesajlarını işle"""
        try:
            self.logger.info(f"Received discovery request: {message.content}")
            
            # Agent capabilities response gönder
            response = create_message(
                message_type=MessageType.DISCOVERY.value,
                content=f"Agent discovery response from {self.agent_id}",
                sender_id=self.agent_id,
                target_agent=message.sender_id,
                correlation_id=message.correlation_id,
                metadata={
                    'agent_id': self.agent_id,
                    'agent_name': self.agent_name,
                    'agent_type': self.agent_type,
                    'capabilities': self.config.capabilities,
                    'status': self.status.value,
                    'uptime': time.time() - self.start_time if self.start_time else 0
                }
            )
            
            # Response gönder
            response_queue = f"orion.agent.{message.sender_id}"
            self.comm_agent.publish_message(response_queue, response)
            
        except Exception as e:
            self.logger.error(f"Discovery handler error: {e}")
    
    def _handle_heartbeat(self, message):
        """Heartbeat mesajlarını işle"""
        try:
            self.logger.debug(f"Received heartbeat: {message.sender_id}")
            # Heartbeat mesajları genellikle response gerektirmez
            
        except Exception as e:
            self.logger.error(f"Heartbeat handler error: {e}")
    
    def _do_communication_work(self):
        """Simulated communication work"""
        try:
            # Random communication activity
            activity_type = random.choice(['heartbeat', 'status_check', 'discovery'])
            
            if activity_type == 'heartbeat' and self.auto_heartbeat:
                self._send_heartbeat()
            elif activity_type == 'status_check':
                self.logger.debug(f"Status check: {self.status.value}")
            elif activity_type == 'discovery':
                self.logger.debug("Discovery activity")
            
        except Exception as e:
            self.logger.error(f"Communication work error: {e}")
    
    def _send_discovery_message(self):
        """Agent discovery mesajı gönder"""
        try:
            discovery_msg = create_message(
                message_type=MessageType.DISCOVERY.value,
                content=f"Agent {self.agent_id} is online",
                sender_id=self.agent_id,
                priority=MessagePriority.NORMAL.value,
                metadata={
                    'agent_type': self.agent_type,
                    'capabilities': self.config.capabilities,
                    'startup_time': time.time()
                }
            )
            
            # System discovery queue'ya gönder
            discovery_queue = "orion.system.discovery"
            self.comm_agent.declare_queue(discovery_queue)
            success = self.comm_agent.publish_message(discovery_queue, discovery_msg)
            
            if success:
                self.logger.info("Discovery message sent successfully")
            else:
                self.logger.warning("Failed to send discovery message")
                
        except Exception as e:
            self.logger.error(f"Discovery message error: {e}")
    
    def _send_heartbeat(self):
        """Heartbeat mesajı gönder"""
        try:
            heartbeat_msg = create_message(
                message_type=MessageType.HEARTBEAT.value,
                content=f"Heartbeat from {self.agent_id}",
                sender_id=self.agent_id,
                priority=MessagePriority.LOW.value,
                metadata={
                    'status': self.status.value,
                    'uptime': time.time() - self.start_time if self.start_time else 0,
                    'stats': self.stats
                }
            )
            
            # Heartbeat queue'ya gönder
            self.comm_agent.declare_queue(self.heartbeat_queue)
            success = self.comm_agent.publish_message(self.heartbeat_queue, heartbeat_msg)
            
            if success:
                self.logger.debug("Heartbeat sent successfully")
            else:
                self.logger.warning("Failed to send heartbeat")
                
        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
    
    def _send_goodbye_message(self):
        """Goodbye mesajı gönder"""
        try:
            goodbye_msg = create_message(
                message_type=MessageType.SYSTEM_STATUS.value,
                content=f"Agent {self.agent_id} is shutting down",
                sender_id=self.agent_id,
                priority=MessagePriority.NORMAL.value,
                metadata={
                    'shutdown_time': time.time(),
                    'final_stats': self.stats
                }
            )
            
            # System status queue'ya gönder
            status_queue = "orion.system.status"
            self.comm_agent.declare_queue(status_queue)
            success = self.comm_agent.publish_message(status_queue, goodbye_msg)
            
            if success:
                self.logger.info("Goodbye message sent successfully")
            else:
                self.logger.warning("Failed to send goodbye message")
                
        except Exception as e:
            self.logger.error(f"Goodbye message error: {e}")
    
    def send_message_to_agent(self, target_agent_id: str, content: str, message_type: str = None) -> bool:
        """
        Başka bir agent'a mesaj gönder
        
        Args:
            target_agent_id: Hedef agent ID
            content: Mesaj içeriği
            message_type: Mesaj tipi (default: agent_communication)
            
        Returns:
            bool: Gönderim başarılı ise True
        """
        try:
            msg_type = message_type or MessageType.AGENT_COMMUNICATION.value
            
            message = create_message(
                message_type=msg_type,
                content=content,
                sender_id=self.agent_id,
                target_agent=target_agent_id
            )
            
            target_queue = f"orion.agent.{target_agent_id}"
            return self.comm_agent.publish_message(target_queue, message)
            
        except Exception as e:
            self.logger.error(f"Send message error: {e}")
            return False
    
    def get_communication_stats(self) -> dict:
        """Communication istatistiklerini getir"""
        comm_stats = self.comm_agent.get_stats() if self.comm_agent else {}
        
        return {
            'agent_stats': self.get_status(),
            'communication_stats': comm_stats,
            'is_connected': self.comm_agent.is_connected if self.comm_agent else False,
            'is_consuming': self.comm_agent.is_consuming if self.comm_agent else False
        }


def create_communication_enabled_agent(config_path: str = None, agent_id: str = None) -> CommunicationEnabledAgent:
    """
    Communication Enabled Agent oluştur
    
    Args:
        config_path: Konfigürasyon dosyası yolu
        agent_id: Agent ID (config_path yoksa kullanılır)
        
    Returns:
        CommunicationEnabledAgent: Oluşturulan agent
    """
    if config_path:
        config = load_agent_config(config_path)
        if not config:
            raise ValueError(f"Failed to load config from: {config_path}")
    else:
        config = create_agent_config(
            agent_id=agent_id or "comm_enabled_agent",
            agent_name="Communication Enabled Agent",
            agent_type="communication_enabled_agent",
            auto_start=False,
            heartbeat_interval=15.0,
            log_level="INFO"
        )
    
    return CommunicationEnabledAgent(config)


def main():
    """Ana test fonksiyonu"""
    print("🚀 Communication Enabled Agent Test - Atlas Prompt 2.1.2")
    print("=" * 60)
    
    try:
        # Agent oluştur
        agent = create_communication_enabled_agent(agent_id="test_comm_agent")
        
        print(f"📋 Agent Info:")
        print(f"  ID: {agent.agent_id}")
        print(f"  Name: {agent.agent_name}")
        print(f"  Type: {agent.agent_type}")
        print(f"  Capabilities: {agent.config.capabilities}")
        
        # Agent'ı başlat
        print(f"\n🚀 Starting agent...")
        success = agent.start()
        
        if success:
            print(f"✅ Agent started successfully")
            
            # Biraz çalışmasını bekle
            print(f"\n⏳ Letting agent work for 20 seconds...")
            time.sleep(20)
            
            # Communication stats göster
            comm_stats = agent.get_communication_stats()
            print(f"\n📊 Communication Stats:")
            print(f"  Connected: {comm_stats['is_connected']}")
            print(f"  Consuming: {comm_stats['is_consuming']}")
            print(f"  Messages Sent: {comm_stats['communication_stats'].get('messages_sent', 0)}")
            print(f"  Messages Received: {comm_stats['communication_stats'].get('messages_received', 0)}")
            
            # Agent'ı durdur
            print(f"\n🛑 Stopping agent...")
            stop_success = agent.stop()
            
            if stop_success:
                print(f"✅ Agent stopped successfully")
            else:
                print(f"❌ Agent stop failed")
                
        else:
            print(f"❌ Agent start failed")
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
        if 'agent' in locals():
            agent.stop()
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        if 'agent' in locals():
            agent.stop()
    
    print(f"\n🏁 Communication Enabled Agent test completed")


if __name__ == "__main__":
    main()
