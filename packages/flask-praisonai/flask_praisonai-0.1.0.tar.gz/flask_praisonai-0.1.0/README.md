# flask-praisonai

[Flask](https://flask.palletsprojects.com/) integration for [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install flask-praisonai
```

## Quick Start

```python
from flask import Flask
from flask_praisonai import create_blueprint

app = Flask(__name__)
app.register_blueprint(create_blueprint())

# Now you have:
# POST /praisonai/query - Send queries to PraisonAI
# GET /praisonai/agents - List available agents

if __name__ == "__main__":
    app.run()
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
from flask_praisonai import PraisonAIClient

client = PraisonAIClient(api_url="http://localhost:8080")

result = client.run_workflow("Research AI trends")
result = client.run_agent("Write an article", "writer")
agents = client.list_agents()
```

## Configuration

```python
from flask_praisonai import create_blueprint

bp = create_blueprint(
    api_url="http://localhost:8080",
    url_prefix="/ai",  # Custom prefix
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
- [Flask Documentation](https://flask.palletsprojects.com)

## License

MIT
