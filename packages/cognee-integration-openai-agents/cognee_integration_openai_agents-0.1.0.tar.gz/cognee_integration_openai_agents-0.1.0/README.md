# Cognee-Integration-OpenAI-Agents

A powerful integration between Cognee and the OpenAI Agents SDK that provides intelligent memory management and retrieval capabilities for AI agents.

## Overview

`cognee-integration-openai-agents` combines [Cognee's advanced memory layer](https://github.com/topoteretes/cognee) with the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python). This integration allows you to build AI agents that can efficiently store, search, and retrieve information from a persistent memory.

## Features

- **Smart Knowledge Storage**: Add and persist information in cognee memory powered by graph + vectors
- **Semantic Search**: Retrieve relevant information using natural language queries
- **Session Management**: Support for session/user/agent-specific data organization
- **OpenAI Agents SDK Integration**: Seamless integration with OpenAI's Agent SDK via tools
- **Async Support**: Built with async/await for high-performance applications
- **Thread-Safe**: Queue-based processing for concurrent operations

## Installation

```bash
pip install cognee-integration-openai-agents
```

## Quick Start

```python
import asyncio
from dotenv import load_dotenv
import cognee
from agents import Agent, Runner
from cognee_integration_openai_agents import add_tool, search_tool

load_dotenv()

async def main():
    # Initialize Cognee (optional - for data management)
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    
    # Create an agent with memory capabilities
    agent = Agent(
        name="research_analyst",
        instructions=(
            "You are an expert research analyst with access to a comprehensive "
            "knowledge base."
        ),
        tools=[add_tool, search_tool],
    )
    
    # Use the agent to store information
    result = await Runner.run(
        agent,
        "Remember that our company signed a contract with HealthBridge Systems "
        "in the healthcare industry, starting Feb 2023, ending Jan 2026, worth £2.4M"
    )
    print(result.final_output)
    
    # Query the stored information
    result = await Runner.run(
        agent,
        "What contracts do we have in the healthcare industry?"
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## Available Tools

### Basic Tools

```python
from cognee_integration_openai_agents import add_tool, search_tool

# add_tool: Store information in the memory
# search_tool: Search and retrieve previously stored information
```

### Sessionized Tools

For multi-user applications, use sessionized tools to isolate data between users:

```python
from cognee_integration_openai_agents import get_sessionized_cognee_tools

# Get tools for a specific user session
add_tool, search_tool = get_sessionized_cognee_tools("user-123")

# Auto-generate a session ID
add_tool, search_tool = get_sessionized_cognee_tools()
```

## Session Management

`cognee-integration-openai-agents` supports user-specific sessions to tag data and isolate retrieval between different users or contexts:

```python
import asyncio
from agents import Agent, Runner
from cognee_integration_openai_agents import get_sessionized_cognee_tools

async def main():
    # Each user gets their own isolated session
    user1_add, user1_search = get_sessionized_cognee_tools("user-123")
    user2_add, user2_search = get_sessionized_cognee_tools("user-456")
    
    # Create separate agents for each user
    agent1 = Agent(
        name="assistant_1",
        instructions="You are a helpful assistant.",
        tools=[user1_add, user1_search]
    )
    
    agent2 = Agent(
        name="assistant_2",
        instructions="You are a helpful assistant.",
        tools=[user2_add, user2_search]
    )
    
    # Each agent works with isolated data
    await Runner.run(agent1, "Remember: I like pizza")
    await Runner.run(agent2, "Remember: I like sushi")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Reference

### `add_tool(data: str)`

Store information in the memory for later retrieval. Data is stored globally.

**Parameters:**
- `data` (str): The text or information you want to store

**Returns:** Confirmation message

**Example:**
```python
agent = Agent(
    name="data_manager",
    instructions="You manage our knowledge base.",
    tools=[add_tool]
)

result = await Runner.run(
    agent,
    "Store this: Our Q4 revenue was $2.5M with 15% growth"
)
```

### `search_tool(query_text: str)`

Search and retrieve previously stored information from the memory. Searches all globally stored data.

**Parameters:**
- `query_text` (str): Natural language search query

**Returns:** List of relevant search results

**Example:**
```python
agent = Agent(
    name="research_assistant",
    instructions="You help users find information quickly.",
    tools=[search_tool]
)

result = await Runner.run(agent, "What was our Q4 revenue?")
print(result.final_output)
```

### `get_sessionized_cognee_tools(session_id: Optional[str] = None)`

Returns cognee tools that orgnaizes data by session. When using sessionized tools:
- Data added is tagged with the session's NodeSet
- Searches only return data from that session's NodeSet
- Different sessions are isolated

**Parameters:**
- `session_id` (Optional[str]): User/session identifier for data organization. If not provided, a random session ID is auto-generated for sessionized tools.

**Returns:** `(add_tool, search_tool)` - A tuple of sessionized tools

**Example:**
```python
# With explicit session ID
add_tool, search_tool = get_sessionized_cognee_tools("user-123")

# Auto-generate session ID
add_tool, search_tool = get_sessionized_cognee_tools()
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Required: OpenAI API key for the OpenAI Agents SDK
OPENAI_API_KEY=your-openai-api-key-here

# LLM API key for Cognee (defaults to OPENAI_API_KEY if not set)
# Cognee supports multiple LLM providers - set this if using a different provider
LLM_API_KEY=your-llm-api-key-here
```

### Cognee Configuration (Optional)

You can customize Cognee's data and system directories:

```python
from cognee.api.v1.config import config
import os

config.data_root_directory(
    os.path.join(os.path.dirname(__file__), ".cognee/data_storage")
)

config.system_root_directory(
    os.path.join(os.path.dirname(__file__), ".cognee/system")
)
```

## Examples

Check out the `examples/` directory for comprehensive usage examples:

- **`examples/tools_example.py`**: Basic usage with add and search tools
- **`examples/sessionized_tools_example.py`**: Multi-user session management with visualization

### Pre-loading Data

You can pre-load data into Cognee before creating agents:

```python
import asyncio
import cognee
from cognee_integration_openai_agents import search_tool
from agents import Agent, Runner

async def main():
    # Pre-load data
    await cognee.add("Important company information here...")
    await cognee.add("More data to remember...")
    await cognee.cognify()  # Process and index the data
    
    # Now create an agent that can search this data
    agent = Agent(
        name="analyst",
        instructions="You have access to our company knowledge base.",
        tools=[search_tool]
    )
    
    result = await Runner.run(agent, "What information do we have?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### Data Management

```python
import asyncio
import cognee

async def reset_memory():
    """Clear all data and reset the memory."""
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

async def visualize_knowledge_graph():
    """Generate a visualization of the knowledge graph."""
    await cognee.visualize_graph("graph.html")
```

### Working with Multiple Agents

```python
import asyncio
from agents import Agent, Runner
from cognee_integration_openai_agents import add_tool, search_tool

async def main():
    # Create a data entry agent
    data_agent = Agent(
        name="data_collector",
        instructions="You collect and store important information.",
        tools=[add_tool]
    )
    
    # Create a research agent
    research_agent = Agent(
        name="researcher",
        instructions="You search and analyze information from the knowledge base.",
        tools=[search_tool]
    )
    
    # Store data
    await Runner.run(
        data_agent,
        "Store this: Project Alpha launched in Q1 2024 with $5M budget"
    )
    
    # Search data
    result = await Runner.run(
        research_agent,
        "When did Project Alpha launch and what was the budget?"
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### Using with Handoffs

```python
import asyncio
from agents import Agent, Runner
from cognee_integration_openai_agents import add_tool, search_tool

async def main():
    # Specialist agent for storing data
    storage_agent = Agent(
        name="storage_specialist",
        instructions="You specialize in storing information accurately.",
        tools=[add_tool]
    )
    
    # Specialist agent for searching data
    search_agent = Agent(
        name="search_specialist",
        instructions="You specialize in finding relevant information.",
        tools=[search_tool]
    )
    
    # Triage agent that routes to specialists
    triage_agent = Agent(
        name="triage_agent",
        instructions=(
            "Route requests to the appropriate specialist. "
            "Use storage_specialist for storing data, "
            "use search_specialist for finding information."
        ),
        handoffs=[storage_agent, search_agent]
    )
    
    result = await Runner.run(
        triage_agent,
        "I need to find all our healthcare contracts"
    )
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

## Requirements

- Python 3.10+
- `OPENAI_API_KEY` - For the OpenAI Agents SDK
- `LLM_API_KEY` - For Cognee if using a different LLM provider
- Dependencies automatically managed via pyproject.toml
