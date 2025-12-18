"""
Configuration for Testing Engine
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration"""
    host: str = "localhost"
    port: int = 5432
    username: str = "testuser"
    password: str = "testpass"
    database: str = "testdb"
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class RabbitMQConfig:
    """RabbitMQ configuration"""
    host: str = "localhost"
    port: int = 5672
    username: str = "testuser"
    password: str = "testpass"
    vhost: str = "/"
    management_port: int = 15672
    
    @property
    def connection_string(self) -> str:
        return f"amqp://{self.username}:{self.password}@{self.host}:{self.port}/{self.vhost}"


@dataclass
class MQTTConfig:
    """MQTT configuration for Eclipse Mosquitto or other MQTT brokers"""
    host: str = "localhost"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None  # Auto-generated if None
    qos: int = 1  # Quality of Service: 0 (at most once), 1 (at least once), 2 (exactly once)
    keepalive: int = 60  # Keepalive interval in seconds
    clean_session: bool = True  # Start with clean session
    
    @property
    def connection_string(self) -> str:
        """Build MQTT connection string"""
        if self.username and self.password:
            return f"mqtt://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"mqtt://{self.host}:{self.port}"


@dataclass
class ServiceConfig:
    """Service endpoint configuration for dynamic service registration"""
    # Dynamic services dictionary - supports any service names and URLs
    _services_dict: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        """Initialize services dictionary for backward compatibility"""
        if self._services_dict is None:
            self._services_dict = {}
    
    @classmethod
    def from_dict(cls, services: Dict[str, str]) -> "ServiceConfig":
        """
        Create ServiceConfig from a dictionary of service names to URLs.
        
        Args:
            services: Dictionary mapping service names to URLs
                     e.g., {"user": "http://localhost:8001", "product": "http://localhost:9000"}
        
        Returns:
            ServiceConfig instance
        """
        instance = cls()
        instance._services_dict = services.copy()
        return instance
    
    def to_dict(self) -> Dict[str, str]:
        """
        Convert to dictionary format.
        
        Returns:
            Dictionary of service name to URL mappings
        """
        return self._services_dict.copy() if self._services_dict else {}
    
    def get(self, service_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get service URL by name.
        
        Args:
            service_name: Name of the service
            default: Default value if service not found
        
        Returns:
            Service URL or default
        """
        if self._services_dict:
            return self._services_dict.get(service_name, default)
        return default


@dataclass
class TestConfig:
    """Test execution configuration"""
    timeout: int = 30  # seconds
    retry_attempts: int = 3
    retry_delay: int = 1  # seconds
    message_wait_timeout: int = 10  # seconds
    db_query_timeout: int = 5  # seconds
    cleanup_after_test: bool = True
    verbose: bool = True


class EngineConfig:
    """Main configuration for Testing Engine"""
    
    def __init__(
        self,
        database: Optional[DatabaseConfig] = None,
        rabbitmq: Optional[RabbitMQConfig] = None,
        mqtt: Optional[MQTTConfig] = None,
        services: Optional[ServiceConfig] = None,
        test: Optional[TestConfig] = None,
        broker_type: str = "rabbitmq"  # "rabbitmq" or "mqtt"
    ):
        self.database = database or DatabaseConfig()
        self.rabbitmq = rabbitmq or RabbitMQConfig()
        self.mqtt = mqtt or MQTTConfig()
        self.services = services or ServiceConfig()
        self.test = test or TestConfig()
        self.broker_type = broker_type.lower()
        
        # Validate broker type
        if self.broker_type not in ["rabbitmq", "mqtt"]:
            raise ValueError(f"Invalid broker_type: {self.broker_type}. Must be 'rabbitmq' or 'mqtt'")
    
    @classmethod
    def from_env(cls) -> "EngineConfig":
        """Load configuration from environment variables"""
        broker_type = os.getenv("BROKER_TYPE", "rabbitmq").lower()
        
        return cls(
            database=DatabaseConfig(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "5432")),
                username=os.getenv("DB_USER", "testuser"),
                password=os.getenv("DB_PASSWORD", "testpass"),
                database=os.getenv("DB_NAME", "testdb"),
            ),
            rabbitmq=RabbitMQConfig(
                host=os.getenv("RABBITMQ_HOST", "localhost"),
                port=int(os.getenv("RABBITMQ_PORT", "5672")),
                username=os.getenv("RABBITMQ_USER", "testuser"),
                password=os.getenv("RABBITMQ_PASSWORD", "testpass"),
            ),
            mqtt=MQTTConfig(
                host=os.getenv("MQTT_HOST", "localhost"),
                port=int(os.getenv("MQTT_PORT", "1883")),
                username=os.getenv("MQTT_USER"),
                password=os.getenv("MQTT_PASSWORD"),
                client_id=os.getenv("MQTT_CLIENT_ID"),
                qos=int(os.getenv("MQTT_QOS", "1")),
                keepalive=int(os.getenv("MQTT_KEEPALIVE", "60")),
                clean_session=os.getenv("MQTT_CLEAN_SESSION", "true").lower() == "true",
            ),
            services=ServiceConfig.from_dict({}),  # Services must be configured via from_dict or environment detection
            test=TestConfig(
                timeout=int(os.getenv("TEST_TIMEOUT", "30")),
                retry_attempts=int(os.getenv("TEST_RETRY_ATTEMPTS", "3")),
                message_wait_timeout=int(os.getenv("MESSAGE_WAIT_TIMEOUT", "10")),
                cleanup_after_test=os.getenv("CLEANUP_AFTER_TEST", "true").lower() == "true",
                verbose=os.getenv("VERBOSE", "true").lower() == "true",
            ),
            broker_type=broker_type,
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "EngineConfig":
        """
        Create configuration from a dictionary.
        
        This allows flexible configuration for any microservices architecture.
        
        Args:
            config_dict: Configuration dictionary with keys:
                - services: Dict[str, str] - service name to URL mapping
                - database: Optional dict with db connection params
                - rabbitmq: Optional dict with rabbitmq connection params
                - mqtt: Optional dict with mqtt connection params
                - test: Optional dict with test execution params
                - broker_type: "rabbitmq" or "mqtt" (default: "rabbitmq")
        
        Returns:
            EngineConfig instance
        
        Example (RabbitMQ):
            config = EngineConfig.from_dict({
                "services": {
                    "user": "http://localhost:8001",
                    "product": "http://localhost:9000",
                },
                "broker_type": "rabbitmq",
                "rabbitmq": {
                    "host": "localhost",
                    "port": 5672
                }
            })
        
        Example (MQTT):
            config = EngineConfig.from_dict({
                "services": {
                    "user": "http://localhost:8001",
                    "product": "http://localhost:9000",
                },
                "broker_type": "mqtt",
                "mqtt": {
                    "host": "localhost",
                    "port": 1883,
                    "username": "mqtt_user",
                    "password": "mqtt_pass",
                    "qos": 1
                }
            })
        """
        # Handle services
        services_data = config_dict.get("services", {})
        if isinstance(services_data, dict):
            services = ServiceConfig.from_dict(services_data)
        else:
            services = ServiceConfig()
        
        # Handle database
        db_data = config_dict.get("database", {})
        database = DatabaseConfig(**db_data) if db_data else DatabaseConfig()
        
        # Handle rabbitmq
        mq_data = config_dict.get("rabbitmq", {})
        rabbitmq = RabbitMQConfig(**mq_data) if mq_data else RabbitMQConfig()
        
        # Handle mqtt
        mqtt_data = config_dict.get("mqtt", {})
        mqtt = MQTTConfig(**mqtt_data) if mqtt_data else MQTTConfig()
        
        # Handle test config
        test_data = config_dict.get("test", {})
        test = TestConfig(**test_data) if test_data else TestConfig()
        
        # Get broker type
        broker_type = config_dict.get("broker_type", "rabbitmq")
        
        return cls(
            database=database,
            rabbitmq=rabbitmq,
            mqtt=mqtt,
            services=services,
            test=test,
            broker_type=broker_type,
        )
