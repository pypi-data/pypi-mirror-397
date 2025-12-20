# Project Context for AI Code Review

## Project Overview

**Purpose:** This project builds system images for automotive software or embedded systems.
**Type:** CLI tool for building system images.
**Domain:** Automotive software, embedded systems, and system image creation.
**Key Dependencies:** No key dependencies specified in the provided project information.

## Technology Stack

### Core Technologies
- **Primary Language:** Python
- **Framework/Runtime:** No specific framework detected; likely a standalone application or library.
- **Architecture Pattern:** Configuration-driven, modular architecture.

### Key Dependencies (for Context7 & API Understanding)
- None detected.

### Development Tools & CI/CD
- **Testing:** Uses `tox` for test automation (`tox.ini`). Test suites are located in the `tests` directory.
- **Code Quality:** No specific tools detected, but configuration may exist in `tox.ini`.
- **Build/Package:** No specific build system detected.
- **CI/CD:** GitLab CI - Configuration is in `.gitlab-ci.yml`. The pipeline is likely complex and multi-stage, leveraging scripts from the `ci-scripts` directory.

## Architecture & Code Organization

### Project Organization
```
.
├── .fmf/
├── aib/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── builder_options_test.py
│   │   ├── exceptions_test.py
│   │   ├── manifest_test.py
│   │   ├── ostree_test.py
│   │   ├── runner_test.py
│   │   ├── simple_test.py
│   │   ├── utils_test.py
│   │   ├── vm_test.py
│   │   └── vmhelper_test.py
│   ├── __init__.py
│   ├── exceptions.py
│   ├── exports.py
│   ├── main.py
│   ├── ostree.py
│   ├── runner.py
│   ├── simple.py
│   ├── utils.py
│   ├── version.py
│   ├── vm.py
│   └── vmhelper.py
├── build/
│   └── build-rpm.sh
├── ci-scripts/
│   └── run_tmt_tests.sh
├── distro/
│   ├── autosd10-latest-sig.ipp.yml
│   ├── autosd9-latest-sig.ipp.yml
│   ├── autosd9-latest-sig.ipp.yml
│   ├── autosd9-sig.ipp.yml
│   ├── autosd9.ipp.yml
│   ├── autosd9.ipp.yml
│   ├── eln.ipp.yml
│   ├── f40.ipp.yml
│   ├── f41.ipp.yml
│   ├── rhivos1.ipp.yml
│   └── rhivos1.ipp.yml
├── docs/
├── examples/
│   ├── complex.aib.yml
│   ├── container.aib.yml
│   ├── lowlevel.mpp.yml
│   ├── qm.aib.yml
│   └── simple.aib.yml
├── files/
│   ├── dnf-aibvm-init.conf
│   ├── manifest_schema.yml
│   └── simple.mpp.yml
├── include/
│   ├── arch-aarch64.ipp.yml
│   ├── arch-x86_64.ipp.yml
│   ├── build.ipp.yml
│   ├── computed-vars.ipp.yml
│   ├── content.ipp.yml
│   ├── data.ipp.yml
│   ├── defaults-computed.ipp.yml
│   ├── defaults.ipp.yml
│   ├── empty.ipp.yml
│   ├── image.ipp.yml
│   ├── main.ipp.yml
│   ├── mode-image.ipp.yml
│   ├── mode-package.ipp.yml
│   └── qm.ipp.yml
├── mpp/
│   └── aibosbuild/
│       └── util/
│           ├── __init__.py
│           ├── bls.py
│           ├── checksum.py
│           ├── containers.py
│           ├── ctx.py
│           ├── fscache.py
│           ├── jsoncomm.py
│           ├── linux.py
│           ├── lorax.py
│           ├── lvm2.py
│           ├── mnt.py
│           ├── osrelease.py
│           ├── ostree.py
│           ├── parsing.py
│           └── path.py
├── targets/
│   ├── _abootqemu.ipp.yml
│   ├── _abootqemukvm.ipp.yml
│   ├── _ridesx4_r3.ipp.yml
│   ├── _ridesx4_scmi.ipp.yml
│   ├── abootqemu.ipp.yml
│   ├── abootqemukvm.ipp.yml
│   ├── am62sk.ipp.yml
│   ├── am69sk.ipp.yml
│   ├── aws.ipp.yml
│   ├── beagleplay.ipp.yml
│   ├── ccimx93dvk.ipp.yml
│   ├── j784s4evm.ipp.yml
│   ├── pc.ipp.yml
│   ├── qdrive3.ipp.yml
│   ├── qemu.ipp.yml
│   ├── rcar_s4.ipp.yml
│   ├── rcar_s4_can.ipp.yml
│   ├── ridesx4.ipp.yml
│   ├── ridesx4_r3.ipp.yml
│   ├── ridesx4_scmi.ipp.yml
│   ├── rpi4.ipp.yml
│   ├── s32g_vnp_rdb3.ipp.yml
│   └── tda4vm_sk.ipp.yml
├── tests/
│   ├── plans/
│   │   ├── connect.fmf
│   │   └── local.fmf
│   ├── scripts/
│   │   ├── cleanup.sh
│   │   ├── rebuild-package.sh
│   │   ├── setup-lib.sh
│   │   ├── setup-local.sh
│   │   ├── setup-repos.sh
│   │   └── test-lib.sh
│   ├── tests/
│   │   ├── add-files/
│   │   │   ├── custom-files.aib.yml
│   │   │   ├── main.fmf
│   │   │   └── test-add-files.sh
│   │   ├── container-image/
│   │   │   ├── main.fmf
│   │   │   ├── test-container-image.sh
│   │   │   └── test.aib.yml
│   │   ├── denylist-modules/
│   │   │   ├── main.fmf
│   │   │   ├── test-denylist-modules.sh
│   │   │   └── test.aib.yml
│   │   ├── denylist-rpms/
│   │   │   ├── main.fmf
│   │   │   ├── test-denylist-rpms.sh
│   │   │   └── test.aib.yml
│   │   ├── install-rpms/
│   │   │   ├── main.fmf
│   │   │   ├── test-install-rpms.sh
│   │   │   └── test.aib.yml
│   │   └── main.fmf
│   ├── README.md
│   ├── run_aws.sh
│   ├── test-compose.json
│   └── test.mpp.yml
├── .gitignore
├── .gitlab-ci.yml
├── Containerfile
├── README.md
└── tox.ini
```

### Architecture Patterns
**Code Organization:** The project follows a **Configuration-Driven Architecture**. The core application logic in the `aib` Python package acts as an orchestrator that processes declarative YAML files. It's structured as a modular command-line tool with a clear separation of concerns: CLI parsing (`main.py`), execution logic (`runner.py`), and domain-specific modules (`ostree.py`, `vm.py`).
**Key Components:**
- **`aib.main`**: The main entry point. It handles command-line argument parsing using `argparse` and orchestrates the overall build flow.
- **`aib.runner`**: Contains the primary execution logic that interprets the parsed configuration and runs the build process, likely by invoking external tools like `osbuild`.
- **`aib.simple.ManifestLoader`**: Responsible for loading, parsing, and merging the various `.ipp.yml` and `.aib.yml` configuration files that define the build.
- **YAML Manifests (`.ipp.yml`, `.aib.yml`)**: These files are not code but are central to the architecture. They declaratively define the image to be built, including distribution, target hardware, and content. The system uses an include mechanism (`.ipp.yml`) to compose configurations.
**Entry Points:** The primary entry point is the command-line interface defined in `aib/main.py`. A typical flow involves a user invoking the tool with a primary manifest file (e.g., `simple.aib.yml`) and command-line flags. The application then discovers and merges included YAML files from the `distro/`, `include/`, and `targets/` directories to create a final build specification, which is then executed by the `Runner`.

### Important Files for Review Context
- **`aib/main.py`**: As the main entry point, this file is critical for understanding how user input (CLI arguments) is translated into application behavior and how the different components (`Runner`, `ManifestLoader`, etc.) are initialized and called.
- **`aib/runner.py`**: This module likely contains the core, stateful logic for executing the build process. Changes here can affect the entire build pipeline, so understanding its responsibilities is essential for reviewing any functional changes.
- **`examples/simple.aib.yml`**: To effectively review code changes, one must understand the structure and schema of the YAML configuration files that drive the application. This file provides a clear example of the primary user-facing input format.

### Development Conventions
- **Naming:** The code follows standard Python PEP 8 conventions (e.g., `snake_case` for functions and variables). A key project-specific convention is the use of the `.ipp.yml` file extension for composable YAML configuration snippets.
- **Module Structure:** The main application logic is contained within the `aib` package, with modules organized by functionality (e.g., `ostree`, `vm`, `utils`). A separate `mpp` package appears to contain lower-level utility functions.
- **Configuration:** The application is heavily reliant on YAML files for configuration. A hierarchical or compositional pattern is used, where base templates from `include/` are combined with specifics from `distro/` and `targets/`.
- **Testing:** The project employs a two-tiered testing strategy. Unit tests for the Python code are located in `aib/tests/`. Higher-level integration and end-to-end tests are in the root `tests/` directory, managed by the Test Management Tool (tmt) as indicated by `.fmf` files, and executed via shell scripts.

## Code Review Focus Areas

- **[Specific Technical Area]** - **File System and Path Manipulation:** The code extensively uses `os`, `shutil`, and `tempfile` for path construction and file management (e.g., `list_ipp_items`). Scrutinize all file system operations for correctness and security. Verify the consistent use of `os.path.join` for cross-platform compatibility and ensure that temporary files/directories are created securely and cleaned up properly.

- **[Architecture/Pattern Area]** - **Configuration-Driven Logic:** The application's behavior is driven by parsing `.ipp.yml` files using the `yaml` library and a `ManifestLoader`. Review changes to this parsing logic for robustness. Ensure that schema changes are handled gracefully, new configuration options have proper validation and defaults, and error messages for malformed YAML/JSON are clear and specific.

- **[Code Quality Area]** - **Custom Exception Handling:** The project uses a dedicated `.exceptions` module. Enforce the use of these custom, specific exceptions over generic ones (`Exception`, `RuntimeError`). Review `try...except` blocks to ensure they catch the correct exceptions and provide meaningful, user-facing error messages, especially around external processes and file I/O.

- **[Domain-Specific Area]** - **OS Image Build Orchestration:** The presence of `osbuild`, `ostree`, and `vmhelper` indicates this tool orchestrates Linux OS image creation. This is the core domain. Focus reviews on the logic that translates input configurations (`.ipp.yml`) into `osbuild` manifests. Pay close attention to how image layers, package sets, repositories, and post-build exports are defined, as errors here directly impact the final OS image artifact.

## Library Documentation & Best Practices

*Library documentation not available*

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