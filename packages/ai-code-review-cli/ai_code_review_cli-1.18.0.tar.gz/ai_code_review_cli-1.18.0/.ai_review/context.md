# Project Context for AI Code Review

## Project Overview

**Purpose:** Provides AI-powered code review for local Git changes, remote pull/merge requests, and CI pipelines.
**Type:** CLI tool
**Domain:** Developer Tools / Code Quality
**Key Dependencies:** click (CLI framework), langchain (LLM interaction), python-gitlab/pygithub (Git provider APIs), aiohttp (async HTTP)

## Technology Stack

### Core Technologies
- **Primary Language:** Python (3.12)
- **Framework/Runtime:** Asyncio (using aiohttp for HTTP and click for CLI)
- **Architecture Pattern:** Asynchronous, src-based layout for a command-line application

### Key Dependencies (for Context7 & API Understanding)
- **langchain>=0.2.0** - Core LLM orchestration framework. Reviewers must understand LangChain concepts (Chains, Agents, RAG) as most logic will be built on it.
- **aiohttp>=3.9.0** - Asynchronous HTTP client/server. Code must use `async/await` syntax for all I/O operations. Review for proper coroutine management and client session handling.
- **pydantic>=2.5.0** - Data validation and settings management. Reviewers should check for correct data model definitions, type annotations, and validation logic.
- **click>=8.1.0** - Command-Line Interface creation. Code changes related to the CLI will involve defining commands, options, and arguments using Click decorators.
- **python-gitlab>=4.0.0 / pygithub>=2.1.0** - API clients for GitLab and GitHub. Review for correct and secure usage of these APIs, especially around authentication and error handling.
- **structlog>=23.2.0** - Structured logging library. Reviewers should ensure logging is structured and contextual, not using simple `print()` or standard `logging` calls.

### Development Tools & CI/CD
- **Testing:** `pytest>=7.4.0` with `pytest-asyncio` for testing asynchronous code and `pytest-cov` for coverage reporting.
- **Code Quality:** `ruff>=0.1.0` for linting/formatting and `mypy>=1.7.0` for static type checking. Enforced via `pre-commit`.
- **Build/Package:** Modern Python packaging using `pyproject.toml`.
- **CI/CD:** GitLab CI, configured via `.gitlab-ci.yml`.

## Architecture & Code Organization

### Project Organization
```
.
├── contexts/
│   ├── aib-context-new.md
│   ├── create-osbuild-context.md
│   ├── gator-context-new.md
│   ├── infra-context-new.md
│   ├── test-console-context-new.md
│   ├── tf-context-new.md
│   └── webserver.md
├── docs/
│   ├── context-generator.md
│   ├── developer-guide.md
│   └── user-guide.md
├── src/
│   ├── ai_code_review/
│   │   ├── core/
│   │   ├── models/
│   │   ├── providers/
│   │   ├── utils/
│   │   ├── __init__.py
│   │   └── cli.py
│   └── context_generator/
│       ├── core/
│       ├── sections/
│       ├── templates/
│       ├── __init__.py
│       ├── cli.py
│       ├── constants.py
│       └── models.py
├── tests/
│   ├── fixtures/
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_context_generator_simple.py
│   ├── unit/
│   │   ├── test_anthropic_provider.py
│   │   ├── test_base_provider.py
│   │   ├── test_cli.py
│   │   ├── test_cli_ci.py
│   │   ├── test_config.py
│   │   ├── test_config_file_loading.py
│   │   ├── test_context_generator_cli.py
│   │   ├── test_context_generator_code_extractor.py
│   │   ├── test_context_generator_constants.py
│   │   ├── test_context_generator_context_builder.py
│   │   ├── test_context_generator_facts_extractor.py
│   │   └── test_context_generator_llm_analyzer.py
│   ├── __init__.py
│   └── conftest.py
├── .gitignore
├── .gitlab-ci.yml
├── .pre-commit-config.yaml
├── Containerfile
├── README.md
└── pyproject.toml
```

### Architecture Patterns
**Code Organization:** Layered Architecture. The application is structured with clear separation of concerns: a Command Line Interface (`cli.py`), data models (`models/`), core business logic (`core/`), and external service integrations (`providers/`).
**Key Components:**
- **`ReviewEngine` (`core/review_engine.py`):** The central orchestrator that coordinates interactions between platform clients (like GitLab/GitHub) and AI providers. It contains the main business logic for generating and posting code reviews.
- **`Config` (`models/config.py`):** A Pydantic `BaseSettings` model that defines and validates all application configuration, loaded from environment variables. It acts as the single source of truth for settings.
- **Platform Clients (`core/*_client.py`):** Implementations of the `PlatformClientInterface` for different code hosting platforms (e.g., GitLab, GitHub). A factory method in `ReviewEngine` selects the correct client based on configuration.
- **AI Providers (`providers/*.py`):** Implementations of the `BaseAIProvider` for different AI models/services (e.g., Ollama). A factory method in `ReviewEngine` selects the provider.
**Entry Points:** The application is a command-line tool invoked via `src/ai_code_review/cli.py`. It uses the `click` library to parse arguments, initialize the `Config` object, and run the `ReviewEngine`.

### Important Files for Review Context
- **`src/ai_code_review/core/review_engine.py`** - Contains the core orchestration logic. Understanding this file is essential to grasp how code diffs are processed, prompts are generated, and reviews are submitted.
- **`src/ai_code_review/models/config.py`** - Defines the entire application configuration using Pydantic. Changes here can affect any part of the system, and reviewers must understand how settings are defined and validated.
- **`src/ai_code_review/cli.py`** - The main entry point. It handles all user-facing command-line options and is responsible for initializing and triggering the `ReviewEngine`.

### Development Conventions
- **Naming:** Classes use `PascalCase` (e.g., `ReviewEngine`), while functions, methods, and variables use `snake_case` (e.g., `_create_platform_client`). Internal helper methods are prefixed with a single underscore. Constants are `UPPER_SNAKE_CASE`.
- **Module Structure:** The `src` directory contains two distinct applications (`ai_code_review`, `context_generator`). Within each, code is organized by function: `core` for business logic, `models` for data structures, `providers` for external services, and `utils` for helpers.
- **Configuration:** Configuration is handled centrally by the `Config` class in `src/ai_code_review/models/config.py`, which uses `pydantic_settings.BaseSettings` for type-safe loading from environment variables, with built-in validation.
- **Testing:** The `tests/` directory is separated into `unit/` and `integration/` subdirectories. Test files are prefixed with `test_`, indicating a standard Pytest-based testing strategy.

## Code Review Focus Areas

- **[LangChain Integration and Prompt Management]** - Scrutinize changes related to prompt construction, especially in `ai_code_review.utils.prompts.create_review_chain`. Verify how diff content is formatted and passed to the LangChain models, as this directly impacts the quality of the AI-generated review. Ensure error handling for AI provider APIs (e.g., rate limits, content filtering) is robust within the provider modules (`ai_code_review.providers.*`).

- **[Provider Abstraction and Extensibility]** - Verify that changes adhere to the established factory and interface patterns. When a new platform or AI provider is added, ensure it correctly implements the `PlatformClientInterface` or `BaseAIProvider` respectively, and that the core `ReviewEngine` interacts only with the abstraction, not the concrete implementation. Check for any logic that breaks this decoupling.

- **[Asynchronous Operations and API Client Handling]** - Review all `async` functions for correct `await` usage, especially during I/O operations like API calls with `aiohttp`/`httpx` or file access with `aiofiles`. Ensure that concurrent operations (e.g., fetching multiple files) are handled efficiently with tools like `asyncio.gather` rather than sequential awaits in a loop.

- **[Pydantic Model and Configuration Validation]** - Pay close attention to changes in `src/ai_code_review/models/config.py`. Check for complex inter-field dependencies in new or modified `model_validator` functions. Ensure that new configuration options have sensible defaults and that validation logic provides clear, user-facing error messages for invalid combinations of settings.

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
