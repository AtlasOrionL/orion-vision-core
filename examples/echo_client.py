#!/usr/bin/env python3
"""
Echo Client Example - Atlas Prompt 1.2.2
Orion Vision Core - Echo Agent Test Client

Bu script, Echo Agent'a mesaj gönderir ve yanıtları dinler.
"""

import sys
import os
import time
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


class EchoClient:
    """
    Echo Agent Test Client
    
    Bu client, Echo Agent'a çeşitli mesajlar gönderir ve yanıtları dinler.
    """
    
    def __init__(self, client_id: str = "echo_client"):
        """
        Echo Client başlatıcı
        
        Args:
            client_id: Client'ın benzersiz kimliği
        """
        self.client_id = client_id
        self.comm_agent = CommunicationAgent(client_id)
        self.received_responses = []
        self.is_listening = False
        
        # Response handler'ı kaydet
        self._register_handlers()
    
    def _register_handlers(self):
        """Mesaj handler'larını kaydet"""
        # Agent communication response handler
        self.comm_agent.register_message_handler(
            MessageType.AGENT_COMMUNICATION.value,
            self._handle_echo_response
        )
        
        # Task response handler
        self.comm_agent.register_message_handler(
            MessageType.TASK_RESPONSE.value,
            self._handle_task_response
        )
    
    def _handle_echo_response(self, message: OrionMessage):
        """Echo yanıtlarını işle"""
        print(f"📨 Echo response received from {message.sender_id}")
        print(f"📝 Content: {message.content}")
        
        if hasattr(message, 'metadata') and message.metadata:
            if 'original_message' in message.metadata:
                print(f"🔄 Original: {message.metadata['original_message']}")
            if 'echo_timestamp' in message.metadata:
                echo_time = message.metadata['echo_timestamp']
                latency = time.time() - echo_time
                print(f"⏱️ Echo latency: {latency:.3f}s")
        
        self.received_responses.append(message)
        print("-" * 40)
    
    def _handle_task_response(self, message: OrionMessage):
        """Task yanıtlarını işle"""
        print(f"📋 Task response received from {message.sender_id}")
        print(f"📝 Content: {message.content}")
        
        if hasattr(message, 'metadata') and message.metadata:
            if 'task_status' in message.metadata:
                print(f"✅ Status: {message.metadata['task_status']}")
            if 'execution_time' in message.metadata:
                print(f"⏱️ Execution time: {message.metadata['execution_time']}s")
        
        self.received_responses.append(message)
        print("-" * 40)
    
    def start_listening(self):
        """Yanıt dinlemeye başla"""
        try:
            print(f"🚀 Starting Echo Client: {self.client_id}")
            
            # Communication agent'a bağlan
            if not self.comm_agent.connect():
                print("❌ Failed to connect to RabbitMQ")
                return False
            
            # Mesaj dinlemeye başla
            if not self.comm_agent.consume_messages():
                print("❌ Failed to start consuming messages")
                return False
            
            self.is_listening = True
            print(f"✅ Echo Client started successfully")
            print(f"🎧 Listening on queue: orion.agent.{self.client_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error starting Echo Client: {e}")
            return False
    
    def stop_listening(self):
        """Yanıt dinlemeyi durdur"""
        try:
            print(f"🛑 Stopping Echo Client: {self.client_id}")
            
            self.is_listening = False
            
            # Mesaj dinlemeyi durdur
            self.comm_agent.stop_consuming_messages()
            
            # Bağlantıyı kapat
            self.comm_agent.disconnect()
            
            print(f"✅ Echo Client stopped")
            print(f"📊 Total responses received: {len(self.received_responses)}")
            
        except Exception as e:
            print(f"❌ Error stopping Echo Client: {e}")
    
    def send_echo_message(self, content: str, priority: str = MessagePriority.NORMAL.value):
        """Echo agent'a mesaj gönder"""
        try:
            message = create_message(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=content,
                sender_id=self.client_id,
                target_agent="echo_agent_demo",
                priority=priority,
                test_timestamp=time.time()
            )
            
            echo_queue = "orion.agent.echo_agent_demo"
            success = self.comm_agent.publish_message(echo_queue, message)
            
            if success:
                print(f"📤 Message sent to echo agent: {content}")
                return True
            else:
                print(f"❌ Failed to send message: {content}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def send_task_request(self, task_content: str):
        """Echo agent'a task request gönder"""
        try:
            message = create_message(
                message_type=MessageType.TASK_REQUEST.value,
                content=task_content,
                sender_id=self.client_id,
                target_agent="echo_agent_demo",
                priority=MessagePriority.HIGH.value,
                task_type="echo_task",
                expected_duration=0.1
            )
            
            echo_queue = "orion.agent.echo_agent_demo"
            success = self.comm_agent.publish_message(echo_queue, message)
            
            if success:
                print(f"📋 Task request sent to echo agent: {task_content}")
                return True
            else:
                print(f"❌ Failed to send task request: {task_content}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending task request: {e}")
            return False
    
    def send_discovery_request(self):
        """Discovery request gönder"""
        try:
            message = create_message(
                message_type=MessageType.DISCOVERY.value,
                content="Discover available agents",
                sender_id=self.client_id,
                priority=MessagePriority.NORMAL.value,
                discovery_type="agent_discovery"
            )
            
            echo_queue = "orion.agent.echo_agent_demo"
            success = self.comm_agent.publish_message(echo_queue, message)
            
            if success:
                print(f"🔍 Discovery request sent to echo agent")
                return True
            else:
                print(f"❌ Failed to send discovery request")
                return False
                
        except Exception as e:
            print(f"❌ Error sending discovery request: {e}")
            return False
    
    def run_test_sequence(self):
        """Test sekansını çalıştır"""
        if not self.start_listening():
            return
        
        try:
            print("\n🧪 Starting Echo Agent Test Sequence")
            print("=" * 50)
            
            # Test 1: Basit echo mesajları
            print("\n📤 Test 1: Basic Echo Messages")
            test_messages = [
                "Hello Echo Agent!",
                "Bu bir test mesajıdır",
                "Testing Turkish characters: ğüşıöç",
                "Special chars: !@#$%^&*()",
                "Numbers: 12345"
            ]
            
            for i, msg in enumerate(test_messages, 1):
                print(f"\n📤 Sending message {i}/{len(test_messages)}")
                self.send_echo_message(msg)
                time.sleep(1)  # Mesajlar arası bekleme
            
            # Test 2: Farklı öncelik seviyeleri
            print("\n📤 Test 2: Priority Levels")
            priorities = [
                (MessagePriority.LOW.value, "Low priority message"),
                (MessagePriority.NORMAL.value, "Normal priority message"),
                (MessagePriority.HIGH.value, "High priority message"),
                (MessagePriority.CRITICAL.value, "Critical priority message")
            ]
            
            for priority, content in priorities:
                print(f"\n📤 Sending {priority} priority message")
                self.send_echo_message(content, priority)
                time.sleep(1)
            
            # Test 3: Task requests
            print("\n📤 Test 3: Task Requests")
            task_requests = [
                "Process data file",
                "Generate report",
                "Backup database",
                "Send notification"
            ]
            
            for task in task_requests:
                print(f"\n📋 Sending task request")
                self.send_task_request(task)
                time.sleep(1)
            
            # Test 4: Discovery
            print("\n📤 Test 4: Agent Discovery")
            self.send_discovery_request()
            
            # Yanıtları bekle
            print("\n⏳ Waiting for responses...")
            time.sleep(10)
            
            # Sonuçları göster
            print(f"\n📊 Test Results:")
            print(f"✅ Total responses received: {len(self.received_responses)}")
            
            # Response tiplerini analiz et
            response_types = {}
            for response in self.received_responses:
                msg_type = response.message_type
                response_types[msg_type] = response_types.get(msg_type, 0) + 1
            
            print(f"📈 Response breakdown:")
            for msg_type, count in response_types.items():
                print(f"  - {msg_type}: {count}")
            
        except KeyboardInterrupt:
            print("\n⚠️ Test interrupted by user")
        finally:
            self.stop_listening()


def main():
    """Ana fonksiyon"""
    print("🚀 Echo Client Example - Atlas Prompt 1.2.2")
    print("=" * 50)
    
    # Echo client oluştur
    echo_client = EchoClient("echo_test_client")
    
    try:
        # Test sekansını çalıştır
        echo_client.run_test_sequence()
        
    except Exception as e:
        print(f"❌ Echo Client error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
