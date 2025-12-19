# Protectron SDK

[![PyPI version](https://badge.fury.io/py/protectron.svg)](https://badge.fury.io/py/protectron)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**EU AI Act compliance for AI agents** - Automatic audit logging, human-in-the-loop approvals, and evidence generation.

## Features

- 🔍 **Automatic Audit Logging** - Log all agent actions, decisions, and tool calls
- 👥 **Human-in-the-Loop** - Request approvals for high-risk actions
- 🛑 **Emergency Stop** - Respect emergency stop signals
- 🔒 **PII Redaction** - Automatic detection and redaction of personal data
- 📊 **Framework Integrations** - Works with LangChain, CrewAI, and more
- 💾 **Offline Resilience** - Buffer events when offline, retry automatically

## Quick Start

### Installation

```bash
pip install protectron
```

### Basic Usage

```python
from protectron import ProtectronAgent

# Initialize
agent = ProtectronAgent(
    api_key="pk_live_your_key_here",
    agent_id="agt_your_agent_id"
)

# Log a decision (critical for Article 12 compliance)
agent.log_decision(
    "approve_refund",
    confidence=0.95,
    reasoning="Amount within policy limits",
    alternatives=["deny", "escalate"]
)

# Log a tool call
agent.log_tool_call(
    "search_database",
    input_data={"query": "customer orders"},
    output_data={"results": [...]},
    duration_ms=150
)

# Log an action
agent.log_action(
    "process_refund",
    status="completed",
    details={"amount": 100, "customer_id": "12345"}
)

# Always close when done
agent.close()
```

### With Context Manager

```python
with ProtectronAgent(api_key="...", agent_id="...") as agent:
    agent.log_action("my_action", status="completed")
# Automatically flushed and closed
```

### With Tracing

```python
with agent.trace("handle_customer_request") as ctx:
    # All events in this block share the same trace_id
    agent.log_tool_call("lookup_customer", ...)
    agent.log_decision("approve_request", ...)
```

## Framework Integrations

### LangChain

```python
from protectron import ProtectronAgent
from protectron.integrations.langchain import ProtectronCallbackHandler
from langchain.agents import create_react_agent

protectron = ProtectronAgent(api_key="...", agent_id="...")
handler = ProtectronCallbackHandler(protectron)

# Add to your agent
agent = create_react_agent(llm, tools, callbacks=[handler])
```

### CrewAI

```python
from protectron import ProtectronAgent
from protectron.integrations.crewai import ProtectronCrewAI
from crewai import Crew

protectron = ProtectronAgent(api_key="...", agent_id="...")
integration = ProtectronCrewAI(protectron)

crew = Crew(agents=[...], tasks=[...])
wrapped_crew = integration.wrap_crew(crew)
result = wrapped_crew.kickoff()
```

## Human-in-the-Loop (HITL)

```python
# Check if action requires approval
if agent.check_hitl("large_refund", {"amount": 500}):
    # Request approval (blocks until response)
    approval = agent.request_approval(
        "large_refund",
        context={"amount": 500, "customer": "VIP"},
        timeout_seconds=3600  # 1 hour
    )
    
    if approval.approved:
        # Proceed with action
        process_refund(500)
    else:
        # Handle rejection
        notify_customer(approval.reason)
```

## Emergency Stop

```python
# Check if agent has been stopped
while not agent.is_stopped():
    # Continue processing
    process_next_item()

# Agent was stopped - exit gracefully
```

## Configuration

All settings can be configured via constructor or environment variables:

| Parameter | Env Variable | Default | Description |
|-----------|--------------|---------|-------------|
| `api_key` | `PROTECTRON_API_KEY` | Required | Your API key |
| `agent_id` | `PROTECTRON_AGENT_ID` | Required | Your agent ID |
| `base_url` | `PROTECTRON_BASE_URL` | `https://api.protectron.ai` | API endpoint |
| `environment` | `PROTECTRON_ENVIRONMENT` | `production` | Environment name |
| `buffer_size` | `PROTECTRON_BUFFER_SIZE` | `1000` | Max events to buffer |
| `flush_interval` | `PROTECTRON_FLUSH_INTERVAL` | `5.0` | Seconds between flushes |
| `pii_redaction` | `PROTECTRON_PII_REDACTION` | `true` | Enable PII redaction |
| `debug` | `PROTECTRON_DEBUG` | `false` | Enable debug logging |

## EU AI Act Compliance

The Protectron SDK helps you comply with:

- **Article 12** - Automatic recording of events over the system's lifetime
- **Article 14** - Human oversight with HITL approvals and emergency stop
- **Article 19** - Log retention (6-36 months configurable)
- **Article 26** - Deployer obligations for operation monitoring

## API Reference

### ProtectronAgent

The main client class for interacting with the Protectron platform.

#### Logging Methods

- `log_action(action, status, details, ...)` - Log an action taken by the agent
- `log_decision(decision, confidence, reasoning, ...)` - Log a decision with reasoning
- `log_tool_call(tool_name, input_data, output_data, ...)` - Log a tool/API call
- `log_llm_call(model, provider, prompt, response, ...)` - Log an LLM API call
- `log_error(error_type, message, stack_trace, ...)` - Log an error
- `log_delegation(to_agent_id, task, context, ...)` - Log delegation to another agent
- `log_human_override(action, original, override, ...)` - Log human override

#### Session & Tracing

- `start_session(session_id=None)` - Start a new session
- `end_session()` - End the current session
- `trace(name, trace_id=None)` - Context manager for tracing

#### HITL

- `check_hitl(action, context)` - Check if action requires approval
- `request_approval(action, context, timeout_seconds, block)` - Request approval

#### Lifecycle

- `flush()` - Flush buffered events to server
- `close()` - Gracefully shutdown the SDK
- `is_stopped()` - Check if agent has been emergency stopped

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/protectron-ai/protectron-sdk.git
cd protectron-sdk

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run ruff check protectron tests
poetry run black --check protectron tests
poetry run mypy protectron
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=protectron --cov-report=html

# Run specific test file
poetry run pytest tests/test_client.py -v
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- Documentation: https://docs.protectron.ai/sdk
- Issues: https://github.com/protectron-ai/protectron-sdk/issues
- Email: support@protectron.ai
