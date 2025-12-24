# nostromo-core

Core domain logic for the MU-TH-UR 6000 chatbot. This package contains:

- **ChatEngine** - Main chat processing logic
- **Ports** - Abstract interfaces for LLM providers and memory stores
- **Adapters** - Implementations for Anthropic Claude and OpenAI GPT
- **Theme** - Colors, error messages, and system prompts

## Installation

```bash
# Core only
pip install nostromo-core

# With Anthropic support
pip install "nostromo-core[anthropic]"

# With OpenAI support
pip install "nostromo-core[openai]"

# All providers
pip install "nostromo-core[all]"
```

## Usage

```python
from nostromo_core import ChatEngine
from nostromo_core.adapters.anthropic import AnthropicProvider
from nostromo_core.adapters.memory import InMemoryStore

# Create engine with adapters
engine = ChatEngine(
    llm=AnthropicProvider(api_key="sk-..."),
    memory=InMemoryStore(),
)

# Chat
response = await engine.chat("session-1", "Hello, MOTHER.")

# Stream response
async for token in engine.chat_stream("session-1", "What is my mission?"):
    print(token, end="", flush=True)
```
