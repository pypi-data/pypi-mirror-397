# streamlit-praisonai

[Streamlit](https://streamlit.io/) components for [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install streamlit-praisonai
```

## Quick Start

```python
import streamlit as st
from streamlit_praisonai import praisonai_chat

st.title("My AI App")
praisonai_chat()
```

## Components

### praisonai_chat

A full chat interface for PraisonAI:

```python
from streamlit_praisonai import praisonai_chat

praisonai_chat(
    api_url="http://localhost:8080",
    agent="researcher",  # Optional: specific agent
    title="🤖 AI Assistant",
    placeholder="Ask me anything...",
)
```

### PraisonAIClient

Direct API client:

```python
from streamlit_praisonai import PraisonAIClient

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
- [Streamlit Documentation](https://docs.streamlit.io)

## License

MIT
