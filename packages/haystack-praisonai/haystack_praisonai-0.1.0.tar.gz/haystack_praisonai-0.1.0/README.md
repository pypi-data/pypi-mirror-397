# haystack-praisonai

[Haystack](https://haystack.deepset.ai/) integration for [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install haystack-praisonai
```

## Quick Start

```python
from haystack import Pipeline
from haystack_praisonai import PraisonAIComponent

# Create pipeline with PraisonAI component
pipeline = Pipeline()
pipeline.add_component("praisonai", PraisonAIComponent())

# Run the pipeline
result = pipeline.run({"praisonai": {"query": "Research the latest AI trends"}})
print(result["praisonai"]["response"])
```

## Using a Specific Agent

```python
from haystack_praisonai import PraisonAIComponent

# Use a specific agent
researcher = PraisonAIComponent(agent="researcher")
result = researcher.run(query="Research quantum computing")
print(result["response"])
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_url` | `http://localhost:8080` | PraisonAI server URL |
| `agent` | `None` | Specific agent to run |
| `timeout` | `300` | Request timeout in seconds |

## Prerequisites

Start PraisonAI server:

```bash
pip install praisonai
praisonai serve agents.yaml --port 8080
```

## Links

- [PraisonAI Documentation](https://docs.praison.ai)
- [Haystack Documentation](https://docs.haystack.deepset.ai)

## License

MIT
