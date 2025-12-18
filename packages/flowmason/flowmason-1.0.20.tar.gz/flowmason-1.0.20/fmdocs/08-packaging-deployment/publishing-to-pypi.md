# Publishing FlowMason to PyPI

This guide covers how to publish FlowMason as a **closed-source/proprietary** package to the Python Package Index (PyPI).

## Overview

### Distribution Model

FlowMason is distributed as a **proprietary package** on PyPI:
- **Wheel only** - No source distribution (keeps code private)
- **Proprietary license** - Not open source
- **No public repository required** - Website URLs instead of GitHub

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOSED-SOURCE PyPI                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Build                    Publish                   Install    │
│   ┌─────────────┐         ┌─────────────┐         ┌──────────┐ │
│   │ python -m   │         │   twine     │         │   pip    │ │
│   │ build       │────────►│   upload    │────────►│ install  │ │
│   │ --wheel     │         │   dist/*    │         │flowmason │ │
│   └─────────────┘         └─────────────┘         └──────────┘ │
│        │                                                        │
│        ▼                                                        │
│   .whl only (no .tar.gz)                                       │
│   = Compiled code, no source                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Package Structure

```
flowmason/
├── pyproject.toml           # Single package: "flowmason"
├── core/flowmason_core/     # Core framework
├── studio/flowmason_studio/ # Backend server
└── lab/flowmason_lab/       # Built-in components
```

### Publishing Options

| Option | Package Name | Install Command |
|--------|--------------|-----------------|
| **Single Package** | `flowmason` | `pip install flowmason` |
| **Split Packages** | `flowmason-core`, `flowmason-studio`, `flowmason-lab` | `pip install flowmason-core` |

This guide covers the **single package** approach. See [Splitting Packages](#splitting-into-multiple-packages) for the alternative.

---

## Prerequisites

### 1. Create PyPI Account

1. Go to [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. Create an account and verify your email
3. Enable 2FA (required for publishing)

### 2. Create TestPyPI Account (Recommended)

1. Go to [https://test.pypi.org/account/register/](https://test.pypi.org/account/register/)
2. Create a separate account (TestPyPI is independent)
3. Use TestPyPI to test publishing before going to production

### 3. Generate API Tokens

**For PyPI:**
1. Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Click "Add API token"
3. Name: `flowmason-publish`
4. Scope: "Entire account" (first time) or project-specific (after first publish)
5. Copy and save the token (starts with `pypi-`)

**For TestPyPI:**
1. Go to [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
2. Same process, token starts with `pypi-`

### 4. Install Build Tools

```bash
pip install build twine
```

---

## Step-by-Step Publishing

### Step 1: Configure pyproject.toml for Closed-Source

Update `pyproject.toml` for proprietary distribution:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "flowmason"
version = "0.4.0"  # Update version before each release
description = "Universal AI Workflow Infrastructure"
readme = "README.md"
requires-python = ">=3.11"
license = "Proprietary"  # NOT open source
keywords = ["ai", "workflow", "llm", "pipeline", "automation"]
authors = [
    { name = "FlowMason", email = "support@flowmason.com" }
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",  # Proprietary classifier
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
dependencies = [
    "pydantic>=2.0.0",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "python-multipart>=0.0.6",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "httpx>=0.26.0",
]

# Website URLs instead of GitHub (no public repo needed)
[project.urls]
Homepage = "https://flowmason.com"
Documentation = "https://flowmason.com/docs"
Support = "https://flowmason.com/support"

[project.scripts]
flowmason = "flowmason_core.cli.main:cli"
fm = "flowmason_core.cli.main:cli"

[tool.hatch.build.targets.wheel]
packages = ["core/flowmason_core", "studio/flowmason_studio", "lab/flowmason_lab"]
```

**Key differences for closed-source:**
- `license = "Proprietary"` - Indicates not open source
- `License :: Other/Proprietary License` - PyPI classifier
- URLs point to website, not GitHub
- No `Repository` or `Issues` URLs needed

### Step 2: Update Version

Before each release, update the version in `pyproject.toml`:

```toml
version = "0.4.0"  # Use semantic versioning
```

**Semantic Versioning:**
- `MAJOR.MINOR.PATCH`
- `0.4.0` → `0.4.1` (bug fix)
- `0.4.0` → `0.5.0` (new feature)
- `0.4.0` → `1.0.0` (breaking change / production ready)

### Step 3: Create README.md

Create `README.md` at repository root (becomes the PyPI project page):

```markdown
# FlowMason

Universal AI Workflow Infrastructure for building, debugging, and deploying intelligent pipelines.

## Installation

```bash
pip install flowmason
```

## Quick Start

```bash
# Initialize a project
fm init

# Start the Studio backend
fm studio start

# Run a pipeline
fm run pipelines/main.pipeline.json
```

## Documentation

Visit [https://flowmason.com/docs](https://flowmason.com/docs)

## Support

- Documentation: https://flowmason.com/docs
- Support: https://flowmason.com/support
- Email: support@flowmason.com

## License

Proprietary software. See LICENSE file for terms.
```

### Step 4: Create LICENSE File

Create a `LICENSE` file for proprietary distribution:

```
FlowMason Proprietary License

Copyright (c) 2025 FlowMason

All rights reserved.

This software and associated documentation files (the "Software") are proprietary
and confidential. Unauthorized copying, modification, distribution, or use of
this Software, via any medium, is strictly prohibited.

The Software is licensed, not sold. You may use this Software only in accordance
with the terms of your license agreement.

The Software is provided "as is", without warranty of any kind, express or implied,
including but not limited to the warranties of merchantability, fitness for a
particular purpose and noninfringement.

For licensing inquiries, contact: licensing@flowmason.com
```

### Step 5: Build the Package (Wheel Only)

**Important:** Build **wheel only** (no source distribution) to keep code private.

```bash
cd /path/to/flowmason

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build WHEEL ONLY (not source distribution)
python -m build --wheel
```

This creates:
```
dist/
└── flowmason-1.0.0-py3-none-any.whl  # Wheel only (no .tar.gz)
```

**Note:** The `.tar.gz` source distribution would expose your source code. By building `--wheel` only, users get compiled bytecode.

### Step 6: Verify the Build

```bash
# Check the package contents
twine check dist/*

# List files in the wheel (verify no source exposed)
unzip -l dist/flowmason-1.0.0-py3-none-any.whl
```

### Step 7: Test with TestPyPI (Recommended)

**Upload to TestPyPI:**
```bash
twine upload --repository testpypi dist/*
```

You'll be prompted for credentials:
- Username: `__token__`
- Password: Your TestPyPI API token (including `pypi-` prefix)

**Test Installation:**
```bash
# Create a fresh virtual environment
python -m venv test-env
source test-env/bin/activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    flowmason

# Verify it works
fm --version
```

### Step 8: Publish to PyPI

Once testing passes:

```bash
twine upload dist/*
```

Credentials:
- Username: `__token__`
- Password: Your PyPI API token

### Step 9: Verify on PyPI

1. Go to [https://pypi.org/project/flowmason/](https://pypi.org/project/flowmason/)
2. Verify the description, version, and metadata
3. Test installation:

```bash
pip install flowmason
fm --version
```

---

## Automating with GitHub Actions (Private Repo)

For a **private repository**, create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: pip install build twine

      - name: Build wheel only (no source distribution)
        run: python -m build --wheel

      - name: Check package
        run: twine check dist/*

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

**Key:** Uses `--wheel` to avoid exposing source code.

**Setup:**
1. Go to repository Settings → Secrets → Actions
2. Add secret `PYPI_API_TOKEN` with your PyPI token

**Usage:**
1. Create a GitHub Release
2. The workflow automatically publishes to PyPI

---

## Using Trusted Publishing (Alternative)

PyPI supports "Trusted Publishing" which eliminates the need for API tokens. However, this requires linking your GitHub repository to PyPI, which may not be ideal for private repos.

### Setup on PyPI

1. Go to [https://pypi.org/manage/account/publishing/](https://pypi.org/manage/account/publishing/)
2. Add a new publisher:
   - Owner: `your-github-username`
   - Repository: `flowmason` (can be private)
   - Workflow: `publish.yml`
   - Environment: `release` (optional)

### Updated GitHub Action

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for trusted publishing
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: pip install build

      - name: Build wheel only
        run: python -m build --wheel

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

No API token secrets needed - PyPI trusts the GitHub Actions identity.

**Note:** Even with trusted publishing from a private repo, only the wheel (compiled code) is published, not your source.

---

## Splitting into Multiple Packages

If you want separate packages (`flowmason-core`, `flowmason-studio`, `flowmason-lab`):

### 1. Create Individual pyproject.toml Files

**core/pyproject.toml:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "flowmason-core"
version = "0.4.0"
description = "FlowMason Core Framework"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "httpx>=0.26.0",
]

[project.scripts]
flowmason = "flowmason_core.cli.main:cli"
fm = "flowmason_core.cli.main:cli"
```

**studio/pyproject.toml:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "flowmason-studio"
version = "0.4.0"
description = "FlowMason Studio Backend"
requires-python = ">=3.11"
dependencies = [
    "flowmason-core>=0.4.0",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
]
```

**lab/pyproject.toml:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "flowmason-lab"
version = "0.4.0"
description = "FlowMason Built-in Components"
requires-python = ">=3.11"
dependencies = [
    "flowmason-core>=0.4.0",
]
```

### 2. Publish Order

Publish in dependency order:
1. `flowmason-core` (no FlowMason dependencies)
2. `flowmason-studio` (depends on core)
3. `flowmason-lab` (depends on core)

### 3. GitHub Action for Multiple Packages

```yaml
name: Publish Packages

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: [core, studio, lab]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: pip install build twine

      - name: Build wheel only
        working-directory: ${{ matrix.package }}
        run: python -m build --wheel

      - name: Publish to PyPI
        working-directory: ${{ matrix.package }}
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

---

## Version Management

### Manual Versioning

Update version in `pyproject.toml` before each release.

### Automatic Versioning with Git Tags

Use `hatch-vcs` for automatic versioning from git tags:

```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
dynamic = ["version"]

[tool.hatch.version]
source = "vcs"
```

Then version comes from git tags:
```bash
git tag v0.4.0
git push --tags
```

---

## Checklist Before Publishing

- [ ] Version updated in `pyproject.toml`
- [ ] License set to `"Proprietary"`
- [ ] README.md is up to date (becomes PyPI page)
- [ ] LICENSE file exists with proprietary terms
- [ ] URLs point to website (not GitHub)
- [ ] All tests pass (`pytest`)
- [ ] Code is linted (`ruff check .`)
- [ ] Built with `--wheel` only (no source distribution)
- [ ] Tested on TestPyPI first
- [ ] Verified installation in fresh environment
- [ ] Verified no source files exposed in wheel

---

## Troubleshooting

### "Package already exists"

Each version can only be published once. Bump the version number.

### "Invalid distribution"

Run `twine check dist/*` to see what's wrong. Common issues:
- Missing README.md
- Invalid classifiers
- Malformed pyproject.toml

### "Authentication failed"

- Use `__token__` as username (literally)
- Use the full token including `pypi-` prefix
- Ensure 2FA is enabled on your PyPI account

### Package doesn't include all files

Check `[tool.hatch.build.targets.wheel]` in pyproject.toml:

```toml
[tool.hatch.build.targets.wheel]
packages = ["core/flowmason_core", "studio/flowmason_studio", "lab/flowmason_lab"]
```

---

## Closed-Source Summary

| Aspect | How to Keep Private |
|--------|---------------------|
| **Source Code** | Build `--wheel` only (no `.tar.gz`) |
| **License** | Use `"Proprietary"` license |
| **Repository** | Keep GitHub repo private |
| **URLs** | Point to website, not GitHub |
| **Distribution** | Users get compiled `.pyc` files in wheel |

**What users CAN see:**
- Package name, description, version on PyPI
- README content (your marketing page)
- List of dependencies
- Compiled Python bytecode (`.pyc` files)

**What users CANNOT see:**
- Original `.py` source files
- Internal implementation details
- Private repository

**Note:** Python bytecode can be decompiled, but it's not trivial. For additional protection, consider tools like PyArmor or Cython compilation.

---

## Links

- [PyPI](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Hatchling Documentation](https://hatch.pypa.io/)
- [Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
