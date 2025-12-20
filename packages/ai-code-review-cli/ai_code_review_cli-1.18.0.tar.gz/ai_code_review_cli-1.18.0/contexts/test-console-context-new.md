# Project Context for AI Code Review

## Project Overview
**Purpose:** This project is a Python console application, likely for testing or as a demonstration.
**Type:** CLI tool
**Domain:** Software Development / Testing
**Key Dependencies:** Relies solely on the Python standard library.

## Technology Stack
*Tech stack not available*

## Architecture & Code Organization
### Project Organization
```
.
├── integration/
│   └── test_container.py
├── scripts/
│   ├── cronjobs/
│   │   ├── requirements.txt
│   │   └── tmt_plans.sh
│   ├── tc_certificate/
│   │   ├── README.md
│   │   └── generate_csr.sh
│   ├── migrate_to_pg.py
│   ├── start.sh
│   └── update_db.sh
├── selenium/
│   ├── README.md
│   ├── test_console_cli.py
│   └── test_testrun_automation.py
├── src/
│   ├── autometar_flow/
│   │   ├── jobs/
│   │   └── modules/
│   ├── package_test_flow/
│   │   ├── jobs/
│   │   └── modules/
│   ├── test_console/
│   │   ├── apidocs/
│   │   └── db/
│   ├── __init__.py
│   └── global_vars.py
├── tests/
│   ├── api/
│   │   ├── conftest.py
│   │   └── test_rhivos_testing.py
│   ├── package_test_flow/
│   │   ├── modules/
│   │   └── utils/
│   ├── __init__.py
│   └── deployment_validation.py
├── README.md
└── .gitignore
```

### Architecture Patterns
**Code Organization:** Modular, Feature-Driven Architecture. The `src` directory is organized into distinct feature flows (e.g., `autometar_flow`, `package_test_flow`), each containing its own `jobs` and `modules`. This suggests that business logic is encapsulated within these feature-specific packages.
**Key Components:**
- **`test_console`**: Appears to be the main control plane or API layer, given the `apidocs/` and `db/` subdirectories. It likely orchestrates the other components.
- **`autometar_flow` & `package_test_flow`**: These are core business logic modules responsible for executing specific testing workflows. The `jobs/` subdirectory within each suggests they handle background or asynchronous tasks.
- **`scripts/`**: A collection of operational scripts for database management (`migrate_to_pg.py`, `update_db.sh`), scheduled tasks (`cronjobs/`), and application startup (`start.sh`).
**Entry Points:**
- **`scripts/start.sh`**: The primary script for starting the application services.
- **`scripts/cronjobs/tmt_plans.sh`**: A scheduled job entry point for running specific test plans.
- **`test_console` API**: The `apidocs` directory implies an API is exposed, which serves as a primary entry point for user or system interactions.

### Important Files for Review Context
- **`src/global_vars.py`**: Likely contains shared configuration or state. Changes here can have widespread, non-local effects and should be reviewed with extreme care for potential side effects.
- **`scripts/start.sh`**: Defines how the application is launched, including environment setup and service initialization. Understanding this file is crucial for reviewing changes to deployment or runtime configuration.
- **`scripts/migrate_to_pg.py`**: This script directly modifies the database schema. Reviews must focus on correctness, data integrity, and backward compatibility to prevent data loss.

### Development Conventions
- **Naming:** File and directory names consistently use `snake_case` (e.g., `package_test_flow`, `global_vars.py`). Test files are prefixed with `test_`.
- **Module Structure:** Code is organized by feature. Within a feature directory, logic is separated into `jobs` (likely executable processes or tasks) and `modules` (reusable libraries or components).
- **Configuration:** Configuration appears to be handled through a combination of a central Python module (`src/global_vars.py`) for static or global values and shell scripts (`start.sh`) which likely process environment variables for runtime settings.
- **Testing:** The project employs a comprehensive, multi-level testing strategy: unit/API tests in `tests/` (using pytest, indicated by `conftest.py`), container-based tests in `integration/`, and browser automation tests in `selenium/`.

## Code Review Focus Areas
- **[Pythonic Idioms & Standard Library Usage]** - Since the project has no external dependencies, verify that changes leverage the Python standard library effectively (e.g., `collections`, `itertools`, `pathlib`) instead of implementing custom solutions. Enforce Pythonic idioms like list comprehensions, context managers (`with` statements), and proper exception handling.
- **[Architecture/Pattern Area]** - Given the `src-based` layout, ensure all new application code is placed within the `src` directory. Scrutinize import statements to prevent circular dependencies and enforce consistent import ordering. Verify that modules have a clear, single responsibility.
- **[Dependency Management]** - As the project currently uses only the standard library, critically evaluate any pull request that introduces a new third-party dependency. The justification for adding an external library must be strong. If a dependency is approved, ensure it is added to the project's dependency management file (e.g., `pyproject.toml`).
- **[Code Quality Area]** - The project is marked as 'tested'. Therefore, all new code (functions, classes, methods) must be accompanied by corresponding unit tests. Review the quality of new tests to ensure they cover edge cases, not just the happy path. Any change that modifies existing logic must also update the relevant tests.

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