"""
RabbitMQ Monitor - Monitor and assert RabbitMQ messages during tests
Implements the MessageBroker interface for AMQP protocol.
"""

import json
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

try:
    import pika
    from pika.exceptions import AMQPConnectionError
    PIKA_AVAILABLE = True
except ImportError:
    PIKA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ pika not installed. RabbitMQ monitoring will not be available.")

from .config import RabbitMQConfig
from .message_broker import MessageBroker

logger = logging.getLogger(__name__)


class RabbitMQMonitor(MessageBroker):
    """
    Monitor RabbitMQ queues and capture messages during tests.
    
    Implements MessageBroker interface for AMQP protocol.
    
    Features:
    - Subscribe to queues and capture messages
    - Publish messages to exchanges/queues
    - Assert messages with specific content
    - Wait for messages with timeout
    - Message filtering and counting
    - Background consumer thread
    """
    
    def __init__(self, config: RabbitMQConfig):
        """
        Initialize RabbitMQ monitor.
        
        Args:
            config: RabbitMQ configuration
        
        Raises:
            ImportError: If pika library not installed
        """
        if not PIKA_AVAILABLE:
            raise ImportError(
                "pika library not installed. Install with: pip install pika"
            )
        
        self.config = config
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.captured_messages: Dict[str, List[Dict[str, Any]]] = {}
        self.consumer_threads: Dict[str, threading.Thread] = {}
        self.stop_flags: Dict[str, threading.Event] = {}
        self.connected = False
    
    def connect(self) -> None:
        """Establish connection to RabbitMQ"""
        try:
            credentials = pika.PlainCredentials(
                self.config.username,
                self.config.password
            )
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.vhost,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.connected = True
            logger.info(f"✅ Connected to RabbitMQ: {self.config.host}:{self.config.port}")
        except AMQPConnectionError as e:
            logger.error(f"❌ Failed to connect to RabbitMQ: {e}")
            self.connected = False
            raise ConnectionError(f"Failed to connect to RabbitMQ: {e}")
    
    def disconnect(self) -> None:
        """Close connection to RabbitMQ"""
        # Stop all consumers
        for queue_name in list(self.consumer_threads.keys()):
            self._stop_monitoring(queue_name)
        
        # Close connections
        if self.channel:
            try:
                self.channel.close()
            except Exception as e:
                logger.warning(f"⚠️ Error closing channel: {e}")
        
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                logger.warning(f"⚠️ Error closing connection: {e}")
        
        self.connected = False
        logger.info("🔌 RabbitMQ monitor disconnected")
    
    def subscribe(self, topic: str, callback: Optional[Callable] = None) -> None:
        """
        Start monitoring a queue in a background thread.
        
        Args:
            topic: Queue name to subscribe to (in AMQP, topics are queues)
            callback: Optional callback function (not used, messages captured automatically)
        """
        if not self.connected:
            raise ConnectionError("Not connected to RabbitMQ. Call connect() first.")
        
        queue_name = topic
        
        if queue_name in self.consumer_threads:
            logger.warning(f"⚠️ Already monitoring queue: {queue_name}")
            return
        
        self.captured_messages[queue_name] = []
        self.stop_flags[queue_name] = threading.Event()
        
        thread = threading.Thread(
            target=self._consume_messages,
            args=(queue_name,),
            daemon=True
        )
        thread.start()
        self.consumer_threads[queue_name] = thread
        
        logger.info(f"🎧 Started monitoring queue: {queue_name}")
    
    def publish(self, topic: str, message: Dict[str, Any]) -> None:
        """
        Publish a message to a queue.
        
        Args:
            topic: Queue name to publish to
            message: Message payload (will be JSON serialized)
        """
        if not self.connected:
            raise ConnectionError("Not connected to RabbitMQ. Call connect() first.")
        
        try:
            # Ensure queue exists
            self.channel.queue_declare(queue=topic, durable=True)
            
            # Publish message
            body = json.dumps(message)
            self.channel.basic_publish(
                exchange='',
                routing_key=topic,
                body=body,
                properties=pika.BasicProperties(
                    content_type='application/json',
                    delivery_mode=2  # Persistent
                )
            )
            logger.info(f"📤 Published message to queue {topic}: {message}")
        except Exception as e:
            logger.error(f"❌ Failed to publish message to {topic}: {e}")
            raise
    
    def get_message(self, topic: str, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """
        Get a single message from captured messages (non-blocking with timeout).
        
        Args:
            topic: Queue name
            timeout: Maximum time to wait for a message (seconds)
        
        Returns:
            Message dict or None if no message available
        """
        queue_name = topic
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.captured_messages.get(queue_name, [])
            if messages:
                # Return the first message (FIFO)
                message = messages[0]
                return {
                    "topic": queue_name,
                    "payload": message.get("body", {}),
                    "routing_key": message.get("routing_key"),
                    "properties": message.get("properties", {})
                }
            time.sleep(0.1)
        
        return None
    
    def wait_for_message(self, topic: str, timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """
        Wait for a message on a specific topic/queue.
        
        Args:
            topic: Queue name to wait for message on
            timeout: Maximum time to wait in seconds
        
        Returns:
            Message dict with keys: topic, payload, routing_key, properties
            None if timeout expires
        """
        queue_name = topic
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.captured_messages.get(queue_name, [])
            if messages:
                message = messages[0]
                logger.info(f"✅ Found message in queue {queue_name}")
                return {
                    "topic": queue_name,
                    "payload": message.get("body", {}),
                    "routing_key": message.get("routing_key"),
                    "properties": message.get("properties", {})
                }
            time.sleep(0.5)
        
        logger.warning(f"⚠️ No message found in {queue_name} within {timeout} seconds")
        return None
    
    def assert_message(
        self,
        topic: str,
        expected_data: Dict[str, Any],
        timeout: float = 10.0
    ) -> bool:
        """
        Assert that a message with specific content exists.
        
        Args:
            topic: Queue name to check
            expected_data: Expected message data (partial match)
            timeout: Maximum time to wait in seconds
        
        Returns:
            True if message found, False otherwise
        
        Raises:
            AssertionError: If message not found within timeout
        """
        queue_name = topic
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            messages = self.captured_messages.get(queue_name, [])
            
            for message in messages:
                body = message.get("body", {})
                # Check if all expected key-value pairs match
                if all(body.get(k) == v for k, v in expected_data.items()):
                    logger.info(f"✅ Message assertion passed for {queue_name}")
                    return True
            
            time.sleep(0.5)
        
        raise AssertionError(
            f"❌ Expected message not found in {queue_name}: {expected_data}"
        )
    
    def get_captured_messages(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get all captured messages from a queue.
        
        Args:
            topic: Queue name
        
        Returns:
            List of captured messages with format:
            [{"topic": str, "payload": dict, "routing_key": str, "properties": dict}, ...]
        """
        queue_name = topic
        messages = self.captured_messages.get(queue_name, [])
        
        return [
            {
                "topic": queue_name,
                "payload": msg.get("body", {}),
                "routing_key": msg.get("routing_key"),
                "properties": msg.get("properties", {})
            }
            for msg in messages
        ]
    
    def clear_captured_messages(self, topic: str) -> None:
        """
        Clear captured messages for a queue.
        
        Args:
            topic: Queue name
        """
        queue_name = topic
        self.captured_messages[queue_name] = []
        logger.debug(f"🧹 Cleared messages for {queue_name}")
    
    # Internal methods (not part of MessageBroker interface)
    
    def _consume_messages(self, queue_name: str):
        """
        Background consumer for a specific queue.
        
        Args:
            queue_name: Queue to consume from
        """
        try:
            # Create a new connection for this thread
            credentials = pika.PlainCredentials(
                self.config.username,
                self.config.password
            )
            parameters = pika.ConnectionParameters(
                host=self.config.host,
                port=self.config.port,
                virtual_host=self.config.vhost,
                credentials=credentials
            )
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # Declare queue (creates if doesn't exist)
            channel.queue_declare(queue=queue_name, durable=True)
            
            def callback(ch, method, properties, body):
                """Message callback"""
                try:
                    message = json.loads(body.decode())
                    self.captured_messages[queue_name].append({
                        "routing_key": method.routing_key,
                        "body": message,
                        "properties": {
                            "content_type": properties.content_type,
                            "delivery_mode": properties.delivery_mode,
                            "timestamp": properties.timestamp,
                        }
                    })
                    logger.debug(f"📨 Captured message from {queue_name}: {message}")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception as e:
                    logger.error(f"❌ Error processing message: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag)
            
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=callback,
                auto_ack=False
            )
            
            logger.info(f"🎧 Consumer started for queue: {queue_name}")
            
            # Consume messages until stop flag is set
            while not self.stop_flags[queue_name].is_set():
                connection.process_data_events(time_limit=1)
            
            channel.close()
            connection.close()
            logger.info(f"🛑 Consumer stopped for queue: {queue_name}")
            
        except Exception as e:
            logger.error(f"❌ Consumer error for {queue_name}: {e}")
    
    def _stop_monitoring(self, queue_name: str):
        """
        Stop monitoring a queue.
        
        Args:
            queue_name: Queue to stop monitoring
        """
        if queue_name not in self.consumer_threads:
            return
        
        self.stop_flags[queue_name].set()
        self.consumer_threads[queue_name].join(timeout=5)
        
        del self.consumer_threads[queue_name]
        del self.stop_flags[queue_name]
        
        logger.info(f"🛑 Stopped monitoring queue: {queue_name}")
    
    # Legacy methods for backward compatibility
    
    def start_monitoring(self, queue_name: str):
        """Legacy method - use subscribe() instead"""
        self.subscribe(queue_name)
    
    def stop_monitoring(self, queue_name: str):
        """Legacy method"""
        self._stop_monitoring(queue_name)
    
    def get_messages(self, queue_name: str) -> List[Dict[str, Any]]:
        """Legacy method - use get_captured_messages() instead"""
        messages = self.captured_messages.get(queue_name, [])
        return [msg.get("body", {}) for msg in messages]
    
    def assert_message_published(
        self,
        queue_name: str,
        expected_body: Dict[str, Any],
        timeout: int = 10
    ) -> Dict[str, Any]:
        """Legacy method - use assert_message() instead"""
        self.assert_message(queue_name, expected_body, timeout)
        # Return the matching message
        messages = self.captured_messages.get(queue_name, [])
        for message in messages:
            body = message.get("body", {})
            if all(body.get(k) == v for k, v in expected_body.items()):
                return message
        return {}
    
    def assert_message_count(self, queue_name: str, expected_count: int) -> int:
        """
        Assert that the number of captured messages matches expected count.
        
        Args:
            queue_name: Queue to check
            expected_count: Expected number of messages
        
        Returns:
            Actual count
        
        Raises:
            AssertionError: If count doesn't match
        """
        actual_count = len(self.captured_messages.get(queue_name, []))
        
        if actual_count != expected_count:
            raise AssertionError(
                f"❌ Message count mismatch in {queue_name}: expected {expected_count}, got {actual_count}"
            )
        
        logger.info(f"✅ Message count matches: {actual_count} in {queue_name}")
        return actual_count
    
    def clear_messages(self, queue_name: str):
        """Legacy method - use clear_captured_messages() instead"""
        self.clear_captured_messages(queue_name)
    
    def close(self):
        """Legacy method - use disconnect() instead"""
        self.disconnect()
