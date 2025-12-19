# PersonaAgent

**PersonaAgent** is a Python library for building **persona-based LLM agents** - agents that:

- Are instantiated with different **personalities, styles, and skills**
- Maintain **memory** of past interactions
- Can be wired to any **LLM backend** (OpenAI, Anthropics, etc.)
- Are easy to compose into **multi-agent systems**

> Concept: a *PersonaAgent* is "a configurable, persona-based LLM agent that can be instantiated with different skills and styles and that adapts based on its past interactions."

## Features

- **Persona profiles** - define personality, style, goals, domain, etc.
- **Memory** - simple interaction history + extensible hooks for long-term memory.
- **Skills** - plug in Python functions the agent can call.
- **Model-agnostic** - you pass in how to call your LLM.
- **Composable** - use multiple PersonaAgents in the same app.

## Installation

```bash
pip install persona-agent
```

## Quickstart

```python
from typing import List
from persona_agent.core import PersonaAgent, ChatMessage

# 1. Define how to call your model
def echo_model(messages: List[ChatMessage], **_) -> str:
  # Replace with real LLM call.
  if not messages or not messages[-1].content.strip():
    return "(nothing to echo)\n"
  return f"{messages[-1].content}"

# 2. Instantiate a PersonaAgent
agent = PersonaAgent(
  name="EchoBot",
  model=echo_model,
)

# 3. Interact
response = agent.react("how r u doing?")
print(response)
```

### Using LiteLLM (recommended for real models)

PersonaAgent works great with [LiteLLM](https://docs.litellm.ai) – a unified client
for 100+ LLMs (OpenAI, Anthropic, Azure, Ollama, etc.). :contentReference[oaicite:3]{index=3}

```python
from persona_agent.core import PersonaAgent
from persona_agent.lite_llm import make_litellm_chat_model
from persona_agent.profiles import DOCTOR_PROFILE

# configure LiteLLM via env vars, e.g.
# export OPENAI_API_KEY="sk-..."

model = make_litellm_chat_model(
    model_name="openai/gpt-4o-mini",
    temperature=0.2,
    max_tokens=512,
)

agent = PersonaAgent(
    name="Dr. Maple",
    model=model,
    persona=DOCTOR_PROFILE,
)

print(agent.react("Explain generalized myasthenia gravis in patient-friendly language."))
```

## Persona definition

A persona is just a Python `dict`:

```python
doctor_persona = {
  "role": "neurologist",
  "personality": "calm, analytical, empathetic",
  "style": "concise, medically accurate, patient-friendly",
  "goals": [
    "educate patients safely",
    "avoid providing diagnosis",
    "encourage consultation with physicians",
  ],
  "domain": "neurology, autoimmune diseases",
}
```

You can load predefined ones from persona_agent.profiles.

## Skills

You can attach Python functions as skills:

```python
def search_literature(query: str) -> str:
  # Stub: connect to your own system
  return f"Search result for: {query}"

agent.add_skill("search_literature", search_literature)

# Then call inside your app:
result = agent.call_skill("search_literature", "efgartigimod gMG phase 3")
print(result)
```

Agent logic itself is up to you: PersonaAgent provides the structure and hooks.

## Memory

By default, PersonaAgent keeps a simple in-memory history of interactions:

```python
agent.react("Hello!")
agent.react("Tell me a joke about neurons.")
print(agent.memory.recent(5))
```

You can also plug in your own memory backend (e.g., vector DB, file, Redis) by subclassing `Memory`.

## Project structure

```text
src/persona_agent/
    core.py      # PersonaAgent main class
    memory.py    # Memory abstractions
    skills.py    # Skill registry and helpers
    profiles.py  # Predefined persona profiles
    models.py    # Model adapter types / helpers
```

## Roadmap

- [x] Built-in LLM adapters (via [`litellm`](https://github.com/BerriAI/litellm))
- [ ] Vector-based long-term memory
- [ ] Configuration of persona specs
- [ ] Multi-agent interactions (follow [MCP](https://modelcontextprotocol.io/docs/getting-started/intro)?)

## Contributing

1. Fork this repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Run tests: pytest
4. Open a Pull Request 🎉

## License

This project is licensed under the MIT license.
