"""
Test Orchestrator - Coordinate test execution with all components
"""

import logging
import time
from typing import Any, Dict, Optional, Callable

from .config import EngineConfig
from .db_inspector import DatabaseInspector
from .queue_monitor import QueueMonitor  # Legacy import for backward compatibility
from .rabbitmq_monitor import RabbitMQMonitor
from .mqtt_monitor import MQTTMonitor
from .message_broker import MessageBroker
from .scenario import TestScenario, TestStep, StepType
from .clients import (
    BaseServiceClient,
    GenericServiceClient
)

logger = logging.getLogger(__name__)


class TestOrchestrator:
    """
    Orchestrate E2E test execution.
    
    Coordinates:
    - Service HTTP clients
    - Database inspection
    - Message queue monitoring
    - Test scenario execution
    
    Features:
    - Execute declarative test scenarios
    - Wait for async events
    - Assert database state
    - Validate message flow
    - Cleanup test data
    """
    
    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig.from_env()
        
        # Initialize components
        self.db_inspector = DatabaseInspector(self.config.database)
        
        # Initialize message broker based on configuration
        self.broker: MessageBroker = self._create_message_broker()
        
        # Legacy attribute for backward compatibility
        self.queue_monitor = self.broker
        
        # Dynamic service registry
        self.services: Dict[str, BaseServiceClient] = {}
        
        # Custom step handlers registry
        self.custom_step_handlers: Dict[str, Callable] = {}
        
        # Register services from config (backward compatible)
        self._register_services_from_config()
        
        logger.info(f"✅ Test orchestrator initialized (broker: {self.config.broker_type})")
    
    def _create_message_broker(self) -> MessageBroker:
        """
        Create the appropriate message broker based on configuration.
        
        Returns:
            MessageBroker instance (RabbitMQMonitor or MQTTMonitor)
        
        Raises:
            ValueError: If broker_type is invalid
        """
        if self.config.broker_type == "rabbitmq":
            broker = RabbitMQMonitor(self.config.rabbitmq)
            broker.connect()
            logger.info("✅ Using RabbitMQ (AMQP) message broker")
            return broker
        elif self.config.broker_type == "mqtt":
            broker = MQTTMonitor(self.config.mqtt)
            broker.connect()
            logger.info("✅ Using MQTT message broker")
            return broker
        else:
            raise ValueError(
                f"Invalid broker_type: {self.config.broker_type}. "
                f"Must be 'rabbitmq' or 'mqtt'"
            )
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        self.close()
        return False
    
    def _register_services_from_config(self):
        """
        Auto-register services from configuration.
        
        Uses GenericServiceClient for all services - fully universal and reusable.
        """
        services_dict = self.config.services.to_dict()
        
        # Register all services as generic clients (universal approach)
        for service_name, service_url in services_dict.items():
            self.register_service(
                service_name,
                GenericServiceClient(
                    service_url,
                    timeout=self.config.test.timeout,
                    retry_attempts=self.config.test.retry_attempts
                )
            )
    
    def register_service(self, name: str, client: BaseServiceClient):
        """
        Register a service client dynamically.
        
        Args:
            name: Service name (used in test scenarios)
            client: Service client instance
        
        Example:
            orchestrator.register_service(
                "product",
                GenericServiceClient("http://localhost:9000")
            )
        """
        self.services[name] = client
        logger.info(f"📝 Registered service: {name} -> {client.base_url}")
    
    def register_step_handler(self, step_type: str, handler: Callable):
        """
        Register a custom step handler.
        
        Allows extending the orchestrator with custom step types beyond the built-in ones.
        
        Args:
            step_type: Custom step type identifier
            handler: Callable that handles the step (receives TestStep as argument)
        
        Example:
            def handle_kafka_message(step: TestStep):
                topic = step.params["topic"]
                message = step.params["message"]
                # ... send to Kafka
            
            orchestrator.register_step_handler("kafka_publish", handle_kafka_message)
        """
        self.custom_step_handlers[step_type] = handler
        logger.info(f"📝 Registered custom step handler: {step_type}")
    
    def check_services_health(self) -> Dict[str, bool]:
        """
        Check health of all services.
        
        Returns:
            Dictionary of service_name: is_healthy
        """
        health_status = {}
        
        for name, client in self.services.items():
            health_status[name] = client.health_check()
        
        all_healthy = all(health_status.values())
        
        if all_healthy:
            logger.info("✅ All services are healthy")
        else:
            unhealthy = [name for name, healthy in health_status.items() if not healthy]
            logger.warning(f"⚠️ Unhealthy services: {unhealthy}")
        
        return health_status
    
    def execute_scenario(self, scenario: TestScenario) -> Dict[str, Any]:
        """
        Execute a test scenario.
        
        Args:
            scenario: Test scenario to execute
        
        Returns:
            Execution results dictionary
        
        Raises:
            Exception: If scenario execution fails
        """
        logger.info(f"🚀 Executing scenario: {scenario.name}")
        start_time = time.time()
        
        results = {
            "scenario": scenario.name,
            "status": "running",
            "steps": [],
            "duration": 0,
            "error": None
        }
        
        try:
            # Execute setup steps
            for step in scenario.setup_steps:
                self._execute_step(step, results)
            
            # Execute main steps
            for step in scenario.steps:
                self._execute_step(step, results)
            
            # Mark as passed
            results["status"] = "passed"
            logger.info(f"✅ Scenario passed: {scenario.name}")
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            logger.error(f"❌ Scenario failed: {scenario.name} - {e}")
            raise
        
        finally:
            # Execute teardown steps
            for step in scenario.teardown_steps:
                try:
                    self._execute_step(step, results)
                except Exception as e:
                    logger.warning(f"⚠️ Teardown step failed: {e}")
            
            # Calculate duration
            results["duration"] = time.time() - start_time
            logger.info(f"⏱️ Scenario duration: {results['duration']:.2f}s")
        
        return results
    
    def _execute_step(self, step: TestStep, results: Dict[str, Any]):
        """
        Execute a single test step.
        
        Args:
            step: Test step to execute
            results: Results dictionary to update
        """
        logger.info(f"▶️ Executing: {step.description}")
        step_start = time.time()
        
        step_result = {
            "description": step.description,
            "type": step.type.value,
            "status": "running",
            "duration": 0,
            "error": None
        }
        
        try:
            if step.type == StepType.HTTP_REQUEST:
                self._execute_http_request(step)
            
            elif step.type == StepType.WAIT_FOR_MESSAGE:
                self._execute_wait_for_message(step)
            
            elif step.type == StepType.ASSERT_MESSAGE:
                self._execute_assert_message(step)
            
            elif step.type == StepType.ASSERT_DATABASE:
                self._execute_assert_database(step)
            
            elif step.type == StepType.SLEEP:
                time.sleep(step.params["seconds"])
            
            elif step.type == StepType.CUSTOM:
                # Check for custom step handlers first
                custom_type = step.params.get("custom_type")
                if custom_type and custom_type in self.custom_step_handlers:
                    self.custom_step_handlers[custom_type](step)
                elif "func" in step.params:
                    # Fallback to old style function parameter
                    step.params["func"]()
                else:
                    raise ValueError(f"Custom step missing 'func' or unregistered 'custom_type': {custom_type}")
            
            step_result["status"] = "passed"
            logger.info(f"✅ Step passed: {step.description}")
            
        except Exception as e:
            step_result["status"] = "failed"
            step_result["error"] = str(e)
            logger.error(f"❌ Step failed: {step.description} - {e}")
            
            if not step.skip_on_failure:
                results["steps"].append(step_result)
                raise
        
        finally:
            step_result["duration"] = time.time() - step_start
            results["steps"].append(step_result)
    
    def _execute_http_request(self, step: TestStep):
        """Execute HTTP request step"""
        params = step.params
        service = self.services.get(params["service"])
        
        if not service:
            raise ValueError(f"Unknown service: {params['service']}")
        
        method = params["method"].lower()
        endpoint = params["endpoint"]
        data = params.get("data")
        expected_status = params.get("expected_status", 200)
        
        # Make request
        if method == "get":
            response = service.get(endpoint)
        elif method == "post":
            response = service.post(endpoint, data=data)
        elif method == "put":
            response = service.put(endpoint, data=data)
        elif method == "delete":
            response = service.delete(endpoint)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Validate status code
        if response.status_code != expected_status:
            raise AssertionError(
                f"Unexpected status code: expected {expected_status}, got {response.status_code}"
            )
    
    def _execute_wait_for_message(self, step: TestStep):
        """Execute wait for message step"""
        params = step.params
        queue = params["queue"]
        contains = params.get("contains", {})
        timeout = step.timeout or self.config.test.message_wait_timeout
        
        # Start monitoring if not already (using subscribe from MessageBroker interface)
        try:
            self.broker.subscribe(queue)
        except Exception:
            pass  # Already subscribed
        
        # Wait for matching message
        def filter_func(message: Dict[str, Any]) -> bool:
            body = message.get("body", {})
            return all(body.get(k) == v for k, v in contains.items())
        
        # For backward compatibility with old QueueMonitor API
        if hasattr(self.broker, 'wait_for_message') and hasattr(self.broker, 'captured_messages'):
            self.broker.wait_for_message(queue, filter_func, timeout)
        else:
            # Use MessageBroker interface
            self.broker.wait_for_message(queue, timeout)
    
    def _execute_assert_message(self, step: TestStep):
        """Execute assert message step"""
        params = step.params
        queue = params["queue"]
        expected_body = params["expected_body"]
        timeout = step.timeout or self.config.test.message_wait_timeout
        
        # Start monitoring if not already
        try:
            self.broker.subscribe(queue)
        except Exception:
            pass  # Already subscribed
        
        # Assert message exists (using MessageBroker interface)
        self.broker.assert_message(queue, expected_body, timeout)
    
    def _execute_assert_database(self, step: TestStep):
        """Execute database assertion step"""
        params = step.params
        table = params["table"]
        conditions = params["conditions"]
        timeout = step.timeout or self.config.test.db_query_timeout
        
        # Assert record exists
        self.db_inspector.assert_record_exists(table, conditions, timeout)
    
    def start_queue_monitoring(self, *queues: str):
        """Start monitoring multiple queues/topics"""
        for queue in queues:
            try:
                self.broker.subscribe(queue)
            except Exception as e:
                logger.warning(f"⚠️ Could not subscribe to {queue}: {e}")
    
    def stop_queue_monitoring(self, *queues: str):
        """Stop monitoring multiple queues/topics"""
        for queue in queues:
            # Legacy method for backward compatibility with RabbitMQMonitor
            if hasattr(self.broker, 'stop_monitoring'):
                try:
                    self.broker.stop_monitoring(queue)
                except Exception as e:
                    logger.warning(f"⚠️ Could not stop monitoring {queue}: {e}")
    
    def cleanup(self, email_pattern: str = "test_%"):
        """
        Clean up test data.
        
        Args:
            email_pattern: Email pattern for test users
        """
        if self.config.test.cleanup_after_test:
            logger.info("🧹 Cleaning up test data")
            self.db_inspector.cleanup_test_data(email_pattern)
    
    def close(self):
        """Close all connections"""
        logger.info("🔌 Closing orchestrator connections")
        self.db_inspector.close()
        self.broker.disconnect()
