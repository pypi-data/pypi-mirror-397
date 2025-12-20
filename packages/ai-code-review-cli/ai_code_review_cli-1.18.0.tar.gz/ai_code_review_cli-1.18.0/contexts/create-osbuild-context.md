# Project Context for AI Code Review

## Project Overview

**Purpose:** An automation wrapper for building Linux operating system images specialized for the automotive sector, with complete CI/CD integration for automated image construction, testing, and cloud distribution.
**Type:** Shell-based automation tool / CI/CD pipeline component
**Domain:** Automotive Linux Build Systems & Infrastructure
**Key Dependencies:** `TMT` (test management), `Testing Farm` (IaaS), `AIB` (Automotive Image Builder), `OSBuild` (build engine), `AWS CLI` (cloud distribution)

## Technology Stack

### Core Technologies
- **Primary Language:** Shell (Bash)
- **Framework/Runtime:** TMT (Test Management Tool) with Testing Farm integration
- **Architecture Pattern:** Modular function-based shell scripting with containerized builds

### Key Dependencies (for Context7 & API Understanding)
- **TMT** - Test Management Tool that orchestrates the complete build workflow through `.fmf` test plans. Understanding TMT plan structure is essential for reviewing workflow changes.
- **Testing Farm** - Infrastructure as a Service that provisions VMs for builds. Provides multi-architecture support (x86_64, aarch64) and integration with CI/CD systems.
- **AIB (Automotive Image Builder)** - High-level manifest processor that abstracts OSBuild complexity. Reviewers must understand AIB options (`--distro`, `--target`, `--mode`, `--export`) and manifest structure.
- **OSBuild** - Low-level deterministic build engine. Executes inside containers with specific dependency requirements.
- **AWS CLI** - Used for S3 uploads, EC2 AMI creation, snapshot management, and cross-region image distribution.
- **ShellSpec** - Testing framework for shell scripts. Code changes should include corresponding ShellSpec tests with mock patterns.
- **podman** - Container runtime for executing builds in isolated environments.

### Development Tools & CI/CD
- **Testing:** `shellspec>=0.28.1` with `kcov` for coverage reporting
- **Code Quality:** `shellcheck` for static analysis, `yamllint`, `markdownlint`, `gitleaks` for security
- **Build/Package:** Container-based build system using `Containerfile`
- **CI/CD:** GitLab CI/CD (`.gitlab-ci.yml`) integrated with Testing Farm and pipelines-as-code

## Architecture & Code Organization

### Project Organization
```
create-osbuild/
├── bin/
│   ├── create-osbuild.sh     # Main build orchestrator
│   ├── clone-repo.sh         # Repository cloning with retry logic
│   ├── sync-to-aws.sh        # AWS upload and AMI creation
│   └── check-image-size.sh   # Image validation
├── lib/
│   ├── create-osbuild.sh     # Core build logic and variable management
│   ├── aws.sh                # AWS operations (S3, AMI, cross-region)
│   ├── build-env.sh          # Container management
│   └── clone-repo.sh         # Git operations
├── plans/
│   ├── local.fmf             # Local development/testing plan
│   └── create-osbuild.fmf    # Main CI/CD TMT plan
├── spec/
│   ├── lib/                  # ShellSpec unit tests
│   │   ├── create-osbuild_spec.sh
│   │   ├── aws_spec.sh
│   │   ├── build-env_spec.sh
│   │   └── clone-repo_spec.sh
│   └── support/
│       └── test_helpers.sh   # Shared mocks and utilities
└── builder/
    └── Containerfile         # Container build context
```

### Architecture Patterns
**Code Organization:** Function-based modular architecture. The project separates orchestration (`bin/` scripts) from implementation (`lib/` functions). Each library file contains related functions with clear responsibilities: `lib/create-osbuild.sh` for build logic, `lib/aws.sh` for cloud operations, `lib/build-env.sh` for container management.

**Key Components:**
- **`set_vars()`** in `lib/create-osbuild.sh`: Central variable initialization and validation. Sets all defaults and derives computed variables. Changes here impact the entire system.
- **`set_osbuild_options()`** in `lib/create-osbuild.sh`: Configures AIB command-line options based on environment variables. Handles special cases like debug images, SSH configuration, and custom kernel packages.
- **`build_target()`** in `lib/create-osbuild.sh`: Executes the actual image build using AIB in a containerized environment.
- **AWS Functions** in `lib/aws.sh`: `upload_to_s3()`, `create_ami()`, `copy_image()`, `grant_image_permissions()` - Handle complete AWS workflow including cross-region AMI distribution.
- **TMT Plans** in `plans/*.fmf`: Define the execution workflow. The main plan (`create-osbuild.fmf`) is the entry point for pipelines-as-code.

**Entry Points:** The application is executed through TMT plans. The main entry point is `plans/create-osbuild.fmf` which orchestrates four sequential steps: repository cloning, image building, size validation, and AWS upload. For local development, use `plans/local.fmf`.

### Important Files for Review Context
- **`lib/create-osbuild.sh`** - Core build logic. Contains `set_vars()`, `set_osbuild_options()`, and `build_target()`. Understanding this file is crucial as it manages all configuration and build execution.
- **`lib/aws.sh`** - All AWS operations including the new cross-region AMI sharing functionality. Critical for changes affecting cloud distribution.
- **`bin/create-osbuild.sh`** - Main orchestrator that sources `lib/create-osbuild.sh` and executes the build workflow. Entry point for understanding execution flow.
- **`plans/create-osbuild.fmf`** - TMT plan that defines the CI/CD workflow. Changes here affect how the pipeline executes in Testing Farm.

### Development Conventions
- **Naming:** Functions use `snake_case` (e.g., `set_vars`, `upload_to_s3`). Environment variables use `UPPER_SNAKE_CASE` (e.g., `PACKAGE_SET`, `BUILD_TARGET`). Local variables within functions use lowercase `snake_case`. AWS-related variables are prefixed with `AWS_` (e.g., `AWS_REGION`, `AWS_TF_ACCOUNT_ID`).
- **Error Handling:** All scripts use `set -euxo pipefail` for fail-fast behavior. Functions validate input parameters with explicit error messages to stderr. Exit codes are consistent: `0` for success, `1` for general errors, `5` for invalid parameters.
- **Module Structure:** Clear separation between `bin/` (executable scripts) and `lib/` (reusable functions). The `lib/` directory contains the core logic and is the primary focus for unit testing.
- **Testing:** ShellSpec tests in `spec/lib/` mirror the structure of `lib/`. Tests use mock functions for external dependencies (AWS CLI, git, podman). Coverage focuses on `lib/` functions, not `bin/` orchestration scripts.

## Code Review Focus Areas

- **[Variable Configuration and Validation]** - The `set_vars()` function in `lib/create-osbuild.sh` is the heart of the system. Review changes for: correct default values, proper variable derivation (e.g., `BASE_TARGET` from multiple variables), validation of boolean variables (`TEST_IMAGE`, `IMPORT_IMAGE`), and handling of complex variables like `IMAGE_TYPE` with `@debug` suffix. Common errors include `BASE_URL` misconfiguration across different streams and improper `KERNEL_RPM` validation.

- **[Stream-Based Configuration Logic]** - The `STREAM` variable (`upstream` vs `downstream`) affects repositories, container registries, release naming, and AWS sharing behavior. When reviewing stream-related changes: verify `BASE_URL` selection, check container registry logic, validate release naming patterns, and ensure AWS cross-region sharing is only enabled for upstream. Stream logic appears in multiple locations and must remain consistent.

- **[AWS Cross-Region AMI Sharing]** - New functionality in `lib/aws.sh` for distributing AMIs across regions and accounts. Key functions: `copy_image()` copies AMI between regions, `grant_image_permissions()` handles both public and private sharing, `task_progress()` monitors copy completion. For upstream builds, AMI is copied from `AWS_TF_REGION` to `AWS_CKI_REGION` with permissions granted to respective accounts. Verify proper error handling, region validation, and account ID management.

- **[AIB Options Configuration]** - The `set_osbuild_options()` function builds the AIB command dynamically. Critical areas: debug boot partition size for `@debug` images (uses `--abootpart-size` and `--ukibootpart-size`), SSH key injection for test images, custom kernel package handling with `--kernel-rpm`, module signature enforcement with `--module-sig-enforce`, and custom image size with `--image-size`. Ensure options are only added when conditions are met.

- **[Container Build and Registry Management]** - Functions in `lib/build-env.sh` handle container building and registry operations. Review for: proper python3-jsonschema dependency installation (was a recent bug fix), registry authentication logic, USE_LATEST vs specific container tags, and stream-specific container image selection. Container failures are a common issue and proper error handling is critical.

- **[S3 Upload Directory Selection]** - Complex priority logic in `lib/aws.sh` function `set_s3_upload_prefix()` determines upload path: (1) `OSTREE_REPO=yes` → `ostree-repos/`, (2) Custom `S3_UPLOAD_DIR`, (3) `IMPORT_IMAGE=True` → `raw-images/`, (4) `SAMPLE_IMAGE=True` → `sample-images/`, (5) Default → `non-sample-images/`. Verify new variables don't break this priority chain and that the logic remains clear.

- **[ShellSpec Test Coverage and Mocking]** - All changes to `lib/*.sh` functions must include corresponding ShellSpec tests. Tests must mock external dependencies (AWS CLI, git, podman, curl). Review for: proper mock function structure, test isolation (BeforeEach/AfterEach cleanup), comprehensive scenario coverage (success and failure paths), and proper variable setup in test environment. Test helpers in `spec/support/test_helpers.sh` should be reused.

## Library Documentation & Best Practices

### 1. Shell Scripting Patterns

*   **Error Handling:** All scripts must start with `set -euxo pipefail` to enable: `-e` (exit on error), `-u` (error on undefined variable), `-x` (print commands for debugging), `-o pipefail` (pipeline fails if any command fails).
    ```bash
    #!/bin/bash
    set -euxo pipefail
    
    # Function parameter validation
    function my_function() {
        if [[ $# -ne 2 ]]; then
            echo "ERROR: Expecting 2 parameters but got $#" >&2
            return 5
        fi
        local param1="$1"
        local param2="$2"
        # Function logic
    }
    ```

*   **Variable Quoting:** Always quote variables in command contexts to prevent word splitting and glob expansion: `"${VARIABLE}"`. Use `${VARIABLE:-default}` for default values. Arrays should use `"${array[@]}"` for proper element handling.

*   **Function Design:** Functions should validate input parameters, use local variables for internal state, return consistent exit codes (0 for success, non-zero for errors), and output results via stdout while errors go to stderr.

*   **TMT Plan Structure:** Plans use YAML format with three main sections: `provision` (VM setup), `prepare` (dependency installation), `execute` (test execution). Environment variables are passed through the `environment:` key and can reference pipeline variables with `${VAR}` syntax.
    ```yaml
    summary: Create image using osbuild
    environment:
      PACKAGE_SET: cs9
      BUILD_TARGET: qemu
    execute:
      how: tmt
      exit-first: true  # Stop on first failure
    ```

*   **Container Operations:** Container images should be built with descriptive tags (`localhost/builder:latest`). Use `--rm` for automatic cleanup. Mount working directory with `-v` and set working directory with `-w`. For AIB execution, ensure proper user ID mapping and device access.

### 2. Best Practices

*   **Environment Variable Management:** Use descriptive names with consistent prefixes (`AWS_`, `S3_`, `DEBUG_`). Provide sensible defaults in `set_vars()`. Document all variables in code comments. Validate boolean variables with regex: `[[ "${VAR}" =~ ^(True|yes)$ ]]`.

*   **AWS Operations:** Always check AWS CLI return codes. Use `--output json` for machine-parseable responses and `jq` for parsing. Implement retry logic for transient failures. Tag all resources with `Name`, `UUID`, and `Release` tags. For AMI operations, verify snapshot and image states before proceeding.

*   **Container Build:** Pre-install python3-jsonschema in container images to avoid AIB manifest preprocessing errors. Use multi-stage builds to minimize image size. Pin base image versions for reproducibility. Configure repositories with GPG check appropriately (disabled for nightly, enabled for releases).

*   **Testing Practices:**
    *   Mock all external commands (aws, git, podman, curl) in ShellSpec tests
    *   Use `Include ./lib/filename.sh` to source the code under test
    *   Create setup/teardown with `BeforeEach`/`AfterEach` hooks
    *   Test both success and failure scenarios
    *   Use temporary directories that are cleaned up automatically
    *   Example mock pattern:
    ```bash
    setup_mocks() {
      aws() { echo '{"ImageId": "ami-test"}'; }
      git() { case "$1" in "clone") echo "Cloned" ;; esac; }
    }
    ```

*   **Logging and Debugging:** Use `echo` for informational messages and progress updates. Direct errors to stderr with `>&2`. Save AIB manifests and OSBuild logs for debugging (`save_files()` function). For TMT debugging, use `tmt run ... login --step execute --when error` to access failed build environment.

### 3. Common Pitfalls

*   **Unquoted Variables:** Using `$VAR` instead of `"${VAR}"` can cause word splitting. Always quote variables in command contexts. Particularly critical for paths and filenames.

*   **BASE_URL Configuration:** Frequently misconfigured. For upstream: uses AutoSD repositories. For downstream: uses RHIVOS repositories. Must match the container registry selection. Different for different `STREAM` values.

*   **IMAGE_TYPE Suffix Handling:** The `@debug` suffix is special and triggers debug-specific configuration (larger boot partition). Code must use regex matching: `[[ "${IMAGE_TYPE}" =~ @debug$ ]]`. Don't strip the suffix when passing to AIB.

*   **AWS Region Confusion:** `AWS_REGION` (primary region), `AWS_TF_REGION` (Testing Farm primary), `AWS_CKI_REGION` (Testing Farm secondary). Cross-region logic only applies to upstream stream. Mixing these variables causes sharing failures.

*   **Container Dependency Missing:** AIB manifest preprocessing requires python3-jsonschema inside the container. This was a bug that was fixed by adding it to the Containerfile. Regressions cause cryptic AIB errors about manifest processing.

*   **TMT Exit-First Behavior:** The `exit-first: true` setting in TMT plans causes the pipeline to stop on the first test failure. This means if repository cloning fails, subsequent steps won't run. Design tests with this in mind.

### 4. Integration Recommendations

*   **GitLab CI Integration:** The project is designed to be called from GitLab CI pipelines through Testing Farm. Pipeline variables are passed as environment variables to the TMT plan. Use `.gitlab-ci.yml` extends pattern for consistency.

*   **Testing Farm Workflow:** Testing Farm receives API request with TMT plan reference → Provisions VM (usually CentOS Stream 9) → Executes TMT plan → Returns artifacts. Plan execution is isolated per build.

*   **AIB Manifest Flow:** YAML manifest (`.aib.yml`) → AIB preprocessor (`aib-osbuild-mpp`) → JSON OSBuild manifest → OSBuild execution → Final image. Reviewers should understand this flow when debugging manifest-related issues.

*   **AWS Distribution Flow:** Build image → Compress with xz → Generate SHA256 → Upload to S3 → (Optional) Import snapshot → Create AMI → (Upstream only) Copy to secondary region → Grant permissions to Testing Farm accounts.

### 5. Configuration Guidelines

*   **Stream Selection:** Set `STREAM=upstream` for AutoSD/CentOS builds with public AMI sharing. Set `STREAM=downstream` for RHIVOS builds with private AMI sharing. This affects repositories, container registries, release naming, and AWS sharing behavior.

*   **Debug Images:** Use `IMAGE_TYPE=ostree@debug` or `IMAGE_TYPE=package@debug` for debug images. Set `DEBUG_BOOT_PARTITION_SIZE=380928` (186 MB default) for enlarged boot partitions. Debug images only affect `aboot` and `ukiboot` targets.

*   **Testing Images:** Set `TEST_IMAGE=yes` to enable SSH with root login. Provide `SSH_KEY` for key-based authentication. Password auth is disabled by default (`ENABLE_SSH_PASSWORD_AUTH=false`). Test images include additional packages: openssh-server, python3, polkit, rsync.

*   **Custom Image Size:** Set `SET_IMAGE_SIZE=true` and `IMAGE_SIZE=4294967296` (bytes) for custom disk sizes. Useful for hardware platforms with specific size requirements. Default size is platform-dependent.

*   **ShellCheck Configuration:** In `.shellcheckrc` or as comments in scripts, disable specific checks if necessary with `# shellcheck disable=SC####`. Document why the check is disabled. Common disables: SC2086 (intentional word splitting), SC2155 (declare and assign separately).

---
<!-- MANUAL SECTIONS - DO NOT MODIFY THIS LINE -->

### Business Logic & Implementation Decisions

- **TMT Plan as Entry Point**: The project is designed to run through TMT plans, not as standalone scripts. This is intentional for integration with pipelines-as-code and Testing Farm. Direct script execution is for development/debugging only.

- **Container-Based Builds**: All OSBuild operations execute inside containers to ensure reproducible builds with correct dependencies. The `USE_LATEST` flag controls whether to build containers locally or pull pre-built ones.

- **Cross-Region AMI Sharing**: Only enabled for `STREAM=upstream` builds. Downstream builds are private and don't need multi-region distribution. This reduces AWS costs and maintains security boundaries.

- **Debug Boot Partition Size**: The larger boot partition (186 MB vs default) for debug images is intentional to accommodate additional debugging tools and kernel debug symbols. Only affects Android Boot and UKI boot images.

- **S3 Directory Organization**: The priority-based directory selection allows different artifact types to be organized logically. OSTree repos are separate from images, raw images for AMI import are isolated, and sample images are distinguished from production images.

- **Exit-First TMT Behavior**: The pipeline stops on first failure to avoid wasting resources. For example, if repository cloning fails, there's no point in attempting the build.

### Domain-Specific Context

- **Automotive Linux Ecosystem**: The project targets **AutoSD** (CentOS Stream Automotive) and **RHIVOS** (Red Hat In-Vehicle Operating System). These are specialized Linux distributions for automotive use cases with specific security and functional safety requirements.

- **OSTree vs Package Images**: OSTree images (`IMAGE_TYPE=ostree`) are immutable, atomic-update systems preferred for production. Package images (`IMAGE_TYPE=package`) are traditional mutable systems used for development and debugging.

- **Hardware Platform Specifics**: 
  - `qemu` - Virtual machines for testing
  - `ami` - AWS EC2 instances (derived from qemu)
  - `rcar_s4` - Renesas R-Car S4 automotive SoC
  - `qdrive3` - Qualcomm automotive platform (uses special kernel options `PARTLABEL=userdata`)
  - `rpi4` - Raspberry Pi 4 for development

- **Image Format Selection**:
  - `qcow2` - Compressed VM images, efficient for development
  - `raw` - Uncompressed disk images, required for AMI import
  - `aboot.simg` - Android Boot v2 sparse image format for embedded hardware

- **AIB vs OSBuild**: AIB (Automotive Image Builder) provides high-level YAML manifests with automotive-specific features. OSBuild is the underlying engine that does the actual image construction. Reviewers should understand this layering.

- **Testing Farm Account Management**: Separate AWS accounts for public Testing Farm (`AWS_TF_ACCOUNT_ID`) and internal Testing Farm (`AWS_CKI_ACCOUNT_ID`). Public account for upstream community, internal account for Red Hat downstream builds.

### Special Cases & Edge Handling

- **SSL Verification Bypass**: Set `SSL_VERIFY=false` to disable SSL verification for git operations. Needed for self-hosted GitLab instances with self-signed certificates. Security consideration: only use in trusted environments.

- **Release vs Nightly Builds**: Release builds (e.g., `RELEASE=AutoSD-9.0`) are kept permanently in S3. Nightly builds (`RELEASE=nightly`) are temporary and may be cleaned up. S3 lifecycle policies differ based on release classification.

- **Image Size Constraints**: The `check-image-size.sh` script validates that `aboot.simg` images don't exceed hardware-specific size limits. QDrive3 and RCar S4 have different maximum sizes. Exceeding these limits causes boot failures on actual hardware.

- **python3-jsonschema Dependency**: Recent bug fix added this to container images. Without it, AIB manifest preprocessing fails with obscure errors. Watch for regressions if container building changes.

- **Hardware-Specific Kernel Options**: QDrive3 requires `PARTLABEL=userdata` kernel option. Other platforms use `PARTLABEL=system_a`. This is hardcoded based on `BUILD_TARGET` and reviewers should verify new platforms have appropriate options.

- **Empty SSH_KEY Handling**: If `TEST_IMAGE=yes` but `SSH_KEY` is empty, the build should still succeed but SSH access will be limited. This is intentional for automated testing scenarios where SSH access isn't needed.

- **Container Registry Authentication**: Authentication to private container registries (e.g., Red Hat registries) is handled through pre-configured credentials. Missing or expired credentials cause container pull failures. Not all builds require authentication (public registries don't).

- **TMT Provision Image Selection**: The provision image (`centos-stream-9`) must match or be compatible with the target distribution. Mismatches can cause dependency resolution failures during build environment setup.

- **AWS CLI Version Sensitivity**: Cross-region AMI operations require AWS CLI v2 for best compatibility. Some older AWS CLI v1 commands have different JSON output formats. Test AWS operations with expected CLI versions.

- **ShellSpec Coverage Exclusions**: The `bin/` directory is excluded from coverage metrics because these are orchestration scripts that wrap `lib/` functions. Coverage focus is on testable, reusable functions in `lib/`.

### Variable Configuration Reference

**Critical Environment Variables:**

```bash
# Build Configuration (affect image content and structure)
PACKAGE_SET=cs9              # Distribution: cs9, autosd9, rhivos9
BUILD_TARGET=qemu            # Platform: qemu, ami, rcar_s4, qdrive3, rpi4
BUILD_FORMAT=qcow2          # Format: qcow2, raw, aboot.simg
IMAGE_TYPE=ostree           # Type: ostree, ostree@debug, package, package@debug
ARCH=x86_64                 # Architecture: x86_64, aarch64
IMAGE_NAME=minimal          # Variant: minimal, standard, developer

# Stream Configuration (affect build environment and distribution)
STREAM=upstream             # Stream: upstream, downstream
DEBUG_BOOT_PARTITION_SIZE=380928  # Debug boot partition size in KB (186 MB)
SET_IMAGE_SIZE=false       # Enable custom image size
IMAGE_SIZE=4294967296      # Custom size in bytes (4 GB default)

# Testing Configuration (affect SSH and test packages)
TEST_IMAGE=yes             # Enable SSH: yes, no, True, False
SSH_KEY="ssh-rsa ..."      # SSH public key for root access
ENABLE_SSH_PASSWORD_AUTH=false  # Enable password authentication

# Container Configuration (affect build environment)
USE_LATEST=False           # Use pre-built container: True, False
USE_AIB_RPM=False          # Install AIB from RPM: True, False
CONTAINER_REGISTRY=quay.io # Registry URL

# AWS Configuration (affect cloud distribution)
AWS_REGION=us-east-1       # Primary AWS region
S3_BUCKET_NAME=autosd-artifacts  # S3 bucket for uploads
IMPORT_IMAGE=True          # Create AMI: True, False
S3_UPLOAD_DIR=""           # Custom S3 directory (optional)
SAMPLE_IMAGE=yes           # Mark as sample: yes, no
OSTREE_REPO=yes            # OSTree repo upload: yes, no

# AWS Cross-Region Configuration (only for upstream)
AWS_TF_REGION=us-east-1    # Testing Farm primary region
AWS_TF_ACCOUNT_ID=123456789012  # Public Testing Farm account
AWS_CKI_REGION=us-west-2   # Testing Farm secondary region
AWS_CKI_ACCOUNT_ID=987654321098  # Internal Testing Farm account

# Advanced Configuration (uncommon use cases)
KERNEL_RPM=""              # Custom kernel package (optional)
USE_MODULE_SIG_ENFORCE=true  # Enforce kernel module signatures
SSL_VERIFY=true            # Git SSL verification
```

**Variable Validation Patterns:**

- Boolean variables accept: `True`, `true`, `yes`, `False`, `false`, `no`
- Regex pattern for validation: `[[ "${VAR}" =~ ^(True|yes)$ ]]`
- Undefined variables fail with `set -u` unless defaults are provided
- Invalid values should fail with clear error messages

### Common Error Patterns and Solutions

**Error: "AIB manifest preprocessing failed"**
- **Cause:** Missing python3-jsonschema in container
- **Solution:** Ensure container has python3-jsonschema installed
- **Prevention:** Don't remove jsonschema from Containerfile

**Error: "AMI sharing failed"**
- **Cause:** Incorrect AWS region or account ID configuration
- **Solution:** Verify `AWS_TF_REGION`, `AWS_CKI_REGION`, `AWS_TF_ACCOUNT_ID`, `AWS_CKI_ACCOUNT_ID`
- **Prevention:** Use consistent region/account variables, test with dry-run

**Error: "Image size exceeds limit"**
- **Cause:** aboot.simg image too large for hardware
- **Solution:** Reduce image content or adjust IMAGE_SIZE
- **Prevention:** Check hardware specifications before build

**Error: "Container pull failed"**
- **Cause:** Registry authentication missing or expired
- **Solution:** Refresh registry credentials
- **Prevention:** Use USE_LATEST=False for local builds

**Error: "Git clone failed with SSL error"**
- **Cause:** Self-signed certificate on GitLab instance
- **Solution:** Set SSL_VERIFY=false
- **Prevention:** Use proper SSL certificates in infrastructure

**Error: "BASE_URL incorrect for stream"**
- **Cause:** BASE_URL doesn't match STREAM configuration
- **Solution:** Verify BASE_URL uses correct repository for upstream/downstream
- **Prevention:** Always set BASE_URL based on STREAM value

### Review Checklist for Common Changes

**When reviewing variable changes in `lib/create-osbuild.sh:set_vars()`:**
- [ ] New variables have sensible defaults
- [ ] Boolean variables use consistent validation pattern
- [ ] Computed variables derive correctly from inputs
- [ ] Stream-specific logic is consistent
- [ ] Documentation comments explain non-obvious variables

**When reviewing AIB options in `lib/create-osbuild.sh:set_osbuild_options()`:**
- [ ] Options only added when conditions are met
- [ ] Debug image logic checks for `@debug` suffix
- [ ] SSH configuration handles TEST_IMAGE correctly
- [ ] Custom kernel package validated before use
- [ ] Image size only set when SET_IMAGE_SIZE=true

**When reviewing AWS operations in `lib/aws.sh`:**
- [ ] Error handling for all AWS CLI calls
- [ ] Region variables used consistently
- [ ] Account ID variables validated
- [ ] Cross-region logic only for upstream
- [ ] Resource tagging includes Name, UUID, Release

**When reviewing container changes in `lib/build-env.sh`:**
- [ ] python3-jsonschema dependency present
- [ ] Registry authentication handled
- [ ] Container tags are meaningful
- [ ] Stream-specific selection works
- [ ] Error messages are clear

**When reviewing ShellSpec tests:**
- [ ] Mocks cover all external dependencies
- [ ] Tests for both success and failure paths
- [ ] Setup/teardown isolates test state
- [ ] Test data uses consistent patterns
- [ ] Coverage includes edge cases

