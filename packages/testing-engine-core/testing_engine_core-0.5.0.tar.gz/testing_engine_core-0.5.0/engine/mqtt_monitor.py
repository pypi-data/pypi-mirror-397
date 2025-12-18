"""
MQTT Monitor - Monitor MQTT messages (Eclipse Mosquitto) during tests
"""

import json
import logging
import threading
import time
from typing import Any, Dict, List, Optional
from queue import Queue, Empty

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ paho-mqtt not installed. Install with: pip install paho-mqtt")

from .message_broker import MessageBroker
from .config import MQTTConfig

logger = logging.getLogger(__name__)


class MQTTMonitor(MessageBroker):
    """
    Monitor MQTT topics (Eclipse Mosquitto) and capture messages during tests.
    
    Features:
    - Subscribe to topics and capture messages
    - Assert messages with specific content
    - Wait for messages with timeout
    - Message filtering and counting
    - QoS support (0, 1, 2)
    """
    
    def __init__(self, config: MQTTConfig):
        if not MQTT_AVAILABLE:
            raise ImportError("paho-mqtt is required for MQTT support. Install with: pip install paho-mqtt")
        
        self.config = config
        self.client: Optional[mqtt.Client] = None
        self.captured_messages: Dict[str, Queue] = {}
        self.subscribed_topics: set = set()
        self.connected = False
        self._lock = threading.Lock()
        self.connect()
    
    def connect(self):
        """Establish connection to MQTT broker (Mosquitto)"""
        try:
            # Create MQTT client
            self.client = mqtt.Client(
                client_id=self.config.client_id or f"testing_engine_{int(time.time())}",
                clean_session=self.config.clean_session
            )
            
            # Set credentials if provided
            if self.config.username and self.config.password:
                self.client.username_pw_set(self.config.username, self.config.password)
            
            # Set callbacks
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect
            
            # Connect to broker
            self.client.connect(
                host=self.config.host,
                port=self.config.port,
                keepalive=self.config.keepalive
            )
            
            # Start network loop in background
            self.client.loop_start()
            
            # Wait for connection
            timeout = 5
            start = time.time()
            while not self.connected and time.time() - start < timeout:
                time.sleep(0.1)
            
            if not self.connected:
                raise ConnectionError("Failed to connect to MQTT broker within timeout")
            
            logger.info(f"✅ Connected to MQTT broker: {self.config.host}:{self.config.port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MQTT broker: {e}")
            raise
    
    def disconnect(self):
        """Close connection to MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            logger.debug("MQTT connection established")
        else:
            logger.error(f"MQTT connection failed with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected MQTT disconnection: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            # Decode message payload
            payload_str = msg.payload.decode('utf-8')
            
            # Try to parse as JSON
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                payload = {"data": payload_str}
            
            # Add message metadata
            message = {
                "topic": msg.topic,
                "payload": payload,
                "qos": msg.qos,
                "retain": msg.retain,
                "timestamp": time.time()
            }
            
            # Store in queue for the topic
            with self._lock:
                if msg.topic in self.captured_messages:
                    self.captured_messages[msg.topic].put(message)
                    logger.debug(f"📨 Captured message on topic '{msg.topic}': {payload}")
        
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def subscribe(self, topic: str, callback=None):
        """
        Subscribe to an MQTT topic.
        
        Args:
            topic: MQTT topic to subscribe to (supports wildcards: +, #)
            callback: Optional callback function
        """
        if not self.connected:
            raise ConnectionError("Not connected to MQTT broker")
        
        with self._lock:
            if topic not in self.subscribed_topics:
                # Create message queue for this topic
                self.captured_messages[topic] = Queue()
                
                # Subscribe to topic
                result, mid = self.client.subscribe(topic, qos=self.config.qos)
                
                if result == mqtt.MQTT_ERR_SUCCESS:
                    self.subscribed_topics.add(topic)
                    logger.info(f"📡 Subscribed to MQTT topic: {topic}")
                else:
                    raise Exception(f"Failed to subscribe to topic: {topic}")
    
    def publish(self, topic: str, message: Any):
        """
        Publish a message to an MQTT topic.
        
        Args:
            topic: MQTT topic
            message: Message to publish (dict will be JSON serialized)
        """
        if not self.connected:
            raise ConnectionError("Not connected to MQTT broker")
        
        try:
            # Serialize message
            if isinstance(message, dict):
                payload = json.dumps(message)
            else:
                payload = str(message)
            
            # Publish
            result = self.client.publish(
                topic=topic,
                payload=payload,
                qos=self.config.qos,
                retain=False
            )
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"📤 Published to topic '{topic}': {message}")
            else:
                raise Exception(f"Failed to publish to topic: {topic}")
        
        except Exception as e:
            logger.error(f"Error publishing MQTT message: {e}")
            raise
    
    def get_message(self, topic: str, timeout: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get a message from a topic (non-blocking with timeout).
        
        Args:
            topic: MQTT topic
            timeout: Timeout in seconds
            
        Returns:
            Message data or None if timeout
        """
        # Ensure subscribed
        if topic not in self.subscribed_topics:
            self.subscribe(topic)
        
        try:
            message = self.captured_messages[topic].get(timeout=timeout)
            return message
        except Empty:
            return None
    
    def wait_for_message(self, topic: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Wait for a message on a topic.
        
        Args:
            topic: MQTT topic
            timeout: Timeout in seconds
            
        Returns:
            Message data or None if timeout
        """
        # Ensure subscribed
        if topic not in self.subscribed_topics:
            self.subscribe(topic)
        
        logger.info(f"⏳ Waiting for message on topic '{topic}' (timeout: {timeout}s)")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            message = self.get_message(topic, timeout=1)
            if message:
                logger.info(f"✅ Received message on topic '{topic}'")
                return message
        
        logger.warning(f"⚠️ Timeout waiting for message on topic '{topic}'")
        return None
    
    def assert_message(self, topic: str, expected_data: Dict[str, Any], timeout: int = 10) -> bool:
        """
        Assert that a message with expected data arrives.
        
        Args:
            topic: MQTT topic
            expected_data: Expected message content (partial match)
            timeout: Timeout in seconds
            
        Returns:
            True if message matches, False otherwise
        """
        message = self.wait_for_message(topic, timeout)
        
        if not message:
            logger.error(f"❌ No message received on topic '{topic}'")
            return False
        
        # Check if expected data is subset of received payload
        payload = message.get("payload", {})
        
        for key, expected_value in expected_data.items():
            if key not in payload:
                logger.error(f"❌ Key '{key}' not found in message payload")
                return False
            
            if payload[key] != expected_value:
                logger.error(f"❌ Value mismatch for '{key}': expected {expected_value}, got {payload[key]}")
                return False
        
        logger.info(f"✅ Message assertion passed for topic '{topic}'")
        return True
    
    def get_captured_messages(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get all captured messages for a topic.
        
        Args:
            topic: MQTT topic
            
        Returns:
            List of captured messages
        """
        if topic not in self.captured_messages:
            return []
        
        messages = []
        while not self.captured_messages[topic].empty():
            try:
                messages.append(self.captured_messages[topic].get_nowait())
            except Empty:
                break
        
        # Put messages back in queue
        for msg in messages:
            self.captured_messages[topic].put(msg)
        
        return messages
    
    def clear_captured_messages(self, topic: str):
        """
        Clear captured messages for a topic.
        
        Args:
            topic: MQTT topic
        """
        if topic in self.captured_messages:
            while not self.captured_messages[topic].empty():
                try:
                    self.captured_messages[topic].get_nowait()
                except Empty:
                    break
            logger.debug(f"Cleared captured messages for topic: {topic}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.disconnect()
