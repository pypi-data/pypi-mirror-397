# gradio-praisonai

[Gradio](https://gradio.app/) components for [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install gradio-praisonai
```

## Quick Start

```python
from gradio_praisonai import launch_chat

# Launch a chat interface
launch_chat()
```

## Components

### create_chat_interface

Create a Gradio Blocks interface:

```python
from gradio_praisonai import create_chat_interface

demo = create_chat_interface(
    api_url="http://localhost:8080",
    agent="researcher",  # Optional: specific agent
    title="🤖 AI Assistant",
)
demo.launch()
```

### PraisonAIClient

Direct API client:

```python
from gradio_praisonai import PraisonAIClient

client = PraisonAIClient(api_url="http://localhost:8080")

# Run full workflow
result = client.run_workflow("Research AI trends")

# Run specific agent
result = client.run_agent("Write an article", "writer")

# List agents
agents = client.list_agents()
```

## Prerequisites

Start PraisonAI server:

```bash
pip install praisonai
praisonai serve agents.yaml --port 8080
```

## Links

- [PraisonAI Documentation](https://docs.praison.ai)
- [Gradio Documentation](https://gradio.app/docs)

## License

MIT
