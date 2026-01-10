# Integration Guide - Management System Integration

This guide explains how to integrate the suite orchestrator into larger management systems, monitoring platforms, and automation tools.

> **See also**: `INTEGRATION_METHODS.md` for a complete overview of all three integration methods (REST API, Message Queue, Plugin System).

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│         External Management System                       │
│  (Kubernetes, Ansible, Terraform, CI/CD, etc.)         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ REST API / Webhooks / CLI
                     │
┌────────────────────▼────────────────────────────────────┐
│         Management API Server (Port 8080)                │
│  - REST Endpoints                                        │
│  - Webhook System                                        │
│  - Metrics Export                                        │
│  - Health Checks                                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Python API
                     │
┌────────────────────▼────────────────────────────────────┐
│         Suite Orchestrator                               │
│  - Service Management                                    │
│  - Process Control                                       │
│  - State Management                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ Subprocess Control
                     │
┌────────────────────▼────────────────────────────────────┐
│         Services (Backend, Frontend, Influencer)         │
└─────────────────────────────────────────────────────────┘
```

## 🔌 Integration Methods

### 1. REST API Integration

The Management API provides REST endpoints for all operations.

#### Base URL
```
http://localhost:8080
```

#### Key Endpoints

**Health Check**
```bash
GET /api/health
# Returns: Overall health status, service statuses, uptime
```

**List Services**
```bash
GET /api/services
# Returns: All services with their current status
```

**Start Services**
```bash
POST /api/services/start
Content-Type: application/json

{
  "services": ["backend", "frontend"],  # Optional: specific services
  "backend_only": false,
  "frontend_only": false,
  "skip_checks": false,
  "skip_setup": false
}
```

**Stop Services**
```bash
POST /api/services/stop
Content-Type: application/json

{
  "services": ["backend"]  # Optional: specific services, or omit for all
}
```

**Get Metrics**
```bash
GET /api/metrics
# Returns: CPU, memory, disk usage, active services count
```

**Get Logs**
```bash
GET /api/logs/{service}?lines=100
# Returns: Recent log lines for a service
```

**Restart Service**
```bash
POST /api/services/{service}/restart
```

### 2. Webhook Integration

Register webhooks to receive notifications for events.

**Register Webhook**
```bash
POST /api/webhooks
Content-Type: application/json

{
  "url": "https://your-system.com/webhooks/suite",
  "events": ["start", "stop", "error", "health_check"],
  "secret": "your-webhook-secret"  # Optional
}
```

**Webhook Payload Format**
```json
{
  "event": "start",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "services": ["backend", "frontend"],
    "status": "starting"
  }
}
```

**Supported Events**
- `start` - Service(s) started
- `stop` - Service(s) stopped
- `error` - Service error occurred
- `health_check` - Health check failed

### 3. CLI Integration

Use the orchestrator directly from command line or scripts.

```bash
# Start all services
python suite_orchestrator.py start

# Start specific services
python suite_orchestrator.py start --backend-only

# Check status
python suite_orchestrator.py status

# Stop all
python suite_orchestrator.py stop
```

### 4. Python Library Integration

Import and use the orchestrator as a Python library.

```python
from suite_orchestrator import SuiteOrchestrator

# Initialize
orchestrator = SuiteOrchestrator()

# Setup environment
orchestrator.setup_environment()

# Start services
orchestrator.start_all(['backend', 'frontend'])

# Check status
orchestrator.status_report()

# Stop services
orchestrator.stop_all()
```

## 🔗 Integration Examples

### Kubernetes Integration

**Deployment with Management API**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: suite-management
spec:
  replicas: 1
  selector:
    matchLabels:
      app: suite-management
  template:
    metadata:
      labels:
        app: suite-management
    spec:
      containers:
      - name: management-api
        image: your-registry/suite-management:latest
        ports:
        - containerPort: 8080
        env:
        - name: BASE_DIR
          value: "/app"
        volumeMounts:
        - name: suite-data
          mountPath: /app
      volumes:
      - name: suite-data
        persistentVolumeClaim:
          claimName: suite-data-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: suite-management
spec:
  selector:
    app: suite-management
  ports:
  - port: 8080
    targetPort: 8080
  type: LoadBalancer
```

**Health Check Probe**
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /api/health
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 5
```

### Ansible Integration

**Playbook Example**

```yaml
---
- name: Manage Suite Services
  hosts: suite_servers
  tasks:
    - name: Start all services
      uri:
        url: "http://localhost:8080/api/services/start"
        method: POST
        body_format: json
        body:
          services: ["backend", "frontend"]
        status_code: 200
    
    - name: Wait for services to be healthy
      uri:
        url: "http://localhost:8080/api/health"
        method: GET
      register: health
      until: health.json.status == "healthy"
      retries: 10
      delay: 5
    
    - name: Get service metrics
      uri:
        url: "http://localhost:8080/api/metrics"
        method: GET
      register: metrics
    
    - name: Display metrics
      debug:
        msg: "CPU: {{ metrics.json.cpu_usage }}%, Memory: {{ metrics.json.memory_usage }}%"
```

### Terraform Integration

**External Data Source**

```hcl
data "external" "suite_status" {
  program = ["python", "${path.module}/scripts/get_suite_status.py"]
}

resource "null_resource" "start_suite" {
  provisioner "local-exec" {
    command = "curl -X POST http://localhost:8080/api/services/start -H 'Content-Type: application/json' -d '{}'"
  }
}
```

### CI/CD Integration (GitHub Actions)

```yaml
name: Deploy Suite

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services
        run: |
          curl -X POST http://localhost:8080/api/services/start \
            -H 'Content-Type: application/json' \
            -d '{"services": ["backend", "frontend"]}'
      
      - name: Wait for health check
        run: |
          for i in {1..30}; do
            STATUS=$(curl -s http://localhost:8080/api/health | jq -r '.status')
            if [ "$STATUS" == "healthy" ]; then
              echo "Services are healthy"
              exit 0
            fi
            sleep 2
          done
          echo "Services failed to become healthy"
          exit 1
      
      - name: Run tests
        run: |
          # Your test commands here
```

### Prometheus Integration

**Metrics Endpoint**

The `/api/metrics` endpoint provides Prometheus-compatible metrics:

```python
# Add to management_api.py
@app.get("/metrics")
async def prometheus_metrics():
    """Prometheus metrics endpoint"""
    metrics = await get_metrics()
    return f"""# HELP suite_cpu_usage CPU usage percentage
# TYPE suite_cpu_usage gauge
suite_cpu_usage {metrics.cpu_usage or 0}

# HELP suite_memory_usage Memory usage percentage
# TYPE suite_memory_usage gauge
suite_memory_usage {metrics.memory_usage or 0}

# HELP suite_active_services Number of active services
# TYPE suite_active_services gauge
suite_active_services {metrics.active_services}
"""
```

**Prometheus Config**
```yaml
scrape_configs:
  - job_name: 'suite-management'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
```

### Grafana Dashboard

**JSON Dashboard Configuration**

```json
{
  "dashboard": {
    "title": "Suite Management",
    "panels": [
      {
        "title": "Service Status",
        "targets": [{
          "expr": "suite_active_services"
        }]
      },
      {
        "title": "CPU Usage",
        "targets": [{
          "expr": "suite_cpu_usage"
        }]
      }
    ]
  }
}
```

### Docker Compose Integration

```yaml
version: '3.8'

services:
  suite-management:
    build: .
    ports:
      - "8080:8080"
    volumes:
      - ./:/app
    environment:
      - BASE_DIR=/app
    depends_on:
      - mongodb
  
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
```

### Slack/Teams Integration

**Webhook Handler**

```python
# webhook_handler.py
import requests

def handle_webhook(payload):
    event = payload['event']
    data = payload['data']
    
    if event == 'error':
        message = f"⚠️ Suite Error: {data.get('message', 'Unknown error')}"
    elif event == 'start':
        message = f"✅ Services started: {', '.join(data.get('services', []))}"
    elif event == 'stop':
        message = f"⏹️ Services stopped: {', '.join(data.get('services', []))}"
    
    # Send to Slack
    requests.post(
        'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
        json={'text': message}
    )
```

## 📊 Monitoring Integration

### Health Check Endpoints

**For Load Balancers**
```bash
# Health check endpoint
GET /api/health

# Response:
{
  "status": "healthy",
  "services": {...},
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime": 3600.5
}
```

### Metrics Export

**For Monitoring Systems**
```bash
# System metrics
GET /api/metrics

# Response:
{
  "cpu_usage": 45.2,
  "memory_usage": 62.1,
  "disk_usage": 38.5,
  "active_services": 3,
  "total_services": 3,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔐 Security Considerations

1. **API Authentication**: Add authentication middleware
2. **Webhook Secrets**: Use secrets for webhook validation
3. **HTTPS**: Use HTTPS in production
4. **Rate Limiting**: Implement rate limiting
5. **CORS**: Configure CORS properly

## 📝 Configuration Export

**Export Configuration for External Systems**

```bash
GET /api/integration/export

# Returns complete configuration in JSON format
```

## 🚀 Quick Start Integration

1. **Start Management API**
   ```bash
   python management_api.py
   ```

2. **Access Dashboard**
   ```
   Open management_dashboard.html in browser
   ```

3. **Test API**
   ```bash
   curl http://localhost:8080/api/health
   ```

4. **Register Webhook**
   ```bash
   curl -X POST http://localhost:8080/api/webhooks \
     -H 'Content-Type: application/json' \
     -d '{
       "url": "https://your-system.com/webhook",
       "events": ["start", "stop", "error"]
     }'
   ```

## 📚 Additional Resources

- **API Documentation**: Auto-generated at `http://localhost:8080/docs`
- **Management Dashboard**: Open `management_dashboard.html`
- **Orchestrator CLI**: See `suite_orchestrator.py --help`
