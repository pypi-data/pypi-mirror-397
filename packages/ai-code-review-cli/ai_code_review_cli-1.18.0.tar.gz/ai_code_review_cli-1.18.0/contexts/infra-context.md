# Project Context for AI Code Review

## Project Overview

**Purpose:** This project provides automation scripts for managing infrastructure across AWS, OpenShift, and GitLab.
**Type:** Automation Toolset
**Domain:** DevOps / Infrastructure as Code (IaC)
**Key Dependencies:** boto3 (AWS), ansible (Configuration Management), openshift (Kubernetes), python-gitlab (CI/CD)

## Technology Stack

### Core Technologies
- **Primary Languages:** HCL (Terraform), Python (scripting/automation), YAML (Ansible/K8s)
- **Infrastructure as Code:** Terraform (AWS resources), Ansible (configuration management)
- **Architecture Pattern:** GitOps-driven Infrastructure as Code (IaC)

### Key Dependencies (for Context7 & API Understanding)
- **terraform~=4.59.0** - The primary Infrastructure as Code tool for AWS resource management. Code reviews should focus on resource definitions, state management, module structure, and provider configurations.
- **ansible==8.4.0** - The core automation engine for OpenShift and Quay management. Code reviews should focus on playbook structure, idempotency, module usage, and variable management.
- **boto3==1.37.35** - The AWS SDK for Python. Reviews must check for correct AWS API usage, error handling, and IAM permission assumptions in automation scripts.
- **openshift==0.13.2** - A Python client for OpenShift/Kubernetes. Code changes using this will interact with cluster resources; check for correct object definitions and API calls.
- **python-gitlab==3.15.0** - A Python wrapper for the GitLab API. Used for automating GitLab operations. Review for proper API usage and secure handling of tokens.
- **ansible-lint==6.22.1** - A linter for Ansible playbooks. Its presence indicates a standard for playbook quality; reviews should enforce its rules.
- **PyYAML==6.0.1** - Used for parsing YAML files, which are central to Ansible, OpenShift, and GitLab CI. Review for correct data structure handling and use of safe loading practices.

### Development Tools & CI/CD
- **Testing:** None detected
- **Code Quality:** `ansible-lint==6.22.1` for Ansible playbooks, managed via `pre-commit`.
- **Build/Package:** None detected
- **CI/CD:** **gitlab-ci** - The `.gitlab-ci.yml` file defines the pipeline. Expect stages for linting (ansible-lint), validating configurations (e.g., `terraform validate`), and executing infrastructure changes via Ansible playbooks or Terraform.

## Architecture & Code Organization

### Project Organization
```
.
├── .gitlab/                                    # GitLab CI/CD templates and shared configurations
│   ├── templates/
│   │   └── ansible_openshift_template.yml
│   ├── ansible_common.yml
│   ├── ansible_openshift.yml
│   ├── ansible_quay.yml
│   ├── renovate.yml
│   ├── rules.yml
│   ├── terraform_aws-internal.yml
│   ├── terraform_aws.yml
│   ├── terraform_common.yml
│   └── terraform_gitlab.yml
├── aws/                                        # Public-facing AWS infrastructure
│   ├── download-server/
│   │   ├── README.md
│   │   ├── mount-on-reboot.txt
│   │   └── sync-releases-latest.sh
│   └── terraform/                              # Main Terraform configurations
│       ├── common/
│       │   └── bucket-public-read/
│       ├── kernel/                             # Kernel team resources
│       ├── toolchain/                          # Toolchain infrastructure
│       │   ├── common/
│       │   ├── downstream/                     # Downstream toolchain resources
│       │   ├── gitlab-docker-runner-pool/      # Auto-scaling GitLab runners
│       │   └── upstream/                       # Upstream toolchain resources
│       └── main.tf                            # Main entry point with module calls
├── aws-internal/                               # Internal/private AWS resources
│   └── modules/
│       ├── bring-your-own-script/              # Custom script deployment
│       ├── common/                             # Shared setup scripts
│       ├── gitlab-docker-runner-pool/          # Internal GitLab runners
│       ├── rhivos-cloudfront/                  # RHIVOS CloudFront distributions
│       ├── rhivos_dashboard/                   # RHIVOS dashboard infrastructure
│       └── test_console/                       # Testing/debugging environments
├── gitlab/                                     # GitLab infrastructure management
│   ├── cee/                                    # GitLab CEE configurations
│   │   ├── avatars/
│   │   └── modules/
│   │       ├── foa/                            # Follow-on-Activities modules
│   │       ├── template/                       # Template modules
│   │       └── toolchain/                      # Toolchain modules
│   └── com/                                    # GitLab.com configurations
├── openshift/                                  # OpenShift platform deployments
│   ├── bos2/                                   # Boston data center
│   │   ├── flasher/                            # Flasher application
│   │   └── sidekick-setup/                     # Sidekick setup automation
│   ├── managed-platform+/                      # MP+ applications
│   │   ├── arca-x/                             # Arca-X application
│   │   ├── auto-toolchain-dashboard/           # Toolchain dashboard
│   │   ├── autosd-webserver/                   # AutoSD web server
│   │   ├── contcert/                           # Continuous Certification
│   │   ├── gitlab-runners/                     # OpenShift GitLab runners
│   │   ├── jfrog-cli/                          # JFrog CLI tools
│   │   ├── rhivos-download-devel/              # RHIVOS download dev
│   │   ├── sea-bridge/                         # Sea-bridge application
│   │   └── test-console/                       # Debugging/testing tools
│   └── setup-resources/                        # Cluster-level resources
│       ├── bos2/                               # Boston setup resources
│       ├── iad2/                               # IAD2 setup resources
│       └── managed-platform+/                  # MP+ setup resources
├── quay/                                       # Quay registry management
│   └── auto-fusa/
│       ├── roles/
│       │   └── repositories/
│       ├── main.yml
│       └── requirements.yml
├── renovate/                                   # Dependency management
│   ├── Containerfile
│   └── README.md
├── .gitlab-ci.yml                             # Main CI/CD pipeline
├── .pre-commit-config.yaml                    # Code quality hooks
├── README.md                                  # Project documentation
└── requirements.txt                           # Python dependencies
```

### Architecture Patterns
**Code Organization:** GitOps-driven Infrastructure as Code (IaC). The project is organized by technology platform (`aws`, `openshift`, `gitlab`, `quay`), not by application feature. It uses a combination of declarative configuration (Terraform, Kubernetes YAML) and imperative automation (Ansible, Bash) to define and manage infrastructure and deployments.

**Key Components:**
- **Terraform Infrastructure (`aws/terraform/`, `aws-internal/`, `gitlab/`):** Primary IaC tool managing AWS cloud resources and GitLab configurations. Uses modular architecture with reusable modules (e.g., `aws-internal/modules/gitlab-docker-runner-pool`). State managed remotely in S3.
- **GitLab CI Pipelines (`.gitlab/`):** The central orchestrator using reusable templates to trigger Terraform plans/applies and Ansible deployments across different environments.
- **Ansible Application Management (`openshift/`, `quay/`):** Handles application deployment and configuration on OpenShift clusters and Quay registry management. Follows role-based structure with environment-specific variable files.
- **Operational Scripts (`aws/download-server/`):** Bash scripts for ongoing operational tasks on provisioned infrastructure, such as artifact synchronization and system maintenance.

**Entry Points:**
- **Primary:** GitLab CI pipeline (`.gitlab-ci.yml`) orchestrating all automation
- **Terraform:** Module entry points like `aws/terraform/main.tf` with locals and module calls
- **Ansible:** Playbooks like `openshift/bos2/flasher/main.yml` and `quay/auto-fusa/main.yml`
- **Operational:** Scripts like `sync-releases-latest.sh` executed via cron or CI jobs

### Important Files for Review Context
- **`.gitlab-ci.yml`**: Defines the main CI/CD pipeline. Understanding this file is critical to know how any code change is validated, built, and deployed across different environments.
- **`aws/terraform/main.tf`**: Primary Terraform entry point with global settings, module calls, and resource state management. Contains extensive `moved` blocks for resource refactoring and import statements.
- **`.gitlab/templates/`**: Reusable GitLab CI templates for Terraform and Ansible operations. These define standard processes for infrastructure validation and deployment.
- **`aws/download-server/sync-releases-latest.sh`**: Demonstrates the standard for operational shell scripting in the project, including robust error handling (`set -euo pipefail`), variable conventions, and interaction with the filesystem for release artifact management.
- **`openshift/bos2/flasher/vars/prod.yml`**: An example of environment-specific configuration. Reviewers must check these files to understand the impact of changes on different environments (e.g., dev vs. prod).
- **`aws-internal/modules/*/main.tf`**: Terraform module definitions showing the standard patterns for resource creation, variable handling, and module structure.

### Development Conventions
- **Naming:** Shell script variables are in `UPPER_SNAKE_CASE` (e.g., `RELEASES_DIR`), while functions are `lower_snake_case` (e.g., `get_timestamp`). Directory and file names are descriptive and kebab-cased (e.g., `sidekick-setup.yaml`). Terraform resources follow `kebab-case` naming.
- **Module Structure:** The project is modular, organized by technology. Terraform modules are reusable (e.g., `aws-internal/modules/gitlab-docker-runner-pool`). Ansible follows role-based structure (e.g., `quay/auto-fusa/roles/repositories`).
- **Configuration:** Clear separation of configuration from logic. Terraform uses `locals` blocks for global settings and variables for module inputs. Ansible uses environment-specific YAML variable files (e.g., `vars/dev.yml`, `vars/prod.yml`). Shell scripts define configuration as variables at the top.
- **State Management:** Terraform state is managed remotely in S3. Resource refactoring uses `moved` blocks to preserve state. Import statements handle existing resources.
- **Testing:** Code quality enforced through pre-commit hooks including security scans (AWS credentials, private keys, GitLeaks), YAML/JSON validation, and markdown linting as defined in `.pre-commit-config.yaml`.

## Code Review Focus Areas

- **[Critical Infrastructure Area] Terraform State Management** - This repository manages production infrastructure via Terraform with remote state in S3. Scrutinize any changes to `moved` blocks in `aws/terraform/main.tf` for correctness, as improper state movements can destroy resources. Verify that new resources use consistent naming patterns and that module calls include all required variables. Check for proper provider configurations and version constraints.

- **[Specific Technical Area] Shell Scripting Robustness** - The entry point is a Bash script (`sync-releases-latest.sh`) that performs critical file operations. Scrutinize changes for proper variable quoting (e.g., `"${variable}"`) to prevent word splitting issues, validate the reliability of parsing text files with `awk`, and ensure `rsync` commands have comprehensive error handling and logging, especially given the `set -euo pipefail` directive.

- **[Architecture/Pattern Area] Idempotency and GitOps Principles** - All infrastructure changes must be idempotent and declarative. For Terraform, verify resource configurations are complete and don't rely on external state. For Ansible playbooks, ensure tasks use state-checking modules (like `ansible.builtin.copy`) instead of commands that always execute (like `ansible.builtin.shell`). Validate that the GitOps workflow is preserved.

- **[Framework-Specific Area] Multi-Module Terraform Architecture** - The project uses extensive Terraform modules (`aws-internal/modules/*`). Review module interfaces for consistency, ensure proper variable typing and validation, check for circular dependencies, and verify that module outputs are properly exposed. Pay attention to resource naming conventions and tagging strategies across modules.

- **[Code Quality Area] Configuration and Secret Management** - Configuration values and secrets must be properly externalized. For Terraform, use variables and locals appropriately. For Ansible, use group_vars and vault. For shell scripts, avoid hardcoded paths and values. Verify that sensitive data (tokens, keys) is not committed to the repository and is properly managed through GitLab CI/CD variables or external secret management.

## Library Documentation & Best Practices



## CI/CD Configuration Guide

*CI/CD documentation not available*

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