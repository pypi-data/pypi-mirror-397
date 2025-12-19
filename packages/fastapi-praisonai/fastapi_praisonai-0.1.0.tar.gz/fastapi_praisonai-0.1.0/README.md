# fastapi-praisonai

[FastAPI](https://fastapi.tiangolo.com/) integration for [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install fastapi-praisonai
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_praisonai import create_router

app = FastAPI()
app.include_router(create_router())

# Now you have:
# POST /praisonai/query - Send queries to PraisonAI
# GET /praisonai/agents - List available agents
```

## API Endpoints

### POST /praisonai/query

Send a query to PraisonAI agents:

```json
{
  "query": "Research AI trends",
  "agent": "researcher"  // optional
}
```

### GET /praisonai/agents

List available PraisonAI agents.

## Using the Client Directly

```python
from fastapi_praisonai import PraisonAIClient

client = PraisonAIClient(api_url="http://localhost:8080")

# In an async context
result = await client.run_workflow("Research AI trends")
result = await client.run_agent("Write an article", "writer")
agents = await client.list_agents()
```

## Configuration

```python
from fastapi_praisonai import create_router

router = create_router(
    api_url="http://localhost:8080",
    prefix="/ai",  # Custom prefix
    tags=["AI Agents"],  # OpenAPI tags
)
```

## Prerequisites

Start PraisonAI server:

```bash
pip install praisonai
praisonai serve agents.yaml --port 8080
```

## Links

- [PraisonAI Documentation](https://docs.praison.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

## License

MIT
