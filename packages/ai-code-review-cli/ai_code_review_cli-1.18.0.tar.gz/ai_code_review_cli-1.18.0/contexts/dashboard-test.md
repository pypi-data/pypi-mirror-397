# Project Context for AI Code Review

## Project Overview

**Purpose:** This project provides a real-time dashboard for monitoring an automated software development toolchain.
**Type:** Web application (dashboard)
**Domain:** Software development tooling and CI/CD monitoring.
**Key Dependencies:** `smashing` (dashboard framework), `apscheduler` (scheduled jobs), `yapsy` (plugin system).

## Technology Stack

### Core Technologies
- **Primary Language:** Python
- **Framework/Runtime:** smashing
- **Architecture Pattern:** Plugin-based, Event-driven (Jobs push data to a dashboard)

### Key Dependencies (for Context7 & API Understanding)
- **smashing** - The core dashboard framework. Code reviews will involve understanding its job/widget architecture, where jobs periodically send data to update dashboard widgets.
- **apscheduler==3.10.1** - Advanced Python Scheduler. This library runs the data-fetching jobs on a schedule. Reviews should focus on job configuration, error handling within scheduled tasks, and scheduling logic (e.g., cron, interval).
- **yapsy==1.12.2** - A plugin management system. The project is architected around plugins (12 `.yapsy-plugin` files detected). Reviews should check plugin interfaces, activation/deactivation logic, and how new data sources are added as plugins.
- **requests==2.32.4** - Used for making HTTP requests to external APIs to fetch data for the dashboard. Reviews should scrutinize API error handling, timeouts, and session management.
- **python-gitlab==3.14.0** - A client for the GitLab API. This indicates the project integrates directly with GitLab. Reviews should verify correct usage of the GitLab API, especially around authentication and data extraction.
- **bs4==0.0.1** - BeautifulSoup, a web scraping library. Some data is likely sourced by parsing HTML. Reviews should check the robustness of HTML selectors and error handling for parsing failures.

### Development Tools & CI/CD
- **Testing:** No testing framework was detected.
- **Code Quality:** No specific linters, formatters, or type checkers were detected.
- **Build/Package:** The application is containerized. Dependencies are managed via pip.
- **CI/CD:** GitLab CI/CD is used, configured via `.gitlab-ci.yml`.

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
**Code Organization:** Component-based architecture. The system is split into two main, decoupled components: a Python `feeder` service for data collection and a Ruby-based `dashboard` for data visualization.
**Key Components:**
- **`dashboard` (Smashing/Ruby):** A web application responsible for rendering data widgets. It receives data via an API secured by an authentication token.
- **`feeder` (Python):** A data-gathering service that runs various jobs (defined in `feeder/jobs/`) to collect information and pushes it to the `dashboard` widgets.
- **`container_entrypoint.sh`:** An orchestrator script that initializes and launches both the `dashboard` and `feeder` components within a container.
**Entry Points:** The application starts via `container_entrypoint.sh`. This script first configures and starts the `smashing` web server in the background, then executes the `feeder.py` script as the main foreground process.

### Important Files for Review Context
- **`container_entrypoint.sh`** - Defines the application's startup sequence and runtime configuration. Changes here impact how the `dashboard` and `feeder` services are initialized and interact.
- **`feeder/feeder.py`** - Contains the core logic for the data collection service. Understanding this file is crucial for reviewing changes to data sources, processing, or how data is sent to the dashboard.
- **`.gitlab-ci.yml`** - Defines the CI/CD pipeline. Reviewers should be aware of this file to understand how code is built, tested, and deployed.
- **`Containerfile`** - Specifies the application's container environment, system dependencies, and build process. Changes can affect the runtime environment for all components.

### Development Conventions
- **Naming:** Directories and scripts use lowercase with hyphens or underscores for separation (e.g., `hot_list_status`, `rhivos-nightly`). Environment variables are uppercase with underscores (e.g., `AUTH_TOKEN`).
- **Module Structure:** The project is organized by component (`dashboard`, `feeder`). The `feeder` component further organizes its data-sourcing logic into subdirectories under `jobs/`, each corresponding to a specific task or system.
- **Configuration:** Runtime configuration is supplied through environment variables (e.g., `AUTH_TOKEN`, `DEFAULT_DASHBOARD`). The entrypoint script injects these values into application configuration files (like `dashboard/config.ru`) at container startup using `sed`.
- **Testing:** No testing frameworks or files are visible in the provided project structure.

## Code Review Focus Areas

- **[Data Fetching & Error Handling]** - Review how jobs scheduled with `apscheduler` handle network errors, API rate limits (especially for `python-gitlab`), and unexpected data formats from external sources (`requests`, `bs4`). Ensure there's proper logging and graceful failure to prevent the entire `feeder.py` script from crashing.

- **[Plugin Architecture]** - Verify that new data source plugins, managed by `yapsy`, correctly implement the expected interface. Check for proper registration, configuration handling, and isolation to ensure a faulty plugin doesn't disrupt the main feeder process.

- **[Feeder-Dashboard Interaction]** - Ensure data payloads sent from Python jobs in `feeder.py` to the Smashing dashboard match the data structure expected by the corresponding widget's HTML/CoffeeScript. Check for consistency in widget IDs and correct use of the `smashing` API for pushing events.

- **[Configuration & Secrets Management]** - Following the pattern in `container_entrypoint.sh`, scrutinize how configuration and secrets (e.g., `AUTH_TOKEN`, GitLab tokens) are loaded from the environment into the Python application. Ensure there are no hardcoded secrets and that missing environment variables are handled with clear startup errors.

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