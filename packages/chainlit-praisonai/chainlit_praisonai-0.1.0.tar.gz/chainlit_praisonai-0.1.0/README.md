# chainlit-praisonai

[Chainlit](https://chainlit.io/) integration for [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install chainlit-praisonai
```

## Quick Start

Create `app.py`:

```python
import chainlit as cl
from chainlit_praisonai import PraisonAIClient

client = PraisonAIClient()

@cl.on_message
async def main(message: cl.Message):
    response = await client.run_workflow(message.content)
    await cl.Message(content=response).send()
```

Run:

```bash
chainlit run app.py
```

## Using a Specific Agent

```python
from chainlit_praisonai import PraisonAIClient

client = PraisonAIClient()

# Use a specific agent
response = await client.run_agent("Research quantum computing", "researcher")
```

## Configuration

```python
from chainlit_praisonai import PraisonAIClient

client = PraisonAIClient(
    api_url="http://localhost:8080",
    timeout=300,
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
- [Chainlit Documentation](https://docs.chainlit.io)

## License

MIT
