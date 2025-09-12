# DeepSeek Chat with Monitoring

Local ChatGPT-like interface using DeepSeek-Coder-1.3B-Instruct model with GPU acceleration and real-time monitoring.

## Requirements

- Docker with NVIDIA GPU support
- 8GB+ GPU memory
- Docker Compose

## Services

- **DeepSeek Chat**: http://localhost:5000 - AI chat interface
- **Grafana**: http://localhost:3000 - Monitoring dashboard (no login required)
- **Prometheus**: http://localhost:9090 - Metrics collection

## Usage

```bash
docker compose up --build
```
