# Project Context for AI Code Review

## Project Overview

**Purpose:** A multi-agent chatbot that analyzes CI/CD data (Testing Farm, GitLab) using LangGraph and Google Gemini.
**Type:** Web service (API)
**Domain:** CI/CD and DevOps analysis
**Key Dependencies:** langgraph, fastapi, langchain, pydantic

## Technology Stack

### Core Technologies
- **Primary Language:** Python
- **Framework/Runtime:** FastAPI
- **Architecture Pattern:** Asynchronous API

### Key Dependencies (for Context7 & API Understanding)
- **fastapi>=0.115.0** - The core web framework. Reviews should focus on correct use of path operations, dependency injection, Pydantic models, and `async` endpoints.
- **pydantic>=2.0.0** - Used for data validation, serialization, and settings management. Reviews should check for well-defined data models and validation logic.
- **langchain>=1.0.0** - The primary framework for building LLM applications. Reviews should focus on the construction and logic of chains, agents, and tool usage.
- **langgraph>=1.0.0** - Used for building stateful, agentic LLM applications as graphs. Reviews should scrutinize the graph structure, state management, and node implementations.
- **langchain-google-genai>=2.0.0** - Specific integration for Google's Gemini models. Reviews should check for proper client initialization, model parameter configuration, and API usage.
- **websockets>=13.0** - Enables real-time, bidirectional communication. Reviews should focus on WebSocket connection handling, message passing, and streaming logic, likely for LLM responses.

### Development Tools & CI/CD
- **Testing:** None detected
- **Code Quality:** None detected
- **Build/Package:** pip with `pyproject.toml`
- **CI/CD:** None detected

## Architecture & Code Organization

### Project Organization
```
.
├── docs/
│   ├── ADDING_AGENTS.md
│   └── PROJECT_GUIDE.md
├── src/
│   ├── chatbot/
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── chatbot_agent.py
│   │   │   ├── specialist_agent_node.py
│   │   │   ├── summarizer_agent.py
│   │   │   └── supervisor_agent.py
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   ├── agent_cli_utils.py
│   │   │   └── cli.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── graph.py
│   │   │   ├── llm.py
│   │   │   ├── models.py
│   │   │   └── state.py
│   │   ├── web/
│   │   │   ├── static/
│   │   │   │   └── app.js
│   │   │   ├── __init__.py
│   │   │   └── server.py
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── prompts.py
│   │   └── utils.py
│   ├── gitlab_agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── cli.py
│   │   ├── models.py
│   │   ├── prompts.py
│   │   ├── subgraph.py
│   │   └── tools.py
│   ├── releases_agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── cli.py
│   │   ├── models.py
│   │   ├── prompts.py
│   │   └── tools.py
│   ├── tf_agent/
│   │   ├── __init__.py
│   │   ├── agent.py
│   │   ├── cli.py
│   │   ├── models.py
│   │   ├── prompts.py
│   │   └── tools.py
│   └── __init__.py
├── .gitignore
├── README.md
└── pyproject.toml
```

### Architecture Patterns
**Code Organization:** Modular, Agent-based Architecture. A central `chatbot` application orchestrates workflows between specialized, self-contained agent modules (e.g., `gitlab_agent`, `tf_agent`). The core logic is implemented as a **State Machine** using the LangGraph library.
**Key Components:**
- **State Graph (`src/chatbot/core/graph.py`):** The central orchestrator. It defines the nodes (agents) and edges (transitions) that control the application's flow based on the current `ChatbotState`.
- **Agents (`src/chatbot/agents/`):** Individual processing units that perform specific roles. Key agents identified are `chatbot` (user interaction), `supervisor` (task routing), `specialist` (tool execution), and `summarizer` (response generation).
- **Specialist Agent Modules (`src/gitlab_agent/`, etc.):** Pluggable modules that provide specific functionalities (tools, prompts, models) and are invoked by the main graph's `specialist_agent_node`.
- **State Management (`src/chatbot/core/state.py`):** A central `ChatbotState` object is used to pass data and context between nodes in the graph.
- **Configuration (`src/chatbot/core/config.py`):** A singleton `AgentConfig` object, based on Pydantic, manages all application settings from environment variables or a `.env` file.
**Entry Points:**
- **Command-Line Interface (CLI):** Each specialist agent has a dedicated CLI entry point (e.g., `src/tf_agent/cli.py`) that utilizes a shared utility (`agent_cli_utils.py`) for a consistent user experience.
- **Web Server (`src/chatbot/web/server.py`):** A web interface that uses a slightly different graph (`create_web_chatbot_graph`) to handle non-interactive sessions.

### Important Files for Review Context
- **`src/chatbot/core/graph.py`** - This file defines the entire application workflow. Understanding the nodes (agents) and the conditional edges is critical to comprehending how tasks are routed and processed.
- **`src/chatbot/core/config.py`** - Defines all external dependencies, API keys, and operational parameters. Reviewers must be aware of these settings to understand how the application interacts with external services and how its behavior can be configured.
- **`src/chatbot/core/models.py`** - Contains the Pydantic models that define the data structures passed between agents and used for tool outputs. This is key to understanding the data contracts within the system.

### Development Conventions
- **Naming:** Follows standard Python PEP 8 conventions: `snake_case` for modules, functions, and variables; `PascalCase` for classes (e.g., `AgentConfig`, `ChatbotState`).
- **Module Structure:** The project uses a clear, feature-based structure. Each specialist agent is a self-contained package with its own `agent.py`, `tools.py`, `prompts.py`, and `cli.py`. This promotes high cohesion and low coupling.
- **Configuration:** Configuration is strictly handled through `pydantic_settings.BaseSettings`, loading from environment variables or a `.env` file. All configuration is centralized in `src/chatbot/core/config.py`.
- **Testing:** No testing files or patterns are visible in the provided project structure.

## Code Review Focus Areas

- **LangGraph State Management** - Scrutinize how nodes in `src/chatbot/core/graph.py` interact with the `ChatbotState`. Verify that each agent node correctly reads its required inputs from the state and writes its outputs back without overwriting or corrupting data needed by subsequent nodes in the graph execution flow.

- **Multi-Agent Routing Logic** - Review the `supervisor_agent_node`. Pay close attention to the mechanism it uses to route tasks to the `specialist_agent_node`. When new tools or capabilities are added, ensure the supervisor's routing or classification logic is updated to correctly delegate the new tasks.

- **FastAPI & WebSocket Integration** - For changes involving the web interface, focus on how the `create_web_chatbot_graph` is invoked and managed within FastAPI endpoints. Specifically, check WebSocket connection handling, asynchronous streaming of agent responses, and implementation of timeouts (`websocket_timeout`) to prevent orphaned connections.

- **Structured Data Contracts (Pydantic)** - Enforce the use of Pydantic models (like `BaseAgentResponse` from `src/chatbot/core/models.py`) for all agent inputs and outputs. Ensure that any data returned from LLM calls or external API tools is parsed and validated against a corresponding model to maintain type safety and a consistent data structure throughout the agent graph.

- **External Service Tooling** - Closely examine any code that implements tools for interacting with the Testing Farm and GitLab APIs (as indicated by `tf_api_key` and `gitlab_token` in `config.py`). Verify secure handling of API keys, robust error handling for external API calls, and correct parsing of the responses from these services.

## Library Documentation & Best Practices



## CI/CD Configuration Guide



---
<!-- MANUAL SECTIONS - DO NOT MODIFY THIS LINE -->
<!-- The sections below will be preserved during updates -->

## Business Logic & Implementation Decisions

<!-- Add project-specific business logic, unusual patterns, or architectural decisions -->
<!-- Example: Why certain algorithms were chosen, performance trade-offs, etc. -->

## Domain-Specific Context

<!-- Add domain terminology, internal services, external dependencies context -->
<!-- Example: Internal APIs, third-party services, business rules, etc. -->

## Special Cases & Edge Handling

<!-- Document unusual scenarios, edge cases, or exception handling patterns -->
<!-- Example: Legacy compatibility, migration considerations, etc. -->

## Additional Context

<!-- Add any other context that reviewers should know -->
<!-- Example: Security considerations, compliance requirements, etc. -->