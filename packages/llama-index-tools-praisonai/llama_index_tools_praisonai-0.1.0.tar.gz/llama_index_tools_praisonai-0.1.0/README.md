# llama-index-tools-praisonai

LlamaIndex tool integration for [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install llama-index-tools-praisonai
```

## Prerequisites

1. Install and start PraisonAI server:
```bash
pip install praisonai
praisonai serve agents.yaml --port 8080
```

## Usage

### Basic Usage with LlamaIndex Agent

```python
from llama_index_tools_praisonai import PraisonAIToolSpec
from llama_index.agent.openai import OpenAIAgent

# Create the PraisonAI tool spec
spec = PraisonAIToolSpec(api_url="http://localhost:8080")
tools = spec.to_tool_list()

# Create agent with PraisonAI tools
agent = OpenAIAgent.from_tools(tools, verbose=True)

# Use the agent
response = agent.chat("Research the latest trends in AI and summarize them")
print(response)
```

### Using Individual Tools

```python
from llama_index_tools_praisonai import PraisonAIToolSpec

spec = PraisonAIToolSpec()

# Run a specific agent
result = spec.run_agent(query="Research quantum computing", agent="researcher")
print(result)

# Run the full workflow
result = spec.run_workflow(query="Create a blog post about AI")
print(result)

# List available agents
agents = spec.list_agents()
print(agents)
```

### Async Usage

```python
import asyncio
from llama_index_tools_praisonai import PraisonAIToolSpec

async def main():
    spec = PraisonAIToolSpec()
    
    # Async agent execution
    result = await spec.arun_agent(query="Research AI", agent="researcher")
    print(result)
    
    # Async workflow execution
    result = await spec.arun_workflow(query="Create content")
    print(result)

asyncio.run(main())
```

### With ReAct Agent

```python
from llama_index_tools_praisonai import PraisonAIToolSpec
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI

spec = PraisonAIToolSpec()
tools = spec.to_tool_list()

llm = OpenAI(model="gpt-4o-mini")
agent = ReActAgent.from_tools(tools, llm=llm, verbose=True)

response = agent.chat("Use PraisonAI to research and write about machine learning")
print(response)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_url` | `http://localhost:8080` | PraisonAI server URL |
| `timeout` | `300` | Request timeout in seconds |

## Available Tools

| Tool | Description |
|------|-------------|
| `run_agent` | Run a specific PraisonAI agent (e.g., researcher, writer) |
| `run_workflow` | Run the full multi-agent workflow |
| `list_agents` | List all available agents |

## Links

- [PraisonAI Documentation](https://docs.praison.ai)
- [PraisonAI GitHub](https://github.com/MervinPraison/PraisonAI)
- [LlamaIndex Documentation](https://docs.llamaindex.ai)

## License

MIT
