# Project Context for AI Code Review

## Project Overview

**Purpose:** This project provides a web-based dashboard for monitoring an automated software development toolchain.
**Type:** Web Application (Dashboard)
**Domain:** DevOps / CI/CD Monitoring
**Key Dependencies:** smashing (dashboard framework), apscheduler (scheduled jobs), yapsy (plugin system), requests (HTTP client)

## Technology Stack

### Core Technologies
- **Primary Language:** Python
- **Framework/Runtime:** smashing (dashboard framework)
- **Architecture Pattern:** Event-Driven, Plugin-based

### Key Dependencies (for Context7 & API Understanding)
- **smashing** - The core dashboard framework. Code changes will likely involve creating jobs that push data to dashboard widgets via Server-Sent Events (SSE).
- **apscheduler==3.10.1** - Used for scheduling periodic data-fetching jobs. Reviews should focus on job configuration (triggers, intervals), error handling, and preventing job overlaps.
- **yapsy==1.12.2** - A plugin system. The project uses a plugin architecture for its data feeders, as evidenced by `.yapsy-plugin` files. Reviews should check plugin implementation, configuration, and interaction with the core system.
- **requests==2.32.4** - Standard HTTP client for fetching data from external APIs. Focus on proper error handling, timeouts, session management, and secure handling of credentials.
- **bs4==0.0.1** - BeautifulSoup, used for web scraping. Reviews should scrutinize the robustness of HTML selectors and error handling for parsing failures.
- **python-gitlab==3.14.0** - A client for the GitLab API. This indicates direct integration with GitLab. Check for efficient API usage, pagination, and correct handling of GitLab objects.

### Development Tools & CI/CD
- **Testing:** No testing framework detected.
- **Code Quality:** No code quality tools detected.
- **Build/Package:** Standard Python packaging (requirements.txt).
- **CI/CD:** Uses GitLab CI/CD for automation, configured via `.gitlab-ci.yml`.

## Architecture & Code Organization

### Project Organization
```
.
├── certs/
├── dashboard/
│   ├── assets/
│   │   └── images/
│   ├── dashboards/
│   ├── widgets/
│   │   ├── headlines_list/
│   │   ├── hot_list_status/
│   │   ├── hot_status/
│   │   └── resource_table/
│   └── Gemfile
├── feeder/
│   ├── jobs/
│   │   ├── atc-resources/
│   │   ├── autosd-9-nightly/
│   │   ├── autosd-nightly/
│   │   ├── autosd-webserver/
│   │   ├── common/
│   │   ├── device-pool-rcar-s4/
│   │   ├── device-pool-ridesx4/
│   │   ├── news/
│   │   ├── rhivos-1-0-nightly-core/
│   │   ├── rhivos-1-0-nightly/
│   │   ├── rhivos-nightly-core/
│   │   └── rhivos-nightly/
│   ├── feeder.py
│   └── requirements.txt
├── scripts/
│   └── gai.conf
├── .gitignore
├── .gitlab-ci.yml
├── Containerfile
└── README.md
```

### Architecture Patterns
**Code Organization:** The project follows a Service-Oriented pattern with two distinct, decoupled components: a Python-based data `feeder` service and a Ruby-based `dashboard` for presentation. These services run as separate processes within the same container.
**Key Components:**
- **`dashboard` (Smashing):** A Ruby application responsible for rendering data visualizations through a system of widgets and dashboards. It receives data pushed from the feeder.
- **`feeder` (Python):** A data aggregation service. It contains multiple `jobs` that fetch data from various external sources and send it to the `dashboard` for display.
- **`container_entrypoint.sh`:** An orchestration script that initializes and runs both the dashboard and feeder services.
**Entry Points:** The application's sole entry point is the `container_entrypoint.sh` script. It first launches the `smashing` web server as a background process and then starts the `feeder.py` script as the main foreground process.

### Important Files for Review Context
- **`container_entrypoint.sh`**: Defines the application's startup logic, process management, and the critical runtime configuration injection mechanism. Changes here impact the entire application's environment.
- **`feeder/feeder.py`**: The central script for the data aggregation service. It likely orchestrates the execution of the various data collection jobs located in the `feeder/jobs/` subdirectories.
- **`.gitlab-ci.yml`**: Defines the continuous integration and deployment pipeline. Understanding this file is crucial for reviewing changes related to the build, testing, and deployment process.
- **`Containerfile`**: Specifies the container build process, including base image, system dependencies, and application setup. It provides context for the runtime environment.

### Development Conventions
- **Naming:** Job-specific logic is organized into hyphenated directory names within `feeder/jobs/` (e.g., `rhivos-1-0-nightly`, `device-pool-rcar-s4`). Dashboard widgets use snake_case directory names (e.g., `headlines_list`).
- **Module Structure:** The project is strictly modularized by function. The `feeder/` directory contains all data-sourcing logic, while `dashboard/` contains all presentation logic. Data sources are further isolated into their own subdirectories under `feeder/jobs/`.
- **Configuration:** Runtime configuration is handled through environment variables (e.g., `AUTH_TOKEN`, `DEFAULT_DASHBOARD`). These variables are injected into application configuration files (like `dashboard/config.ru`) at container startup via shell commands (`sed`) in the entrypoint script.
- **Testing:** No testing frameworks or test files are visible in the provided project structure.

## Code Review Focus Areas

- **[Specific Technical Area]** - Data Fetching and Payload Formatting: The project uses `requests`, `bs4`, and `python-gitlab` to fetch data. Review the data-fetching logic within jobs for proper error handling (e.g., connection errors, timeouts, unexpected API responses) and efficient parsing. Critically, verify that the final JSON payload sent to the Smashing dashboard matches the data structure expected by the target widget.

- **[Architecture/Pattern Area]** - Plugin-Based Job Architecture: The use of `yapsy` indicates that data-fetching logic is implemented as plugins. When reviewing a new plugin, ensure it correctly adheres to the expected interface for discovery by `yapsy`. Verify that plugins are self-contained, manage their own state, and handle their specific configurations without creating side effects for the main `feeder.py` process or other plugins.

- **[Framework-Specific Area]** - `apscheduler` Job Management: The `feeder.py` script uses `apscheduler` to run jobs. Scrutinize the job trigger configurations (e.g., `interval`, `cron`). Check if long-running jobs have appropriate timeouts or overlap prevention (e.g., `max_instances=1`) to avoid resource exhaustion. Ensure exceptions within a scheduled job are caught and logged without crashing the entire feeder process.

- **[Code Quality Area]** - Configuration and Secret Handling: The `container_entrypoint.sh` script injects the `AUTH_TOKEN` from an environment variable. Enforce this pattern throughout the codebase. Verify that no secrets, API keys, or tokens are hardcoded in Python files. All configuration should be passed via environment variables or external configuration files.

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