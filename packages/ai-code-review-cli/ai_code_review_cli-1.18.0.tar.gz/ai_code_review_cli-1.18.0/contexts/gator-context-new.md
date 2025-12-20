# Project Context for AI Code Review

## Project Overview
**Purpose:** A configurable tool to perform quality and release gating checks for the Red Hat In-Vehicle Operating System (RHIVOS).
**Type:** CLI tool
**Domain:** Software Release Management / CI/CD Gating (for Red Hat internal systems)
**Key Dependencies:** `click` (for CLI structure), `koji` (for build system interaction), `errata-tool` (for release advisory interaction), `pyyaml` (for configuration)

## Technology Stack
### Core Technologies
- **Primary Language:** Python
- **Framework/Runtime:** Standard Python runtime; no web framework detected.
- **Architecture Pattern:** `src`-based layout for code organization.

### Key Dependencies (for Context & API Understanding)
- **koji>=1.34.0** - Interacts with the Koji RPM build system. Code changes may affect package build and management logic.
- **errata-tool>=1.32.0** - Connects to the Red Hat Errata Tool. This suggests the project automates release processes or advisory creation.
- **jira>=3.6.0** - Interacts with Jira for issue tracking. Code likely involves creating, updating, or querying Jira tickets.
- **requests>=2.31.0** - Core library for making HTTP requests to external APIs. Reviewers should check for proper error handling, timeouts, and session management.
- **cattrs>=24.1.2** & **attrs>=24.3.0** - Used for data modeling and serialization/deserialization. Code will use `attrs` for class definitions and `cattrs` for converting between Python objects and formats like JSON/YAML.
- **pandas>=2.2.3** - Used for data manipulation and analysis. Indicates the application processes tabular data, likely from API responses.

### Development Tools & CI/CD
- **Testing:** `pytest` is used for writing and running tests.
- **Code Quality:** Enforces standards using `ruff` for linting/formatting and `mypy` for static type checking.
- **Build/Package:** Project configuration and dependencies are managed via `pyproject.toml`.
- **CI/CD:** Uses GitLab CI (`.gitlab-ci.yml`) with a multi-stage pipeline including static analysis, container builds, and various testing stages defined in the `.gitlab/` directory.

## Architecture & Code Organization
### Project Organization
```
.
├── .gitlab/
│   ├── brew-diff-test.yml
│   ├── code-review.yml
│   ├── container-build.yml
│   ├── evaluate.yml
│   ├── generate-advisories.yml
│   ├── package-test.yml
│   ├── promote.yml
│   ├── rules.yml
│   ├── static-analysis.yml
│   └── system.yml
├── config/
│   ├── RHIVOS-1/
│   ├── RHIVOS-1.0-Core-gating.yaml
│   ├── RHIVOS-1.0-Core-promote.yaml
│   ├── RHIVOS-1.0-DevPreview-Update-gating.yaml
│   ├── RHIVOS-1.0-DevPreview-Update-promote.yaml
│   ├── RHIVOS-1.0-TechPreview-Update-promote.yaml
│   ├── RHIVOS-1.0-TechPreview-gating.yaml
│   ├── RHIVOS-1.0-TechPreview-promote.yaml
│   ├── RHIVOS-1.0-gating.yaml
│   ├── RHIVOS-1.0-promote.yaml
│   ├── RHIVOS-1.0.0-gating.yaml
│   └── RHIVOS-1.0.0-promote.yaml
├── src/
│   └── gator/
├── tests/
│   ├── commands/
│   ├── config/
│   ├── gator_cli/
│   ├── utils/
│   └── __init__.py
├── pyproject.toml
├── README.md
└── .gitignore
```

### Architecture Patterns
**Code Organization:** The project follows a **Command Pattern** combined with a **Layered Architecture**. The CLI layer (`gator_cli`) is distinctly separated from the business logic layer (`gator/commands`). Each CLI command delegates its execution to a corresponding function in the `commands` module.
**Key Components:**
- **`gator_cli/cli.py`**: The main application entry point. It uses the `click` library to define the CLI structure, parse arguments, and route execution to the appropriate command logic. It is responsible for initial setup like logging and configuration loading.
- **`gator/commands/*`**: A collection of modules, each implementing the core logic for a specific CLI command (e.g., `evaluate`, `promote`, `audit`). This isolates the business logic from the CLI interface.
- **`gator/utils/configure.py`**: A utility module responsible for loading and parsing configuration from YAML files. The configuration is then passed to all commands via the `click` context.
**Entry Points:** The application is a command-line tool invoked via the `gator` command. The primary execution flow starts in `src/gator/gator_cli/cli.py`, which then dispatches to subcommands like `gator evaluate` or `gator promote`.

### Important Files for Review Context
- **`src/gator/gator_cli/cli.py`**: As the main entry point, this file defines the application's command structure and initialization process. Changes here can affect all commands.
- **`config/*.yaml`**: These files control the application's behavior for different stages (e.g., `gating`, `promote`). Reviewers must understand that application logic is heavily influenced by these external configurations.
- **`.gitlab/*.yml`**: These files define the CI/CD pipelines. The logic in the application's commands (e.g., `promote`, `package-test`) is directly related to the stages defined in these pipeline files.

### Development Conventions
- **Naming:** Imported business logic functions are aliased with a leading underscore to distinguish them from the `click` command functions (e.g., `from gator.commands.evaluate import evaluate as _evaluate`). Configuration files follow a strict `PRODUCT-VERSION-STAGE-ACTION.yaml` pattern.
- **Module Structure:** The source code is organized by feature and responsibility. The CLI interface is in `gator_cli/`, command logic is in `commands/`, and shared utilities are in `utils/`. The `tests/` directory mirrors this structure.
- **Configuration:** Configuration is loaded once at startup from YAML files in the `config/` directory via `gator.utils.configure.load_config()`. The resulting configuration object is passed down to all subcommands using the `click` context object (`ctx.obj`).
- **Testing:** A dedicated `tests/` directory with a structure that mirrors the `src/` directory is used, indicating that tests are organized by the component they are testing.

## Code Review Focus Areas
- **[Specific Technical Area]** - **CLI Command Implementation:** The project uses `click` for its CLI structure. Review new or modified commands to ensure they follow the established pattern: the `cli.py` file should only contain the `click` decorator and a call to a dedicated implementation function in the `gator.commands` package. Logic should not be implemented directly within the CLI function.

- **[Architecture/Pattern Area]** - **Configuration Propagation:** The main `gator` group loads a configuration object (`gator_conf`) and passes it to subcommands via `ctx.obj`. Verify that all commands correctly use `@click.pass_obj` to receive this central configuration and do not attempt to load configuration themselves, ensuring a single source of truth.

- **[Framework-Specific Area]** - **External Service Interactions:** Given dependencies like `koji`, `errata-tool`, and `jira`, pay close attention to how clients for these services are instantiated and used. Code changes should handle potential API errors, network timeouts, and authentication issues gracefully, likely using patterns established elsewhere in the `gator.commands` module.

- **[Code Quality Area]** - **Structured Data Handling:** The use of `attrs` and `cattrs` indicates a preference for structured data classes over raw dictionaries for configuration and API payloads. When reviewing code that processes data from YAML files or API responses, ensure it uses `attrs` classes for validation, type safety, and clarity.

- **[Domain-Specific Area]** - **RPM Build and Release Logic:** The project's core domain involves RPMs, Koji builds, and Errata advisories. Scrutinize any code using `koji`, `errata-tool`, or `rpm-vercmp`. Verify that logic for tagging builds, comparing package versions, or generating advisories is correct, as errors in these areas can directly impact the software release pipeline.

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