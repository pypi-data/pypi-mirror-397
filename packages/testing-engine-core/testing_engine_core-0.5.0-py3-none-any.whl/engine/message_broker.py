"""
Base Message Broker - Abstract interface for message brokers
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MessageBroker(ABC):
    """
    Abstract base class for message broker implementations.
    
    Supports different message brokers:
    - RabbitMQ (AMQP)
    - Eclipse Mosquitto (MQTT)
    - Other brokers can be added by implementing this interface
    """
    
    @abstractmethod
    def connect(self):
        """Establish connection to the message broker"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close connection to the message broker"""
        pass
    
    @abstractmethod
    def subscribe(self, topic: str, callback=None):
        """
        Subscribe to a topic/queue.
        
        Args:
            topic: Topic name or queue name
            callback: Optional callback function for messages
        """
        pass
    
    @abstractmethod
    def publish(self, topic: str, message: Any):
        """
        Publish a message to a topic/queue.
        
        Args:
            topic: Topic name or queue name
            message: Message to publish
        """
        pass
    
    @abstractmethod
    def get_message(self, topic: str, timeout: int = 1) -> Optional[Dict[str, Any]]:
        """
        Get a message from a topic/queue.
        
        Args:
            topic: Topic name or queue name
            timeout: Timeout in seconds
            
        Returns:
            Message data or None if timeout
        """
        pass
    
    @abstractmethod
    def wait_for_message(self, topic: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """
        Wait for a message on a topic/queue.
        
        Args:
            topic: Topic name or queue name
            timeout: Timeout in seconds
            
        Returns:
            Message data or None if timeout
        """
        pass
    
    @abstractmethod
    def assert_message(self, topic: str, expected_data: Dict[str, Any], timeout: int = 10) -> bool:
        """
        Assert that a message with expected data arrives.
        
        Args:
            topic: Topic name or queue name
            expected_data: Expected message content
            timeout: Timeout in seconds
            
        Returns:
            True if message matches, False otherwise
        """
        pass
    
    @abstractmethod
    def get_captured_messages(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get all captured messages for a topic/queue.
        
        Args:
            topic: Topic name or queue name
            
        Returns:
            List of captured messages
        """
        pass
    
    @abstractmethod
    def clear_captured_messages(self, topic: str):
        """
        Clear captured messages for a topic/queue.
        
        Args:
            topic: Topic name or queue name
        """
        pass
