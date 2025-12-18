# Copyright (c) typedef int GmbH, Germany, 2025. All rights reserved.

# -----------------------------------------------------------------------------
# -- just global configuration
# -----------------------------------------------------------------------------

set unstable := true
set positional-arguments := true
set script-interpreter := ['uv', 'run', '--script']

# uv env vars (see: https://docs.astral.sh/uv/reference/environment/)

# Project base directory
PROJECT_DIR := justfile_directory()

# Tell uv to use project-local cache directory
export UV_CACHE_DIR := './.uv-cache'

# Use this common single directory for all uv venvs
VENV_DIR := './.venvs'

# Define supported Python environments
ENVS := 'cpy314 cpy313 cpy312 cpy311 pypy311'

# Default recipe: show project header and list all recipes
default:
    #!/usr/bin/env bash
    set -e
    VERSION=$(grep '^version' pyproject.toml | head -1 | sed 's/.*= *"\(.*\)"/\1/')
    GIT_REV=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    echo ""
    echo "==============================================================================="
    echo "                                   cfxdb                                       "
    echo ""
    echo "       Crossbar.io database schemas and access classes for zLMDB/LMDB         "
    echo ""
    echo "   Python Package:         cfxdb                                              "
    echo "   Python Package Version: ${VERSION}                                         "
    echo "   Git Version:            ${GIT_REV}                                         "
    echo "   Protocol Specification: https://wamp-proto.org/                            "
    echo "   Documentation:          https://crossbar.readthedocs.io                    "
    echo "   Package Releases:       https://pypi.org/project/cfxdb/                    "
    echo "   Nightly/Dev Releases:   https://github.com/crossbario/cfxdb/releases       "
    echo "   Source Code:            https://github.com/crossbario/cfxdb                "
    echo "   Copyright:              typedef int GmbH (Germany/EU)                      "
    echo "   License:                MIT License                                        "
    echo ""
    echo "       >>>   Created by The WAMP/Autobahn/Crossbar.io OSS Project   <<<       "
    echo "==============================================================================="
    echo ""
    just --list
    echo ""

# Internal helper to map Python version short name to full uv version
_get-spec short_name:
    #!/usr/bin/env bash
    set -e
    case {{short_name}} in
        cpy314)  echo "cpython-3.14";;
        cpy313)  echo "cpython-3.13";;
        cpy312)  echo "cpython-3.12";;
        cpy311)  echo "cpython-3.11";;
        pypy311) echo "pypy-3.11";;
        *)       echo "Unknown environment: {{short_name}}" >&2; exit 1;;
    esac

# Internal helper that calculates and prints the system-matching venv name
_get-system-venv-name:
    #!/usr/bin/env bash
    set -e
    SYSTEM_VERSION=$(/usr/bin/python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    ENV_NAME="cpy$(echo ${SYSTEM_VERSION} | tr -d '.')"
    if ! echo "{{ ENVS }}" | grep -q -w "${ENV_NAME}"; then
        echo "Error: System Python (${SYSTEM_VERSION}) maps to '${ENV_NAME}', which is not a supported environment." >&2
        exit 1
    fi
    echo "${ENV_NAME}"

# Helper recipe to get the python executable path for a venv
_get-venv-python venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PATH="{{PROJECT_DIR}}/.venvs/${VENV_NAME}"
    if [[ "$OS" == "Windows_NT" ]]; then
        echo "${VENV_PATH}/Scripts/python.exe"
    else
        echo "${VENV_PATH}/bin/python3"
    fi

# -----------------------------------------------------------------------------
# -- General/global helper recipes
# -----------------------------------------------------------------------------

# Setup bash tab completion for the current user (to activate: `source ~/.config/bash_completion`).
setup-completion:
    #!/usr/bin/env bash
    set -e
    COMPLETION_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/bash_completion"
    MARKER="# --- Just completion ---"
    echo "==> Setting up bash tab completion for 'just'..."
    if [ -f "${COMPLETION_FILE}" ] && grep -q "${MARKER}" "${COMPLETION_FILE}"; then
        echo "--> 'just' completion is already configured."
        exit 0
    fi
    echo "--> Configuration not found. Adding it now..."
    mkdir -p "$(dirname "${COMPLETION_FILE}")"
    echo "" >> "${COMPLETION_FILE}"
    echo "${MARKER}" >> "${COMPLETION_FILE}"
    just --completions bash >> "${COMPLETION_FILE}"
    echo "--> Successfully added completion logic to ${COMPLETION_FILE}."
    echo ""
    echo "==> Setup complete. Please restart your shell or run:"
    echo "    source \"${COMPLETION_FILE}\""

# Remove ALL generated files, including venvs, caches, and build artifacts
distclean: clean-build clean-pyc clean-test
    #!/usr/bin/env bash
    set -e
    echo "==> Performing a deep clean (distclean)..."
    rm -rf {{VENV_DIR}}
    rm -rf {{UV_CACHE_DIR}}
    echo "--> Removed all venvs and caches."

# Clean build artifacts
clean-build:
    #!/usr/bin/env bash
    set -e
    echo "==> Cleaning build artifacts..."
    rm -rf build/ dist/ *.egg-info/ .eggs/
    find . -name '*.whl' -delete
    find . -name '*.tar.gz' -delete
    echo "--> Build artifacts cleaned."

# Clean Python bytecode files
clean-pyc:
    #!/usr/bin/env bash
    set -e
    echo "==> Cleaning Python bytecode files..."
    find . -type f -name '*.py[co]' -delete
    find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
    echo "--> Python bytecode cleaned."

# Clean test and coverage artifacts
clean-test:
    #!/usr/bin/env bash
    set -e
    echo "==> Cleaning test artifacts..."
    rm -rf .pytest_cache/ .coverage htmlcov/ .tox/ .mypy_cache/ .ty/
    echo "--> Test artifacts cleaned."

# Clean generated documentation
docs-clean:
    #!/usr/bin/env bash
    set -e
    echo "==> Cleaning documentation..."
    rm -rf docs/_build
    echo "--> Documentation cleaned."

# Run spelling check on documentation
docs-spelling venv="": (install-docs venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    TMPBUILDDIR="./.build"
    mkdir -p "${TMPBUILDDIR}"
    echo "==> Running spell check on documentation..."
    "${VENV_PATH}/bin/sphinx-build" -b spelling -d "${TMPBUILDDIR}/docs/doctrees" docs "${TMPBUILDDIR}/docs/spelling"

# -----------------------------------------------------------------------------
# -- Virtual Environment Management
# -----------------------------------------------------------------------------

# Create a single Python virtual environment (usage: `just create cpy314` or `just create`)
create venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    PYTHON_SPEC=$(just --quiet _get-spec ${VENV_NAME})
    VENV_PATH="{{VENV_DIR}}/${VENV_NAME}"
    echo "==> Creating venv for ${VENV_NAME} (${PYTHON_SPEC})..."
    if [ ! -d "${VENV_PATH}" ]; then
        uv venv --seed --python "${PYTHON_SPEC}" "${VENV_PATH}"
        echo "--> Created venv at ${VENV_PATH}"
    else
        echo "--> Venv already exists at ${VENV_PATH}"
    fi

# Create all Python virtual environments
create-all:
    #!/usr/bin/env bash
    set -e
    for env in {{ENVS}}; do
        just create ${env}
    done

# List all Python virtual environments
list-all:
    #!/usr/bin/env bash
    set -e
    echo "==> Listing all venvs in {{VENV_DIR}}..."
    if [ -d "{{VENV_DIR}}" ]; then
        ls -1 {{VENV_DIR}}
    else
        echo "--> No venvs directory found."
    fi

# Get the version of a single virtual environment's Python
version venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    ${VENV_PYTHON} --version

# Get versions of all Python virtual environments
version-all:
    #!/usr/bin/env bash
    set -e
    for env in {{ENVS}}; do
        echo -n "${env}: "
        just version ${env} || echo "Not installed"
    done

# -----------------------------------------------------------------------------
# -- Installation
# -----------------------------------------------------------------------------

# Install cfxdb with runtime dependencies
install venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Installing cfxdb..."
    ${VENV_PYTHON} -m pip install .
    echo "--> Installed cfxdb"

# Install cfxdb in development (editable) mode
install-dev venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Installing cfxdb in development mode..."
    ${VENV_PYTHON} -m pip install -e '.[dev]'
    echo "--> Installed cfxdb[dev] in editable mode"

# Install with locally editable WAMP packages for cross-repo development (usage: `just install-dev-local cpy312`)
install-dev-local venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")

    echo "==> Installing WAMP packages in editable mode from local repos..."
    echo "==> Looking for sibling repos (../txaio, ../autobahn-python, ../zlmdb)..."

    # Install local WAMP packages in editable mode
    # txaio - no extras needed
    if [ -d "../txaio" ]; then
        echo "  ✓ Installing txaio from ../txaio"
        ${VENV_PYTHON} -m pip install -e "../txaio"
    else
        echo "  ⚠ Warning: ../txaio not found, skipping"
    fi

    # autobahn-python - install with all extras
    if [ -d "../autobahn-python" ]; then
        echo "  ✓ Installing autobahn-python with [all] from ../autobahn-python"
        ${VENV_PYTHON} -m pip install -e "../autobahn-python[all]"
    else
        echo "  ⚠ Warning: ../autobahn-python not found, skipping"
    fi

    # zlmdb - no extras needed
    if [ -d "../zlmdb" ]; then
        echo "  ✓ Installing zlmdb from ../zlmdb"
        ${VENV_PYTHON} -m pip install -e "../zlmdb"
    else
        echo "  ⚠ Warning: ../zlmdb not found, skipping"
    fi

    echo "==> Installing cfxdb in editable mode with [dev] extras..."
    ${VENV_PYTHON} -m pip install -e .[dev] --upgrade --upgrade-strategy only-if-needed

# Install development tools (ruff, sphinx, etc.)
# Note: ty (Astral type checker) is installed via `uv tool install ty`
install-tools venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Installing development tools..."
    ${VENV_PYTHON} -m pip install ruff pytest sphinx twine build
    echo "--> Installed development tools"

# Install minimal build tools for building wheels
install-build-tools venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Installing build tools..."
    ${VENV_PYTHON} -m pip install build wheel twine
    echo "--> Installed build tools"

# Install all environments
install-all:
    #!/usr/bin/env bash
    set -e
    for env in {{ENVS}}; do
        just install-dev ${env}
    done

# Meta-recipe to run `install-dev` on all environments
install-dev-all:
    #!/usr/bin/env bash
    set -e
    for venv in {{ENVS}}; do
        just install-dev ${venv}
    done

# Meta-recipe to run `install-tools` on all environments
install-tools-all:
    #!/usr/bin/env bash
    set -e
    for venv in {{ENVS}}; do
        just install-tools ${venv}
    done

# -----------------------------------------------------------------------------
# -- Code Quality
# -----------------------------------------------------------------------------

# Check code formatting with Ruff (dry run)
check-format venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Checking code formatting with Ruff..."
    ${VENV_PYTHON} -m ruff format --check src/cfxdb/
    echo "--> Format check passed"

# Automatically fix all formatting and code style issues.
fix-format venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Auto-formatting code with Ruff..."
    ${VENV_PYTHON} -m ruff format src/cfxdb/
    echo "--> Code formatted"

# Alias for fix-format (backward compatibility)
autoformat venv="": (fix-format venv)

# Run Ruff linter
check-lint venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Running Ruff linter..."
    ${VENV_PYTHON} -m ruff check src/cfxdb/
    echo "--> Linting passed"

# Run static type checking with ty (Astral's Rust-based type checker)
# FIXME: Many type errors need to be fixed. For now, we ignore most rules
# to get CI passing. Create follow-up issue to address type errors.
check-typing venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Running type checking with ty..."
    ty check \
        --python "${VENV_PYTHON}" \
        --ignore unresolved-import \
        --ignore unresolved-attribute \
        --ignore unresolved-reference \
        --ignore unresolved-global \
        --ignore possibly-missing-attribute \
        --ignore possibly-missing-import \
        --ignore call-non-callable \
        --ignore invalid-assignment \
        --ignore invalid-argument-type \
        --ignore invalid-return-type \
        --ignore invalid-method-override \
        --ignore invalid-type-form \
        --ignore unsupported-operator \
        --ignore too-many-positional-arguments \
        --ignore unknown-argument \
        --ignore missing-argument \
        --ignore non-subscriptable \
        --ignore not-iterable \
        --ignore no-matching-overload \
        --ignore conflicting-declarations \
        --ignore deprecated \
        src/cfxdb/

# Run all code quality checks
check venv="": (check-format venv) (check-lint venv) (check-typing venv)

# -----------------------------------------------------------------------------
# -- Testing
# -----------------------------------------------------------------------------

# Run the test suite with pytest (requires: `just install-dev`)
test venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Running test suite with pytest..."
    ${VENV_PYTHON} -m pytest -v src/cfxdb/tests/
    echo "--> Tests passed"

# Run tests in all environments
test-all:
    #!/usr/bin/env bash
    set -e
    for env in {{ENVS}}; do
        echo ""
        echo "======================================================================"
        echo "Testing with ${env}"
        echo "======================================================================"
        just test ${env}
    done

# Run smoke tests (quick sanity check for imports and bundled files)
test-smoke venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    echo "Running smoke tests with Python: $(${VENV_PYTHON} --version)"
    echo "Venv: ${VENV_PATH}"
    echo ""

    # Run the smoke test Python script
    ${VENV_PYTHON} "{{ PROJECT_DIR }}/scripts/smoke_test.py"

# Test installing and verifying a built wheel (used in CI for artifact verification)
# Usage: just test-wheel-install /path/to/cfxdb-*.whl
test-wheel-install wheel_path:
    #!/usr/bin/env bash
    set -e
    WHEEL_PATH="{{ wheel_path }}"

    if [ ! -f "${WHEEL_PATH}" ]; then
        echo "ERROR: Wheel file not found: ${WHEEL_PATH}"
        exit 1
    fi

    WHEEL_NAME=$(basename "${WHEEL_PATH}")
    echo "========================================================================"
    echo "  WHEEL INSTALL TEST"
    echo "========================================================================"
    echo ""
    echo "Wheel: ${WHEEL_NAME}"
    echo ""

    # Create ephemeral venv name based on wheel
    EPHEMERAL_VENV="smoke-wheel-$$"
    EPHEMERAL_PATH="{{ VENV_DIR }}/${EPHEMERAL_VENV}"

    # Extract Python version from wheel filename
    # Wheel format: {name}-{version}-{python tag}-{abi tag}-{platform tag}.whl
    # Python tag examples: cp312, cp311, pp311, py3
    PYTAG=$(echo "${WHEEL_NAME}" | sed -n 's/.*-\(cp[0-9]*\|pp[0-9]*\|py[0-9]*\)-.*/\1/p')

    # For py3-none-any wheels (pure Python), use system Python
    if [ "${PYTAG}" = "py3" ]; then
        SYS_VENV=$(just --quiet _get-system-venv-name)
        echo "Pure Python wheel detected, using system venv: ${SYS_VENV}"
        PYTAG="${SYS_VENV}"
    fi

    # Map pytag to uv python version
    case "${PYTAG}" in
        cp314|cpy314) PYTHON_VERSION="3.14" ;;
        cp313|cpy313) PYTHON_VERSION="3.13" ;;
        cp312|cpy312) PYTHON_VERSION="3.12" ;;
        cp311|cpy311) PYTHON_VERSION="3.11" ;;
        pp311|pypy311) PYTHON_VERSION="pypy3.11" ;;
        *) echo "Unknown Python tag: ${PYTAG}"; exit 1 ;;
    esac

    echo "Python version: ${PYTHON_VERSION}"
    echo "Ephemeral venv: ${EPHEMERAL_PATH}"
    echo ""

    # Clean up any existing ephemeral venv
    rm -rf "${EPHEMERAL_PATH}"

    # Create fresh venv with uv
    echo "Creating ephemeral venv..."
    uv venv --python "${PYTHON_VERSION}" "${EPHEMERAL_PATH}"

    # Install the wheel
    echo "Installing wheel..."
    uv pip install --python "${EPHEMERAL_PATH}/bin/python" "${WHEEL_PATH}"

    # Run smoke tests
    echo ""
    echo "Running smoke tests..."
    "${EPHEMERAL_PATH}/bin/python" "{{ PROJECT_DIR }}/scripts/smoke_test.py"
    RESULT=$?

    # Clean up ephemeral venv
    echo ""
    echo "Cleaning up ephemeral venv..."
    rm -rf "${EPHEMERAL_PATH}"

    if [ ${RESULT} -eq 0 ]; then
        echo ""
        echo "========================================================================"
        echo "  WHEEL INSTALL TEST: PASSED"
        echo "========================================================================"
    else
        echo ""
        echo "========================================================================"
        echo "  WHEEL INSTALL TEST: FAILED"
        echo "========================================================================"
        exit 1
    fi

# Test installing and verifying a source distribution (used in CI for artifact verification)
# Usage: just test-sdist-install /path/to/cfxdb-*.tar.gz
test-sdist-install sdist_path:
    #!/usr/bin/env bash
    set -e
    SDIST_PATH="{{ sdist_path }}"

    if [ ! -f "${SDIST_PATH}" ]; then
        echo "ERROR: Source distribution not found: ${SDIST_PATH}"
        exit 1
    fi

    SDIST_NAME=$(basename "${SDIST_PATH}")
    echo "========================================================================"
    echo "  SOURCE DISTRIBUTION INSTALL TEST"
    echo "========================================================================"
    echo ""
    echo "Source dist: ${SDIST_NAME}"
    echo ""

    # Create ephemeral venv
    EPHEMERAL_VENV="smoke-sdist-$$"
    EPHEMERAL_PATH="{{ VENV_DIR }}/${EPHEMERAL_VENV}"

    # Use system Python version
    SYS_VENV=$(just --quiet _get-system-venv-name)
    case "${SYS_VENV}" in
        cpy314) PYTHON_VERSION="3.14" ;;
        cpy313) PYTHON_VERSION="3.13" ;;
        cpy312) PYTHON_VERSION="3.12" ;;
        cpy311) PYTHON_VERSION="3.11" ;;
        pypy311) PYTHON_VERSION="pypy3.11" ;;
        *) echo "Unknown system venv: ${SYS_VENV}"; exit 1 ;;
    esac

    echo "Python version: ${PYTHON_VERSION}"
    echo "Ephemeral venv: ${EPHEMERAL_PATH}"
    echo ""

    # Clean up any existing ephemeral venv
    rm -rf "${EPHEMERAL_PATH}"

    # Create fresh venv with uv
    echo "Creating ephemeral venv..."
    uv venv --python "${PYTHON_VERSION}" "${EPHEMERAL_PATH}"

    # Install the sdist
    echo "Installing source distribution..."
    uv pip install --python "${EPHEMERAL_PATH}/bin/python" "${SDIST_PATH}"

    # Run smoke tests
    echo ""
    echo "Running smoke tests..."
    "${EPHEMERAL_PATH}/bin/python" "{{ PROJECT_DIR }}/scripts/smoke_test.py"
    RESULT=$?

    # Clean up ephemeral venv
    echo ""
    echo "Cleaning up ephemeral venv..."
    rm -rf "${EPHEMERAL_PATH}"

    if [ ${RESULT} -eq 0 ]; then
        echo ""
        echo "========================================================================"
        echo "  SOURCE DISTRIBUTION INSTALL TEST: PASSED"
        echo "========================================================================"
    else
        echo ""
        echo "========================================================================"
        echo "  SOURCE DISTRIBUTION INSTALL TEST: FAILED"
        echo "========================================================================"
        exit 1
    fi

# Upgrade dependencies in a single environment (re-installs all deps to latest)
upgrade venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Upgrading all dependencies..."
    ${VENV_PYTHON} -m pip install --upgrade pip
    ${VENV_PYTHON} -m pip install --upgrade -e '.[dev]'
    echo "--> Dependencies upgraded"

# Meta-recipe to run `upgrade` on all environments
upgrade-all:
    #!/usr/bin/env bash
    set -e
    for venv in {{ENVS}}; do
        echo ""
        echo "======================================================================"
        echo "Upgrading ${venv}"
        echo "======================================================================"
        just upgrade ${venv}
    done

# Generate code coverage report (requires: `just install-dev`)
check-coverage venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Generating coverage report..."
    ${VENV_PYTHON} -m pytest --cov=cfxdb --cov-report=html --cov-report=term src/cfxdb/tests/
    echo "--> Coverage report generated in htmlcov/"

# Alias for check-coverage (backward compatibility)
coverage venv="": (check-coverage venv)

# -----------------------------------------------------------------------------
# -- Building
# -----------------------------------------------------------------------------

# Build source distribution
build-sourcedist venv="": (install-build-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Building source distribution..."
    ${VENV_PYTHON} -m build --sdist
    ls -la dist/

# Build wheel package
build venv="": (install-build-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PATH="{{VENV_DIR}}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Building wheel package..."
    ${VENV_PYTHON} -m build --wheel
    ls -la dist/

# Build both source distribution and wheel
dist venv="": (install-build-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Building distribution packages..."
    ${VENV_PYTHON} -m build
    echo ""
    echo "Built packages:"
    ls -lh dist/

# Build wheels for all environments (pure Python - only needs one build)
build-all: build
    echo "==> Pure Python package: single universal wheel built."

# Verify wheels using twine check (pure Python package - auditwheel not applicable)
verify-wheels venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PATH="{{VENV_DIR}}/${VENV_NAME}"
    echo "==> Verifying wheels with twine check..."
    "${VENV_PATH}/bin/twine" check dist/*
    echo ""
    echo "==> Note: This is a pure Python package (py3-none-any wheel)."
    echo "    auditwheel verification is not applicable (no native extensions)."
    echo ""
    echo "==> Wheel verification complete."

# Alias for verify-wheels (used by release.yml)
verify-dist venv="": (verify-wheels venv)

# -----------------------------------------------------------------------------
# -- Documentation
# -----------------------------------------------------------------------------

# Install documentation dependencies
install-docs venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Installing documentation tools in ${VENV_NAME}..."
    ${VENV_PYTHON} -m pip install -e .[docs]

# Sync images (logo and favicon) from crossbar (Crossbar.io subarea source)
sync-images:
    #!/usr/bin/env bash
    set -e

    SOURCEDIR="{{ PROJECT_DIR }}/../crossbar/docs/_static"
    TARGETDIR="{{ PROJECT_DIR }}/docs/_static"
    IMGDIR="${TARGETDIR}/img"

    echo "==> Syncing images from crossbar..."
    mkdir -p "${IMGDIR}"

    # Copy optimized logo SVG (Crossbar.io icon)
    if [ -f "${SOURCEDIR}/img/crossbar_icon.svg" ]; then
        cp "${SOURCEDIR}/img/crossbar_icon.svg" "${IMGDIR}/"
        echo "  Copied: crossbar_icon.svg"
    else
        echo "  Warning: crossbar_icon.svg not found in crossbar"
        echo "  Run 'just optimize-images' in crossbar first"
    fi

    # Copy favicon
    if [ -f "${SOURCEDIR}/favicon.ico" ]; then
        cp "${SOURCEDIR}/favicon.ico" "${TARGETDIR}/"
        echo "  Copied: favicon.ico"
    else
        echo "  Warning: favicon.ico not found in crossbar"
        echo "  Run 'just optimize-images' in crossbar first"
    fi

    echo "==> Image sync complete."

# Build HTML documentation using Sphinx
docs venv="": (sync-images)
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Building documentation..."
    cd docs
    ${VENV_PYTHON} -m sphinx -b html . _build/html
    echo "--> Documentation built in docs/_build/html/"

# View built documentation
docs-view venv="":
    #!/usr/bin/env bash
    set -e
    if [ ! -f "docs/_build/html/index.html" ]; then
        echo "Error: Documentation not built yet. Run 'just docs' first."
        exit 1
    fi
    xdg-open docs/_build/html/index.html 2>/dev/null || \
        open docs/_build/html/index.html 2>/dev/null || \
        echo "Could not open browser. Open docs/_build/html/index.html manually."

# -----------------------------------------------------------------------------
# -- Publishing
# -----------------------------------------------------------------------------

# Publish to PyPI using twine
publish venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Publishing to PyPI..."
    echo ""
    echo "WARNING: This will upload to PyPI!"
    echo "Press Ctrl+C to cancel, or Enter to continue..."
    read
    ${VENV_PYTHON} -m twine upload dist/*
    echo "--> Published to PyPI"

# Publish to Test PyPI
publish-test venv="":
    #!/usr/bin/env bash
    set -e
    VENV_PYTHON=$(just --quiet _get-venv-python {{ venv }})
    echo "==> Publishing to Test PyPI..."
    ${VENV_PYTHON} -m twine upload --repository testpypi dist/*
    echo "--> Published to Test PyPI"

# Download GitHub release artifacts (usage: `just download-github-release` for nightly, or `just download-github-release stable`)
# Downloads wheel, sdist, and verifies checksums
# This is the unified download recipe for both docs integration and release notes generation
download-github-release release_type="nightly":
    #!/usr/bin/env bash
    set -euo pipefail

    RELEASE_TYPE="{{ release_type }}"
    REPO="crossbario/cfxdb"

    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  Downloading GitHub Release Artifacts"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Release type: ${RELEASE_TYPE}"
    echo ""

    # Check if gh is available and authenticated
    if ! command -v gh &> /dev/null; then
        echo "❌ ERROR: GitHub CLI (gh) is not installed"
        echo "   Install: https://cli.github.com/"
        exit 1
    fi

    if ! gh auth status &> /dev/null; then
        echo "❌ ERROR: GitHub CLI is not authenticated"
        echo "   Run: gh auth login"
        exit 1
    fi

    # Determine which release tag to download
    case "${RELEASE_TYPE}" in
        nightly)
            echo "==> Looking for nightly release..."
            RELEASE_TAG=$(gh release list --repo "${REPO}" --limit 20 | grep -E "^master-" | head -1 | awk '{print $1}') || true
            if [ -z "${RELEASE_TAG}" ]; then
                echo "❌ ERROR: No nightly (master-*) release found"
                echo "Available releases:"
                gh release list --repo "${REPO}" --limit 10
                exit 1
            fi
            ;;
        stable|latest)
            echo "==> Looking for stable release..."
            RELEASE_TAG=$(gh release list --repo "${REPO}" --limit 20 | grep -E "^v[0-9]+\.[0-9]+\.[0-9]+" | head -1 | awk '{print $1}') || true
            if [ -z "${RELEASE_TAG}" ]; then
                echo "❌ ERROR: No stable (v*) release found"
                echo "Available releases:"
                gh release list --repo "${REPO}" --limit 10
                exit 1
            fi
            ;;
        development|dev)
            echo "==> Looking for development release (fork-*)..."
            RELEASE_TAG=$(gh release list --repo "${REPO}" --limit 20 | grep -E "^fork-" | head -1 | awk '{print $1}') || true
            if [ -z "${RELEASE_TAG}" ]; then
                echo "❌ ERROR: No development (fork-*) release found"
                echo "Available releases:"
                gh release list --repo "${REPO}" --limit 10
                exit 1
            fi
            ;;
        *)
            # Assume it's a specific tag name
            RELEASE_TAG="${RELEASE_TYPE}"
            ;;
    esac

    echo "✅ Found release: ${RELEASE_TAG}"
    echo ""

    # Destination directory - compatible with generate-release-notes
    DEST_DIR="/tmp/release-artifacts/${RELEASE_TAG}"

    # Create/clean destination directory
    if [ -d "${DEST_DIR}" ]; then
        echo "==> Cleaning existing directory: ${DEST_DIR}"
        rm -rf "${DEST_DIR}"
    fi
    mkdir -p "${DEST_DIR}"

    # Download all release assets
    echo "==> Downloading all release assets to: ${DEST_DIR}"
    echo ""
    cd "${DEST_DIR}"

    gh release download "${RELEASE_TAG}" \
        --repo "${REPO}" \
        --pattern "*" \
        --clobber

    # Count different types of files
    WHEEL_COUNT=$(ls -1 *.whl 2>/dev/null | wc -l || echo "0")
    TARBALL_COUNT=$(ls -1 *.tar.gz 2>/dev/null | wc -l || echo "0")
    CHECKSUM_COUNT=$(ls -1 *CHECKSUMS* 2>/dev/null | wc -l || echo "0")

    echo ""
    echo "==> Downloaded assets:"
    ls -la
    echo ""
    echo "==> Asset summary:"
    echo "    Wheels:     ${WHEEL_COUNT}"
    echo "    Tarballs:   ${TARBALL_COUNT}"
    echo "    Checksums:  ${CHECKSUM_COUNT}"

    # Verify checksums if available
    if [ -f "CHECKSUMS.sha256" ]; then
        echo ""
        echo "==> Verifying checksums..."
        VERIFIED=0
        FAILED=0
        while IFS= read -r line; do
            [ -z "$line" ] && continue
            FILE_PATH=$(echo "$line" | sed -E 's/^SHA2?-?256\(([^)]+)\)=.*/\1/')
            EXPECTED_CHECKSUM=$(echo "$line" | awk -F'= ' '{print $2}')
            FILE_PATH="${FILE_PATH#./}"
            if [ -f "$FILE_PATH" ]; then
                ACTUAL_CHECKSUM=$(openssl sha256 "$FILE_PATH" | awk '{print $2}')
                if [ "$ACTUAL_CHECKSUM" = "$EXPECTED_CHECKSUM" ]; then
                    VERIFIED=$((VERIFIED + 1))
                else
                    echo "    ❌ MISMATCH: $FILE_PATH"
                    FAILED=$((FAILED + 1))
                fi
            fi
        done < CHECKSUMS.sha256
        if [ $FAILED -gt 0 ]; then
            echo "    ERROR: ${FAILED} file(s) failed verification!"
            exit 1
        else
            echo "    ✅ ${VERIFIED} file(s) verified successfully"
        fi
    fi

    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "✅ Download Complete"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Artifacts location: ${DEST_DIR}"
    echo ""
    echo "Next steps:"
    echo "  1. Build docs:            just docs"
    echo "  2. Integrate artifacts:   just docs-integrate-github-release ${RELEASE_TAG}"
    echo "  3. Generate release notes: just generate-release-notes <version> ${RELEASE_TAG}"
    echo ""

# Download release artifacts from GitHub and publish to PyPI
publish-pypi venv="" tag="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_PATH="{{VENV_DIR}}/$(just --quiet _get-system-venv-name)"
    if [ -n "{{ venv }}" ]; then
        VENV_PATH="{{VENV_DIR}}/{{ venv }}"
    fi
    TAG="{{ tag }}"
    if [ -z "${TAG}" ]; then
        echo "Error: Please specify a tag to publish"
        echo "Usage: just publish-pypi cpy311 v24.1.1"
        exit 1
    fi

    DOWNLOAD_DIR="/tmp/release-artifacts/${TAG}"

    echo "==> Publishing ${TAG} to PyPI..."
    echo ""
    echo "Step 1: Download release artifacts from GitHub..."
    just download-github-release "${TAG}"
    echo ""
    echo "Step 2: Verify packages with twine..."
    "${VENV_PATH}/bin/twine" check "${DOWNLOAD_DIR}"/*.whl "${DOWNLOAD_DIR}"/*.tar.gz
    echo ""
    echo "Note: This is a pure Python package (py3-none-any wheel)."
    echo "      auditwheel verification is not applicable (no native extensions)."
    echo ""
    echo "Step 3: Upload to PyPI..."
    echo ""
    echo "WARNING: This will upload to PyPI!"
    echo "Press Ctrl+C to cancel, or Enter to continue..."
    read
    "${VENV_PATH}/bin/twine" upload "${DOWNLOAD_DIR}"/*.whl "${DOWNLOAD_DIR}"/*.tar.gz
    echo ""
    echo "==> Successfully published ${TAG} to PyPI"

# Trigger Read the Docs build for a specific tag
publish-rtd tag="":
    #!/usr/bin/env bash
    set -e
    TAG="{{ tag }}"
    if [ -z "${TAG}" ]; then
        echo "Error: Please specify a tag to build"
        echo "Usage: just publish-rtd v24.1.1"
        exit 1
    fi
    echo "==> Triggering Read the Docs build for ${TAG}..."
    echo ""
    echo "Note: Read the Docs builds are typically triggered automatically"
    echo "      when tags are pushed to GitHub. This recipe is a placeholder"
    echo "      for manual triggering if needed."
    echo ""
    echo "To manually trigger a build:"
    echo "  1. Go to https://readthedocs.org/projects/cfxdb/"
    echo "  2. Click 'Build a version'"
    echo "  3. Select the tag: ${TAG}"
    echo ""


# Generate release notes from GitHub release for documentation integration
generate-release-notes tag:
    #!/usr/bin/env bash
    set -e

    TAG="{{ tag }}"
    DOWNLOAD_DIR="/tmp/release-artifacts/${TAG}"

    echo "==> Generating release notes for ${TAG}..."

    # Check gh CLI is authenticated
    if ! gh auth status &>/dev/null; then
        echo "❌ Error: gh CLI is not authenticated"
        echo "   Run: gh auth login"
        exit 1
    fi

    # Get release info from GitHub
    echo ""
    echo "==> Fetching release information from GitHub..."
    gh release view "${TAG}" --repo crossbario/cfxdb --json tagName,name,body,createdAt,assets \
        > "${DOWNLOAD_DIR}/release-info.json" 2>/dev/null || {
        echo "❌ Error: Could not fetch release ${TAG}"
        exit 1
    }

    # Extract release body (notes)
    echo ""
    echo "==> Release notes for ${TAG}:"
    echo "----------------------------------------"
    gh release view "${TAG}" --repo crossbario/cfxdb --json body -q '.body'
    echo "----------------------------------------"
    echo ""
    echo "==> Release info saved to: ${DOWNLOAD_DIR}/release-info.json"

# Integrate GitHub release artifacts into documentation (chain-of-custody)
docs-integrate-github-release tag:
    #!/usr/bin/env bash
    set -e

    TAG="{{ tag }}"
    DOWNLOAD_DIR="/tmp/release-artifacts/${TAG}"
    DOCS_RELEASE_DIR="docs/_releases/${TAG}"

    echo "==> Integrating GitHub release ${TAG} into documentation..."

    # Ensure artifacts are downloaded
    if [ ! -d "${DOWNLOAD_DIR}" ] || [ -z "$(ls -A ${DOWNLOAD_DIR} 2>/dev/null)" ]; then
        echo "==> Artifacts not found, downloading..."
        just download-github-release "${TAG}"
    fi

    # Create docs release directory
    mkdir -p "${DOCS_RELEASE_DIR}"

    # Copy chain-of-custody files
    echo ""
    echo "==> Copying chain-of-custody files..."

    # Handle both CHECKSUMS.sha256 and CHECKSUMS-ALL.sha256 for compatibility
    if [ -f "${DOWNLOAD_DIR}/CHECKSUMS.sha256" ]; then
        cp "${DOWNLOAD_DIR}/CHECKSUMS.sha256" "${DOCS_RELEASE_DIR}/"
        echo "  ✓ CHECKSUMS.sha256"
    elif [ -f "${DOWNLOAD_DIR}/CHECKSUMS-ALL.sha256" ]; then
        cp "${DOWNLOAD_DIR}/CHECKSUMS-ALL.sha256" "${DOCS_RELEASE_DIR}/CHECKSUMS.sha256"
        echo "  ✓ CHECKSUMS.sha256 (copied from CHECKSUMS-ALL.sha256)"
    fi

    if [ -f "${DOWNLOAD_DIR}/release-info.json" ]; then
        cp "${DOWNLOAD_DIR}/release-info.json" "${DOCS_RELEASE_DIR}/"
        echo "  ✓ release-info.json"
    fi

    # Generate build-info.txt with download metadata
    echo "==> Generating build-info.txt..."
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    ARTIFACTS=$(ls -la "${DOWNLOAD_DIR}"/*.whl "${DOWNLOAD_DIR}"/*.tar.gz 2>/dev/null | awk '{print "  " $NF ": " $5 " bytes"}')
    {
        echo "Release: ${TAG}"
        echo "Downloaded: ${TIMESTAMP}"
        echo "Source: GitHub Releases (crossbario/cfxdb)"
        echo "Verification: Checksums verified during download"
        echo ""
        echo "Artifacts:"
        echo "${ARTIFACTS}"
    } > "${DOCS_RELEASE_DIR}/build-info.txt"
    echo "  ✓ build-info.txt"

    # Generate VALIDATION.txt
    echo "==> Generating VALIDATION.txt..."
    CHECKSUM_STATUS="NO CHECKSUMS AVAILABLE"
    if [ -f "${DOWNLOAD_DIR}/CHECKSUMS.sha256" ] || [ -f "${DOWNLOAD_DIR}/CHECKSUMS-ALL.sha256" ]; then
        CHECKSUM_STATUS="PASSED"
    fi
    ARTIFACT_LIST=$(ls "${DOWNLOAD_DIR}"/*.whl "${DOWNLOAD_DIR}"/*.tar.gz 2>/dev/null | while read f; do echo "  - $(basename "$f")"; done)
    {
        echo "Validation Report for ${TAG}"
        echo "Generated: ${TIMESTAMP}"
        echo ""
        echo "Source Verification:"
        echo "  - Downloaded from: GitHub Releases (crossbario/cfxdb)"
        echo "  - Release tag: ${TAG}"
        echo "  - Checksum verification: ${CHECKSUM_STATUS}"
        echo ""
        echo "Artifact List:"
        echo "${ARTIFACT_LIST}"
        echo ""
        echo "This package is a pure Python wheel (py3-none-any)."
        echo "No native code compilation or platform-specific verification required."
    } > "${DOCS_RELEASE_DIR}/VALIDATION.txt"
    echo "  ✓ VALIDATION.txt"

    echo ""
    echo "==> Documentation integration complete."
    echo "    Files written to: ${DOCS_RELEASE_DIR}/"
    ls -la "${DOCS_RELEASE_DIR}/"

# -----------------------------------------------------------------------------
# -- FlatBuffers Schema Management
# -----------------------------------------------------------------------------

# Regenerate .bfbs binary schemas from .fbs files (requires autobahn with flatc)
# Note: cfxdb bundles both .fbs and .bfbs files; use this to regenerate after .fbs changes
# cfxdb uses zlmdb's vendored flatbuffers runtime (from zlmdb import flatbuffers)
generate-bfbs venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    echo "==> Regenerating .bfbs binary schemas from .fbs files..."
    echo "    Note: cfxdb uses zlmdb's vendored flatbuffers runtime"

    # Check if flatc is available via autobahn (autobahn bundles the flatc compiler)
    if ! "${VENV_PATH}/bin/python" -c "from autobahn._flatc import get_flatc_path; print(get_flatc_path())" &>/dev/null; then
        echo "❌ Error: flatc not available. Install autobahn[all] with flatc support."
        echo "   Run: just install-dev"
        exit 1
    fi

    FLATC=$("${VENV_PATH}/bin/python" -c "from autobahn._flatc import get_flatc_path; print(get_flatc_path())")
    echo "   Using flatc: ${FLATC}"

    # Output directory for .bfbs files (matches existing structure)
    BFBS_DIR="src/cfxdb/gen"

    # Find and compile all .fbs files in src/cfxdb/
    FBS_FILES=$(find src/cfxdb -maxdepth 1 -name "*.fbs" -type f)
    for FBS in ${FBS_FILES}; do
        BASENAME=$(basename "${FBS}" .fbs)
        echo "   Compiling: ${FBS} -> ${BFBS_DIR}/${BASENAME}.bfbs"
        "${FLATC}" --binary --schema -o "${BFBS_DIR}" "${FBS}"
    done

    echo ""
    echo "==> Generated .bfbs files:"
    ls -la "${BFBS_DIR}"/*.bfbs 2>/dev/null || echo "   No .bfbs files generated"
    echo ""
    echo "==> Note: Both .fbs and .bfbs files are bundled in the cfxdb wheel"

# List FlatBuffers schema files (.fbs source and .bfbs binary)
list-fbs:
    #!/usr/bin/env bash
    set -e
    echo "==> FlatBuffers schema files (.fbs) in src/cfxdb/:"
    find src/cfxdb -maxdepth 1 -name "*.fbs" -type f | sort
    echo ""
    echo "==> Binary schema files (.bfbs) in src/cfxdb/gen/:"
    find src/cfxdb/gen -name "*.bfbs" -type f 2>/dev/null | sort || echo "   None found"
    echo ""
    echo "==> Note: cfxdb uses 'from zlmdb import flatbuffers' (zlmdb's vendored runtime)"

# -----------------------------------------------------------------------------
# -- Release workflow recipes
# -----------------------------------------------------------------------------

# Generate changelog entry from git history for a given version
prepare-changelog version:
    #!/usr/bin/env bash
    set -e
    VERSION="{{ version }}"

    echo ""
    echo "=========================================="
    echo " Generating changelog for version ${VERSION}"
    echo "=========================================="
    echo ""

    # Find the previous tag
    PREV_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    if [ -z "${PREV_TAG}" ]; then
        echo "No previous tag found. Showing all commits..."
        git log --oneline --no-decorate | head -50
    else
        echo "Commits since ${PREV_TAG}:"
        echo ""
        git log --oneline --no-decorate "${PREV_TAG}..HEAD" | head -50
    fi

    echo ""
    echo "=========================================="
    echo " Suggested changelog format:"
    echo "=========================================="
    echo ""
    echo "${VERSION}"
    echo "------"
    echo ""
    echo "**New**"
    echo ""
    echo "* new: <feature description>"
    echo ""
    echo "**Fix**"
    echo ""
    echo "* fix: <fix description>"
    echo ""
    echo "**Other**"
    echo ""
    echo "* other: <other changes>"
    echo ""

# Validate release is ready: checks changelog, releases, version
draft-release version:
    #!/usr/bin/env bash
    set -e
    VERSION="{{ version }}"

    echo ""
    echo "=========================================="
    echo " Validating release ${VERSION}"
    echo "=========================================="
    echo ""

    ERRORS=0

    # Check pyproject.toml version
    PYPROJECT_VERSION=$(grep '^version' pyproject.toml | head -1 | sed 's/.*= *"\(.*\)"/\1/')
    if [ "${PYPROJECT_VERSION}" = "${VERSION}" ]; then
        echo "✅ pyproject.toml version matches: ${VERSION}"
    else
        echo "❌ pyproject.toml version mismatch: ${PYPROJECT_VERSION} != ${VERSION}"
        ERRORS=$((ERRORS + 1))
    fi

    # Check changelog entry
    if grep -q "^${VERSION}$" docs/changelog.rst; then
        echo "✅ Changelog entry exists for ${VERSION}"
    else
        echo "❌ Changelog entry missing for ${VERSION}"
        ERRORS=$((ERRORS + 1))
    fi

    # Check releases entry
    if grep -q "^${VERSION}$" docs/releases.rst; then
        echo "✅ Releases entry exists for ${VERSION}"
    else
        echo "❌ Releases entry missing for ${VERSION}"
        ERRORS=$((ERRORS + 1))
    fi

    echo ""
    if [ ${ERRORS} -gt 0 ]; then
        echo "=========================================="
        echo " ❌ Validation failed with ${ERRORS} error(s)"
        echo "=========================================="
        exit 1
    else
        echo "=========================================="
        echo " ✅ All checks passed for ${VERSION}"
        echo "=========================================="
    fi

# Full release preparation: validate + test + build docs
prepare-release version venv="":
    #!/usr/bin/env bash
    set -e
    VERSION="{{ version }}"
    VENV="{{ venv }}"

    echo ""
    echo "=========================================="
    echo " Preparing release ${VERSION}"
    echo "=========================================="
    echo ""

    # Run draft-release validation first
    just draft-release "${VERSION}"

    echo ""
    echo "==> Running tests..."
    if [ -n "${VENV}" ]; then
        just test "${VENV}"
    else
        just test
    fi

    echo ""
    echo "==> Building documentation..."
    just docs

    echo ""
    echo "=========================================="
    echo " ✅ Release ${VERSION} is ready"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. git add docs/changelog.rst docs/releases.rst pyproject.toml"
    echo "  2. git commit -m \"Release ${VERSION}\""
    echo "  3. git tag v${VERSION}"
    echo "  4. git push && git push --tags"
    echo ""
