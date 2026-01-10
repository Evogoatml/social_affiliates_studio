# Integration Methods - Complete Guide

This document describes all three integration methods for connecting the suite orchestrator to larger management systems.

## 🎯 Integration Methods Overview

### Method 1: REST API Integration ⭐ Most Common
**Best for**: Web applications, CI/CD pipelines, monitoring dashboards

- **File**: `management_api.py`
- **Port**: 8080
- **Protocol**: HTTP/REST
- **Features**: REST endpoints, webhooks, metrics, health checks

### Method 2: Message Queue Integration ⭐ For Microservices
**Best for**: Microservices architectures, event-driven systems, distributed systems

- **File**: `message_queue_integration.py`
- **Protocol**: Redis/RabbitMQ/Kafka
- **Features**: Pub/sub, event streaming, command/response patterns

### Method 3: Plugin System ⭐ For Extensibility
**Best for**: Custom functionality, third-party integrations, extensible architectures

- **File**: `plugin_system.py`
- **Location**: `plugins/` directory
- **Features**: Hook system, custom metrics, config modification

---

## Method 1: REST API Integration

### Quick Start

```bash
# Start Management API
python management_api.py

# Access API
curl http://localhost:8080/api/health
```

### Use Cases

✅ **Kubernetes Operators**
- Health checks for liveness/readiness probes
- Service discovery integration
- Metrics scraping for Prometheus

✅ **CI/CD Pipelines**
- Start/stop services during deployment
- Health verification before traffic routing
- Integration tests

✅ **Monitoring Dashboards**
- Real-time service status
- Metrics collection
- Alerting integration

✅ **Infrastructure as Code**
- Terraform external data sources
- Ansible playbooks
- CloudFormation custom resources

### Example: Kubernetes Integration

```yaml
# Deployment with health checks
livenessProbe:
  httpGet:
    path: /api/health
    port: 8080
  initialDelaySeconds: 30

# Service discovery
apiVersion: v1
kind: Service
metadata:
  name: suite-management
spec:
  selector:
    app: suite-management
  ports:
    - port: 8080
```

### Example: CI/CD Integration

```yaml
# GitHub Actions
- name: Deploy Suite
  run: |
    curl -X POST http://localhost:8080/api/services/start \
      -H 'Content-Type: application/json' \
      -d '{"services": ["backend", "frontend"]}'
```

**See**: `integration_guide.md` for detailed examples

---

## Method 2: Message Queue Integration

### Quick Start

```python
from message_queue_integration import MessageQueueIntegration, QueueConfig, QueueType
from suite_orchestrator import SuiteOrchestrator

# Setup
config = QueueConfig(
    queue_type=QueueType.REDIS,
    host="localhost",
    port=6379
)

queue = MessageQueueIntegration(config)
orchestrator = SuiteOrchestrator()
bridge = OrchestratorQueueBridge(orchestrator, queue)

# Connect
await bridge.setup()
```

### Use Cases

✅ **Microservices Communication**
- Service mesh integration
- Event-driven architectures
- Distributed system coordination

✅ **Event Streaming**
- Real-time event processing
- Event sourcing patterns
- CQRS implementations

✅ **Multi-System Integration**
- Multiple management systems
- Cross-platform coordination
- Decoupled service management

### Supported Queues

1. **Redis** (Pub/Sub)
   ```python
   config = QueueConfig(
       queue_type=QueueType.REDIS,
       host="localhost",
       port=6379
   )
   ```

2. **RabbitMQ** (AMQP)
   ```python
   config = QueueConfig(
       queue_type=QueueType.RABBITMQ,
       host="localhost",
       port=5672,
       username="guest",
       password="guest",
       exchange="suite_events"
   )
   ```

3. **Kafka** (Planned)
   ```python
   # Coming soon
   config = QueueConfig(
       queue_type=QueueType.KAFKA,
       host="localhost",
       port=9092
   )
   ```

### Example: Redis Integration

```python
import asyncio
from message_queue_integration import *

async def main():
    # Setup queue
    config = QueueConfig(QueueType.REDIS, host="localhost", port=6379)
    queue = MessageQueueIntegration(config)
    await queue.connect()
    
    # Subscribe to events
    async def handle_event(data):
        print(f"Received event: {data}")
    
    await queue.subscribe("suite.service_started", handle_event)
    
    # Publish command
    await queue.publish("suite.control.start", {
        "services": ["backend", "frontend"]
    })
    
    # Keep running
    await asyncio.sleep(3600)

asyncio.run(main())
```

### Example: RabbitMQ Integration

```python
# Producer (External System)
await queue.publish("suite.control.start", {
    "services": ["backend"]
})

# Consumer (Orchestrator)
bridge = OrchestratorQueueBridge(orchestrator, queue)
await bridge.setup()  # Automatically subscribes to control commands
```

### Event Types

**Control Events** (Commands):
- `suite.control.start` - Start services
- `suite.control.stop` - Stop services
- `suite.control.restart` - Restart service

**Status Events** (Notifications):
- `suite.service_started` - Service started
- `suite.service_stopped` - Service stopped
- `suite.service_error` - Service error
- `suite.health_check` - Health check result

---

## Method 3: Plugin System

### Quick Start

1. **Create Plugin**
```python
# plugins/my_plugin.py
from plugin_system import PluginBase, PluginInfo

class MyPlugin(PluginBase):
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="my_plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Your Name",
            hooks=["service_start", "service_stop"]
        )
    
    def on_service_start(self, service_name: str, pid: int):
        # Your custom logic
        print(f"Service {service_name} started!")
```

2. **Load Plugin**
```python
from plugin_system import PluginManager
from suite_orchestrator import SuiteOrchestrator

# Setup
orchestrator = SuiteOrchestrator()
plugin_manager = PluginManager()
plugin_manager.load_plugins()

# Integrate hooks
orchestrator.plugin_manager = plugin_manager
```

### Use Cases

✅ **Custom Monitoring**
- Add custom metrics
- Integrate with monitoring tools
- Custom alerting logic

✅ **Third-Party Integrations**
- Slack notifications
- Email alerts
- Log aggregation

✅ **Configuration Management**
- Dynamic config updates
- Environment-specific settings
- Secret management

✅ **Business Logic**
- Custom workflows
- Approval processes
- Audit logging

### Available Hooks

1. **`on_service_start`** - Called when service starts
   ```python
   def on_service_start(self, service_name: str, pid: int):
       # Send notification, update metrics, etc.
   ```

2. **`on_service_stop`** - Called when service stops
   ```python
   def on_service_stop(self, service_name: str, pid: int):
       # Cleanup, logging, etc.
   ```

3. **`on_service_error`** - Called on service errors
   ```python
   def on_service_error(self, service_name: str, error: Exception):
       # Alerting, error tracking, etc.
   ```

4. **`on_health_check`** - Called during health checks
   ```python
   def on_health_check(self, health_data: Dict[str, Any]):
       # Custom health validation
   ```

5. **`on_metrics_collect`** - Add custom metrics
   ```python
   def on_metrics_collect(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
       return {
           "custom_metric": 123.45,
           "another_metric": "value"
       }
   ```

6. **`on_config_load`** - Modify configuration
   ```python
   def on_config_load(self, config: Dict[str, Any]) -> Dict[str, Any]:
       config["custom_setting"] = "value"
       return config
   ```

7. **`on_shutdown`** - Called on shutdown
   ```python
   def on_shutdown(self):
       # Cleanup resources
   ```

### Example: Slack Notification Plugin

```python
# plugins/slack_notifier.py
import requests
from plugin_system import PluginBase, PluginInfo

class SlackNotifierPlugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="slack_notifier",
            version="1.0.0",
            description="Sends Slack notifications for service events",
            author="Your Name",
            hooks=["service_start", "service_stop", "service_error"]
        )
    
    def on_service_start(self, service_name: str, pid: int):
        self._send_slack(f"✅ Service '{service_name}' started (PID: {pid})")
    
    def on_service_stop(self, service_name: str, pid: int):
        self._send_slack(f"⏹️ Service '{service_name}' stopped")
    
    def on_service_error(self, service_name: str, error: Exception):
        self._send_slack(f"❌ Service '{service_name}' error: {error}")
    
    def _send_slack(self, message: str):
        if self.webhook_url:
            requests.post(self.webhook_url, json={"text": message})
```

### Example: Custom Metrics Plugin

```python
# plugins/custom_metrics.py
from plugin_system import PluginBase, PluginInfo

class CustomMetricsPlugin(PluginBase):
    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="custom_metrics",
            version="1.0.0",
            description="Adds custom business metrics",
            hooks=["metrics_collect"]
        )
    
    def on_metrics_collect(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        # Add custom metrics
        return {
            "requests_per_second": self._calculate_rps(),
            "error_rate": self._calculate_error_rate(),
            "custom_business_metric": 42
        }
```

---

## 🎯 Choosing the Right Method

### Use REST API When:
- ✅ You need simple HTTP-based integration
- ✅ Building web dashboards or UIs
- ✅ Integrating with CI/CD pipelines
- ✅ Need standard REST patterns
- ✅ Want auto-generated API docs

### Use Message Queue When:
- ✅ Building microservices architecture
- ✅ Need event-driven patterns
- ✅ Multiple systems need to coordinate
- ✅ Want decoupled communication
- ✅ Need high-throughput event processing

### Use Plugin System When:
- ✅ Need custom business logic
- ✅ Want to extend functionality
- ✅ Third-party tool integration
- ✅ Custom monitoring/alerting
- ✅ Need to modify behavior

---

## 🔄 Combining Methods

You can use multiple methods together:

```python
# REST API + Message Queue + Plugins
from suite_orchestrator import SuiteOrchestrator
from management_api import app
from message_queue_integration import *
from plugin_system import PluginManager

# Setup orchestrator
orchestrator = SuiteOrchestrator()

# Add plugins
plugin_manager = PluginManager()
plugin_manager.load_plugins()
orchestrator.plugin_manager = plugin_manager

# Add message queue
queue = MessageQueueIntegration(QueueConfig(QueueType.REDIS))
bridge = OrchestratorQueueBridge(orchestrator, queue)
await bridge.setup()

# Start REST API
# (runs in separate process/thread)
```

---

## 📚 Additional Resources

- **REST API Docs**: `http://localhost:8080/docs` (when running)
- **Integration Guide**: `integration_guide.md`
- **Plugin Examples**: `plugins/example_plugin.py`
- **Queue Examples**: See code comments in `message_queue_integration.py`

---

## 🚀 Quick Reference

| Method | File | Port/Protocol | Best For |
|--------|------|---------------|----------|
| REST API | `management_api.py` | HTTP :8080 | Web apps, CI/CD |
| Message Queue | `message_queue_integration.py` | Redis/RabbitMQ | Microservices |
| Plugin System | `plugin_system.py` | Python hooks | Extensibility |
