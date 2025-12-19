# langchain-praisonai

LangChain integration for [PraisonAI](https://github.com/MervinPraison/PraisonAI) multi-agent framework.

## Installation

```bash
pip install langchain-praisonai
```

## Prerequisites

1. Install and start PraisonAI server:
```bash
pip install praisonai
praisonai serve agents.yaml --port 8080
```

## Usage

### Basic Usage

```python
from langchain_praisonai import PraisonAITool
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType

# Create the PraisonAI tool
praisonai_tool = PraisonAITool(api_url="http://localhost:8080")

# Use with LangChain agent
llm = ChatOpenAI(model="gpt-4o-mini")
agent = initialize_agent(
    tools=[praisonai_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.run("Research the latest trends in AI and summarize them")
print(result)
```

### Using Specific Agents

```python
from langchain_praisonai import PraisonAIAgentTool

# Create tools for specific agents
researcher = PraisonAIAgentTool(agent_name="researcher")
writer = PraisonAIAgentTool(agent_name="writer")

# Use multiple agent tools
tools = [researcher, writer]
```

### List Available Agents

```python
from langchain_praisonai import PraisonAIListAgentsTool

list_tool = PraisonAIListAgentsTool()
agents = list_tool.run({})
print(agents)
```

### Direct Tool Usage

```python
from langchain_praisonai import PraisonAITool

tool = PraisonAITool()

# Run with default workflow
result = tool.run({"query": "What are the benefits of AI?"})

# Run with specific agent
result = tool.run({"query": "Research quantum computing", "agent": "researcher"})
```

### Async Usage

```python
import asyncio
from langchain_praisonai import PraisonAITool

async def main():
    tool = PraisonAITool()
    result = await tool.arun({"query": "Analyze market trends"})
    print(result)

asyncio.run(main())
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_url` | `http://localhost:8080` | PraisonAI server URL |
| `timeout` | `300` | Request timeout in seconds |

## Available Tools

| Tool | Description |
|------|-------------|
| `PraisonAITool` | General-purpose tool for running PraisonAI workflows |
| `PraisonAIAgentTool` | Tool for running a specific named agent |
| `PraisonAIListAgentsTool` | Tool for listing available agents |

## Links

- [PraisonAI Documentation](https://docs.praison.ai)
- [PraisonAI GitHub](https://github.com/MervinPraison/PraisonAI)
- [LangChain Documentation](https://python.langchain.com)

## License

MIT
