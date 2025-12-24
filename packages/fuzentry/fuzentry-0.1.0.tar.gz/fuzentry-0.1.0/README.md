# Fuzentry Python SDK

Official Python SDK for Fuzentry AI AgentOS PaaS Platform.

## Installation

```bash
pip install fuzentry
```

## Quick Start

```python
from fuzentry import FuzentryClient
from fuzentry.agents import AgentsClient
from fuzentry.memory import MemoryClient

# Initialize client
client = FuzentryClient(api_key="fuz_your_api_key_here")

# Use agents
agents = AgentsClient(client)
result = agents.invoke(
    message="Analyze this contract for risks",
    folders=[{"id": "folder-123", "name": "Legal Docs"}]
)

print(f"Response: {result['response']}")
print(f"Tokens used: {result['tokensUsed']}")

# Store and search memories
memory = MemoryClient(client)
memory.store(
    content="Q4 revenue was $2.5M",
    folder_id="folder-123",
    metadata={"quarter": "Q4", "year": "2024"}
)

results = memory.search("revenue", folder_id="folder-123", top_k=5)
```

## Modules

- **`fuzentry.auth`** - API key validation, session tokens
- **`fuzentry.agents`** - AI orchestration, chaining
- **`fuzentry.prompts`** - Prompt template management
- **`fuzentry.memory`** - Vector search, semantic memory
- **`fuzentry.plugins`** - MCP tools, OAuth integrations
- **`fuzentry.exporter`** - Data export, compliance

## Authentication

Get your API key from [AWS Marketplace](https://aws.amazon.com/marketplace) after subscribing.

## Usage Tracking

All API calls are automatically metered through AWS Marketplace at **$0.00030 per orchestration**.

## Documentation

Full documentation: https://docs.fuzentry.com

## License

Proprietary - Licensed to AWS Marketplace customers only.
