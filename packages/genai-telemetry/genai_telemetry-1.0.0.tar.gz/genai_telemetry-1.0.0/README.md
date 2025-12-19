# GenAI Telemetry

Observability SDK for GenAI/LLM applications.

## Supported Platforms

- Splunk
- Elasticsearch
- OpenTelemetry (Jaeger, Tempo, etc.)
- Datadog
- Prometheus
- Grafana Loki
- AWS CloudWatch
- Console
- File

## Installation
```bash
pip install genai-telemetry
```

## Quick Start
```python
from genai_telemetry import setup_telemetry, trace_llm

# Splunk
setup_telemetry(
    workflow_name="my-app",
    exporter="splunk",
    splunk_url="https://splunk:8088",
    splunk_token="your-token"
)

# Elasticsearch
setup_telemetry(
    workflow_name="my-app",
    exporter="elasticsearch",
    es_hosts=["http://localhost:9200"]
)

@trace_llm(model_name="gpt-4o", model_provider="openai")
def chat(message):
    # Your LLM code here
    pass
```

## License

MIT
```

---
