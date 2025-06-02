#!/usr/bin/env python3
"""
Echo Agent Example - Atlas Prompt 1.2.2
Orion Vision Core - Basit Echo Agent Örneği

Bu script, CommunicationAgent sınıfını kullanarak basit bir echo agent'ı implement eder.
Echo agent, aldığı mesajları gönderen agent'a geri gönderir.
"""

import sys
import os
import time
import signal
import threading

# Communication agent'ı import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agents.communication_agent import (
    CommunicationAgent, 
    OrionMessage, 
    MessageType, 
    MessagePriority,
    create_message
)


class EchoAgent:
    """
    Basit Echo Agent
    
    Bu agent, aldığı mesajları gönderen agent'a geri gönderir.
    Mesaj routing ve agent iletişiminin temel örneğidir.
    """
    
    def __init__(self, agent_id: str = "echo_agent"):
        """
        Echo Agent başlatıcı
        
        Args:
            agent_id: Agent'ın benzersiz kimliği
        """
        self.agent_id = agent_id
        self.comm_agent = CommunicationAgent(agent_id)
        self.is_running = False
        self.message_count = 0
        
        # Message handlers'ı kaydet
        self._register_handlers()
    
    def _register_handlers(self):
        """Mesaj handler'larını kaydet"""
        # Agent communication handler
        self.comm_agent.register_message_handler(
            MessageType.AGENT_COMMUNICATION.value,
            self._handle_agent_communication
        )
        
        # Task request handler
        self.comm_agent.register_message_handler(
            MessageType.TASK_REQUEST.value,
            self._handle_task_request
        )
        
        # System status handler
        self.comm_agent.register_message_handler(
            MessageType.SYSTEM_STATUS.value,
            self._handle_system_status
        )
        
        # Discovery handler
        self.comm_agent.register_message_handler(
            MessageType.DISCOVERY.value,
            self._handle_discovery
        )
    
    def _handle_agent_communication(self, message: OrionMessage):
        """Agent iletişim mesajlarını işle"""
        print(f"🔄 Echo: Agent communication from {message.sender_id}")
        print(f"📝 Original content: {message.content}")
        
        # Echo mesajı oluştur
        echo_content = f"Echo: {message.content}"
        echo_message = create_message(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content=echo_content,
            sender_id=self.agent_id,
            target_agent=message.sender_id,
            priority=message.priority,
            correlation_id=message.correlation_id,
            original_message=message.content,
            echo_timestamp=time.time()
        )
        
        # Gönderen agent'a geri gönder
        sender_queue = f"orion.agent.{message.sender_id}"
        success = self.comm_agent.publish_message(sender_queue, echo_message)
        
        if success:
            self.message_count += 1
            print(f"✅ Echo sent back to {message.sender_id}")
        else:
            print(f"❌ Failed to send echo to {message.sender_id}")
    
    def _handle_task_request(self, message: OrionMessage):
        """Görev isteği mesajlarını işle"""
        print(f"📋 Echo: Task request from {message.sender_id}")
        print(f"📝 Task content: {message.content}")
        
        # Task response oluştur
        response_content = f"Echo task completed: {message.content}"
        response_message = create_message(
            message_type=MessageType.TASK_RESPONSE.value,
            content=response_content,
            sender_id=self.agent_id,
            target_agent=message.sender_id,
            priority=MessagePriority.HIGH.value,
            correlation_id=message.correlation_id,
            task_status="completed",
            execution_time=0.1
        )
        
        # Response gönder
        sender_queue = f"orion.agent.{message.sender_id}"
        success = self.comm_agent.publish_message(sender_queue, response_message)
        
        if success:
            self.message_count += 1
            print(f"✅ Task response sent to {message.sender_id}")
        else:
            print(f"❌ Failed to send task response to {message.sender_id}")
    
    def _handle_system_status(self, message: OrionMessage):
        """Sistem durumu mesajlarını işle"""
        print(f"📊 Echo: System status from {message.sender_id}")
        print(f"📝 Status: {message.content}")
        
        # Kendi durumumuzu rapor et
        status_message = create_message(
            message_type=MessageType.SYSTEM_STATUS.value,
            content=f"Echo Agent Status: Running, processed {self.message_count} messages",
            sender_id=self.agent_id,
            priority=MessagePriority.LOW.value,
            agent_status="running",
            processed_messages=self.message_count,
            uptime=time.time()
        )
        
        # System status queue'ya gönder
        system_queue = "orion.system.status"
        self.comm_agent.declare_queue(system_queue)
        success = self.comm_agent.publish_message(system_queue, status_message)
        
        if success:
            print(f"✅ Status report sent to system queue")
        else:
            print(f"❌ Failed to send status report")
    
    def _handle_discovery(self, message: OrionMessage):
        """Agent keşfi mesajlarını işle"""
        print(f"🔍 Echo: Discovery request from {message.sender_id}")
        
        # Discovery response oluştur
        discovery_response = create_message(
            message_type=MessageType.DISCOVERY.value,
            content=f"Echo Agent discovered",
            sender_id=self.agent_id,
            target_agent=message.sender_id,
            priority=MessagePriority.NORMAL.value,
            agent_type="echo_agent",
            capabilities=["echo", "task_echo", "status_report"],
            version="1.0.0"
        )
        
        # Discovery queue'ya gönder
        discovery_queue = "orion.system.discovery"
        self.comm_agent.declare_queue(discovery_queue)
        success = self.comm_agent.publish_message(discovery_queue, discovery_response)
        
        if success:
            print(f"✅ Discovery response sent")
        else:
            print(f"❌ Failed to send discovery response")
    
    def start(self):
        """Echo agent'ı başlat"""
        try:
            print(f"🚀 Starting Echo Agent: {self.agent_id}")
            
            # Communication agent'a bağlan
            if not self.comm_agent.connect():
                print("❌ Failed to connect to RabbitMQ")
                return False
            
            # Mesaj dinlemeye başla
            if not self.comm_agent.consume_messages():
                print("❌ Failed to start consuming messages")
                return False
            
            self.is_running = True
            print(f"✅ Echo Agent started successfully")
            print(f"🎧 Listening on queue: orion.agent.{self.agent_id}")
            
            # Heartbeat gönder
            self.comm_agent.send_heartbeat()
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting Echo Agent: {e}")
            return False
    
    def stop(self):
        """Echo agent'ı durdur"""
        try:
            print(f"🛑 Stopping Echo Agent: {self.agent_id}")
            
            self.is_running = False
            
            # Mesaj dinlemeyi durdur
            self.comm_agent.stop_consuming_messages()
            
            # Bağlantıyı kapat
            self.comm_agent.disconnect()
            
            print(f"✅ Echo Agent stopped")
            print(f"📊 Total messages processed: {self.message_count}")
            
        except Exception as e:
            print(f"❌ Error stopping Echo Agent: {e}")
    
    def run(self):
        """Echo agent'ı çalıştır (blocking)"""
        if not self.start():
            return
        
        try:
            print("⏳ Echo Agent running... (Press Ctrl+C to stop)")
            
            # Ana döngü
            while self.is_running:
                time.sleep(1)
                
                # Periyodik heartbeat gönder (her 60 saniyede)
                if int(time.time()) % 60 == 0:
                    self.comm_agent.send_heartbeat()
                    
        except KeyboardInterrupt:
            print("\n⚠️ Keyboard interrupt received")
        finally:
            self.stop()


def signal_handler(signum, frame):
    """Signal handler for graceful shutdown"""
    print(f"\n🛑 Signal {signum} received, shutting down...")
    sys.exit(0)


def main():
    """Ana fonksiyon"""
    print("🚀 Echo Agent Example - Atlas Prompt 1.2.2")
    print("=" * 50)
    
    # Signal handler'ları ayarla
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Echo agent oluştur
    echo_agent = EchoAgent("echo_agent_demo")
    
    try:
        # Agent'ı çalıştır
        echo_agent.run()
        
    except Exception as e:
        print(f"❌ Echo Agent error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
