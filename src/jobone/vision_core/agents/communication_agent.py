#!/usr/bin/env python3
"""
Communication Agent - Orion Vision Core
Atlas Prompt 1.2.1: Agent'lar arası iletişimi standardize eden temel modül

Bu modül, Orion Vision Core projesi için agent'lar arası güvenilir ve esnek
mesaj alışverişi sağlar. RabbitMQ tabanlı mesaj kuyruğu sistemi kullanır.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import json
import logging
import datetime
import threading
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from enum import Enum
import pika
import pika.exceptions


class MessagePriority(Enum):
    """Mesaj öncelik seviyeleri"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageType(Enum):
    """Standart mesaj tipleri"""
    AGENT_COMMUNICATION = "agent_communication"
    SYSTEM_STATUS = "system_status"
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    ERROR_REPORT = "error_report"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    SHUTDOWN = "shutdown"


@dataclass
class OrionMessage:
    """Orion mesaj formatı standardı"""
    message_type: str
    content: str
    sender_id: str
    priority: str = MessagePriority.NORMAL.value
    target_agent: Optional[str] = None
    correlation_id: Optional[str] = None
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Mesaj oluşturulduktan sonra otomatik alanları doldur"""
        if self.timestamp is None:
            self.timestamp = datetime.datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        """Mesajı dictionary'ye çevir"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrionMessage':
        """Dictionary'den mesaj oluştur"""
        return cls(**data)

    def to_json(self) -> str:
        """Mesajı JSON string'e çevir"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class CommunicationAgent:
    """
    Orion Vision Core - Agent İletişim Modülü

    Bu sınıf, agent'lar arası güvenilir mesaj alışverişi için
    RabbitMQ tabanlı iletişim altyapısını sağlar.
    """

    def __init__(self,
                 agent_id: str,
                 host: str = 'localhost',
                 port: int = 5672,
                 virtual_host: str = 'orion_vhost',
                 username: str = 'orion_admin',
                 password: str = 'orion_secure_2024',
                 auto_reconnect: bool = True,
                 heartbeat_interval: int = 600):
        """
        Communication Agent başlatıcı

        Args:
            agent_id: Bu agent'ın benzersiz kimliği
            host: RabbitMQ sunucu adresi
            port: RabbitMQ portu
            virtual_host: Virtual host adı
            username: Kullanıcı adı
            password: Şifre
            auto_reconnect: Otomatik yeniden bağlanma
            heartbeat_interval: Heartbeat aralığı (saniye)
        """
        self.agent_id = agent_id
        self.host = host
        self.port = port
        self.virtual_host = virtual_host
        self.username = username
        self.password = password
        self.auto_reconnect = auto_reconnect
        self.heartbeat_interval = heartbeat_interval

        # Bağlantı durumu
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.is_connected = False
        self.is_consuming = False

        # Message handling
        self.message_handlers: Dict[str, Callable] = {}
        self.consumer_thread: Optional[threading.Thread] = None
        self.stop_consuming = False

        # Logging
        self.logger = self._setup_logger()

        # Statistics
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'connection_errors': 0,
            'last_heartbeat': None
        }

    def _setup_logger(self) -> logging.Logger:
        """Logger kurulumu"""
        logger = logging.getLogger(f"CommunicationAgent.{self.agent_id}")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def connect(self) -> bool:
        """
        RabbitMQ'ya bağlan

        Returns:
            bool: Bağlantı başarılı ise True
        """
        try:
            # Bağlantı parametrelerini ayarla
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                heartbeat=self.heartbeat_interval,
                blocked_connection_timeout=300
            )

            # Bağlantı kur
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.is_connected = True

            self.logger.info(f"RabbitMQ'ya başarıyla bağlanıldı: {self.host}:{self.port}/{self.virtual_host}")

            # Agent'a özel queue oluştur
            self._declare_agent_queue()

            return True

        except Exception as e:
            self.stats['connection_errors'] += 1
            self.logger.error(f"RabbitMQ bağlantı hatası: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """RabbitMQ bağlantısını kapat"""
        try:
            self.stop_consuming = True
            self.is_consuming = False

            if self.consumer_thread and self.consumer_thread.is_alive():
                self.consumer_thread.join(timeout=5)

            if self.connection and not self.connection.is_closed:
                self.connection.close()
                self.logger.info("RabbitMQ bağlantısı kapatıldı")

            self.is_connected = False

        except Exception as e:
            self.logger.error(f"Bağlantı kapatma hatası: {e}")

    def _declare_agent_queue(self):
        """Agent'a özel queue oluştur"""
        if not self.channel:
            return False

        try:
            queue_name = f"orion.agent.{self.agent_id}"
            self.channel.queue_declare(queue=queue_name, durable=True)
            self.logger.info(f"Agent queue oluşturuldu: {queue_name}")
            return True
        except Exception as e:
            self.logger.error(f"Agent queue oluşturma hatası: {e}")
            return False

    def declare_queue(self, queue_name: str, durable: bool = True) -> bool:
        """
        Queue oluştur veya var olanı kontrol et

        Args:
            queue_name: Queue adı
            durable: Kalıcı olup olmayacağı

        Returns:
            bool: İşlem başarılı ise True
        """
        if not self.channel:
            self.logger.error("Kanal mevcut değil. Önce connect() çağırın.")
            return False

        try:
            self.channel.queue_declare(queue=queue_name, durable=durable)
            self.logger.info(f"Queue oluşturuldu/kontrol edildi: {queue_name}")
            return True
        except Exception as e:
            self.logger.error(f"Queue oluşturma hatası: {e}")
            return False

    def publish_message(self,
                       target_queue: str,
                       message: OrionMessage) -> bool:
        """
        Mesaj gönder

        Args:
            target_queue: Hedef queue adı
            message: Gönderilecek OrionMessage

        Returns:
            bool: Gönderim başarılı ise True
        """
        if not self.is_connected or not self.channel:
            self.logger.error("Bağlantı mevcut değil. Önce connect() çağırın.")
            return False

        try:
            # Mesaj gönderen bilgisini güncelle
            message.sender_id = self.agent_id
            if message.timestamp is None:
                message.timestamp = datetime.datetime.now().isoformat()

            # JSON formatına çevir
            message_body = message.to_json()

            # Mesajı gönder
            self.channel.basic_publish(
                exchange='',
                routing_key=target_queue,
                body=message_body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mesajı kalıcı yap
                    content_type='application/json',
                    content_encoding='utf-8',
                    priority=self._get_priority_value(message.priority)
                )
            )

            self.stats['messages_sent'] += 1
            self.logger.info(f"Mesaj gönderildi: {target_queue} -> {message.message_type}")
            return True

        except Exception as e:
            self.logger.error(f"Mesaj gönderme hatası: {e}")
            return False

    def _get_priority_value(self, priority: str) -> int:
        """Mesaj önceliğini sayısal değere çevir"""
        priority_map = {
            MessagePriority.LOW.value: 1,
            MessagePriority.NORMAL.value: 5,
            MessagePriority.HIGH.value: 8,
            MessagePriority.CRITICAL.value: 10
        }
        return priority_map.get(priority, 5)

    def register_message_handler(self,
                                message_type: str,
                                handler: Callable[[OrionMessage], None]):
        """
        Mesaj tipi için handler kaydet

        Args:
            message_type: Mesaj tipi
            handler: Handler fonksiyonu
        """
        self.message_handlers[message_type] = handler
        self.logger.info(f"Handler kaydedildi: {message_type}")

    def consume_messages(self,
                       queue_name: Optional[str] = None,
                       auto_ack: bool = False,
                       prefetch_count: int = 1) -> bool:
        """
        Mesaj dinlemeye başla

        Args:
            queue_name: Dinlenecek queue adı (None ise agent'ın kendi queue'su)
            auto_ack: Otomatik acknowledgment
            prefetch_count: Aynı anda işlenecek mesaj sayısı

        Returns:
            bool: Başlatma başarılı ise True
        """
        if not self.is_connected or not self.channel:
            self.logger.error("Bağlantı mevcut değil. Önce connect() çağırın.")
            return False

        if queue_name is None:
            queue_name = f"orion.agent.{self.agent_id}"

        try:
            # Queue'nun var olduğundan emin ol
            self.declare_queue(queue_name)

            # QoS ayarla
            self.channel.basic_qos(prefetch_count=prefetch_count)

            # Consumer'ı ayarla
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._message_callback,
                auto_ack=auto_ack
            )

            self.is_consuming = True
            self.logger.info(f"Mesaj dinleme başlatıldı: {queue_name}")

            # Ayrı thread'de consuming başlat
            self.stop_consuming = False
            self.consumer_thread = threading.Thread(
                target=self._consume_worker,
                name=f"Consumer-{self.agent_id}",
                daemon=True
            )
            self.consumer_thread.start()

            return True

        except Exception as e:
            self.logger.error(f"Mesaj dinleme başlatma hatası: {e}")
            return False

    def _consume_worker(self):
        """Consumer worker thread"""
        try:
            while not self.stop_consuming and self.is_connected:
                try:
                    # Process data events with timeout
                    if self.connection and not self.connection.is_closed:
                        self.connection.process_data_events(time_limit=1)
                    else:
                        break
                except Exception as e:
                    self.logger.error(f"Message processing error: {e}")
                    if not self.auto_reconnect:
                        break
                    time.sleep(1)

        except Exception as e:
            self.logger.error(f"Consumer worker error: {e}")
        finally:
            self.is_consuming = False
            self.logger.info("Consumer worker stopped")

    def _message_callback(self, channel, method, properties, body):
        """
        Gelen mesajları işleyen callback fonksiyonu

        Args:
            channel: RabbitMQ kanalı
            method: Mesaj metodu
            properties: Mesaj özellikleri
            body: Mesaj içeriği
        """
        try:
            self.stats['messages_received'] += 1

            # Mesajı JSON olarak parse et
            message_data = json.loads(body.decode('utf-8'))
            message = OrionMessage.from_dict(message_data)

            self.logger.info(f"Mesaj alındı: {message.message_type} from {message.sender_id}")

            # Mesaj tipine göre handler çağır
            message_type = message.message_type
            if message_type in self.message_handlers:
                try:
                    self.message_handlers[message_type](message)
                except Exception as e:
                    self.logger.error(f"Message handler error for {message_type}: {e}")
            else:
                # Default handler
                self._default_message_handler(message)

            # Manual acknowledgment (eğer auto_ack False ise)
            if not properties.headers or not properties.headers.get('auto_ack', False):
                channel.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse hatası: {e}")
            self.logger.error(f"Raw message: {body}")
            # Hatalı mesajı reject et
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            self.logger.error(f"Mesaj işleme hatası: {e}")
            # Hata durumunda mesajı reject et
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _default_message_handler(self, message: OrionMessage):
        """
        Varsayılan mesaj handler'ı

        Args:
            message: Gelen mesaj
        """
        self.logger.info(f"Default handler - Message: {message.message_type}")
        self.logger.info(f"Content: {message.content}")
        self.logger.info(f"From: {message.sender_id}")
        if message.target_agent:
            self.logger.info(f"Target: {message.target_agent}")

    def stop_consuming_messages(self):
        """Mesaj dinlemeyi durdur"""
        try:
            self.stop_consuming = True
            self.is_consuming = False

            if self.channel and not self.channel.is_closed:
                self.channel.stop_consuming()

            if self.consumer_thread and self.consumer_thread.is_alive():
                self.consumer_thread.join(timeout=5)

            self.logger.info("Mesaj dinleme durduruldu")

        except Exception as e:
            self.logger.error(f"Mesaj dinleme durdurma hatası: {e}")

    def send_heartbeat(self):
        """Heartbeat mesajı gönder"""
        heartbeat_msg = OrionMessage(
            message_type=MessageType.HEARTBEAT.value,
            content=f"Agent {self.agent_id} aktif",
            sender_id=self.agent_id,
            priority=MessagePriority.LOW.value,
            metadata={
                'stats': self.stats,
                'uptime': time.time()
            }
        )

        heartbeat_queue = "orion.system.heartbeat"
        self.declare_queue(heartbeat_queue)
        success = self.publish_message(heartbeat_queue, heartbeat_msg)

        if success:
            self.stats['last_heartbeat'] = datetime.datetime.now().isoformat()

        return success

    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        return {
            'agent_id': self.agent_id,
            'is_connected': self.is_connected,
            'is_consuming': self.is_consuming,
            **self.stats
        }

    def __enter__(self):
        """Context manager desteği"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği"""
        self.disconnect()


# Convenience functions
def create_message(message_type: str,
                  content: str,
                  sender_id: str,
                  target_agent: Optional[str] = None,
                  priority: str = MessagePriority.NORMAL.value,
                  **kwargs) -> OrionMessage:
    """
    Hızlı mesaj oluşturma fonksiyonu

    Args:
        message_type: Mesaj tipi
        content: Mesaj içeriği
        sender_id: Gönderen agent ID
        target_agent: Hedef agent ID (opsiyonel)
        priority: Mesaj önceliği
        **kwargs: Ek metadata

    Returns:
        OrionMessage: Oluşturulan mesaj
    """
    return OrionMessage(
        message_type=message_type,
        content=content,
        sender_id=sender_id,
        target_agent=target_agent,
        priority=priority,
        metadata=kwargs
    )
