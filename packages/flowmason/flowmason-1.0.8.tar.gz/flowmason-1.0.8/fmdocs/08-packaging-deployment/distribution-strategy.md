# FlowMason Distribution Strategy

This guide covers distributing FlowMason as a **closed-source** product across three channels.

## Overview

| Component | Channel | Install Command |
|-----------|---------|-----------------|
| **VSCode Extension** | VS Code Marketplace | Install from Extensions panel |
| **Local Runtime** | PyPI | `pip install flowmason` |
| **Production Runtime** | Docker Hub | `docker pull flowmason/studio:0.4.0` |

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DISTRIBUTION                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   VSCode Extension          Python Runtime         Docker Images    │
│   ┌─────────────┐          ┌─────────────┐        ┌─────────────┐  │
│   │ Marketplace │          │    PyPI     │        │ Docker Hub  │  │
│   │             │          │             │        │             │  │
│   │ .vsix       │          │ .whl        │        │ Image       │  │
│   └──────┬──────┘          └──────┬──────┘        └──────┬──────┘  │
│          │                        │                      │         │
│          ▼                        ▼                      ▼         │
│   code --install           pip install            docker pull      │
│   flowmason                flowmason              flowmason/studio │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. VSCode Extension → VS Code Marketplace

### Prerequisites

1. **Microsoft/Azure Account**
   - Go to [https://marketplace.visualstudio.com/manage](https://marketplace.visualstudio.com/manage)
   - Sign in with Microsoft account

2. **Create Publisher**
   - Click "Create Publisher"
   - Publisher ID: `flowmason` (used in extension ID)
   - Display Name: `FlowMason`

3. **Personal Access Token (PAT)**
   - Go to [Azure DevOps](https://dev.azure.com/)
   - User Settings → Personal Access Tokens
   - Create token with **Marketplace (Manage)** scope
   - Save the token securely

### Update package.json

```json
{
  "name": "flowmason",
  "displayName": "FlowMason",
  "description": "AI Pipeline Development for VSCode",
  "version": "0.4.0",
  "publisher": "flowmason",
  "icon": "images/icon.png",
  "repository": {
    "type": "git",
    "url": "https://flowmason.com"
  },
  "homepage": "https://flowmason.com",
  "bugs": {
    "url": "https://flowmason.com/support"
  }
}
```

**Note:** `repository` URL doesn't need to be a real Git repo - can be your website.

### Build and Publish

```bash
cd vscode-extension

# Install vsce (VS Code Extension manager)
npm install -g @vscode/vsce

# Login with your PAT
vsce login flowmason

# Package (creates .vsix)
vsce package

# Publish to Marketplace
vsce publish
```

### Verify Publication

1. Go to [VS Code Marketplace](https://marketplace.visualstudio.com/)
2. Search for "FlowMason"
3. Your extension should appear

### Users Install Via

- **VSCode UI**: Extensions panel → Search "FlowMason" → Install
- **Command**: `code --install-extension flowmason.flowmason`

---

## 2. Python Runtime → PyPI (Closed Source)

### Prerequisites

1. **PyPI Account**: [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. **API Token**: [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
3. **Build Tools**: `pip install build twine`

### Configure pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "flowmason"
version = "0.4.0"
description = "Universal AI Workflow Infrastructure"
readme = "README.md"
requires-python = ">=3.11"
license = "Proprietary"
authors = [
    { name = "FlowMason", email = "support@flowmason.com" }
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "pydantic>=2.0.0",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "typer>=0.9.0",
    "rich>=13.0.0",
    "httpx>=0.26.0",
]

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

**Key Points:**
- `license = "Proprietary"` - Indicates closed source
- `License :: Other/Proprietary License` - PyPI classifier
- No repository URL required

### Create README.md for PyPI

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

Proprietary. See LICENSE file for terms.
```

### Create LICENSE File

```
FlowMason Proprietary License

Copyright (c) 2025 FlowMason

All rights reserved.

This software and associated documentation files (the "Software") are proprietary
and confidential. Unauthorized copying, modification, distribution, or use of
this Software, via any medium, is strictly prohibited.

The Software is provided "as is", without warranty of any kind, express or implied.

For licensing inquiries, contact: licensing@flowmason.com
```

### Build and Publish

```bash
cd /path/to/flowmason

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build wheel only (no source distribution)
python -m build --wheel

# Verify
twine check dist/*

# Publish
twine upload dist/*
# Username: __token__
# Password: pypi-your-api-token
```

### Users Install Via

```bash
pip install flowmason
```

---

## 3. Production Runtime → Docker Hub

### Prerequisites

1. **Docker Hub Account**: [https://hub.docker.com/signup](https://hub.docker.com/signup)
2. **Create Repository**: `flowmason/studio`
3. **Docker Installed**: For building images

### Create Dockerfile

`docker/Dockerfile.studio`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python package
COPY dist/flowmason-*.whl /tmp/
RUN pip install --no-cache-dir /tmp/flowmason-*.whl && rm /tmp/*.whl

# Create non-root user
RUN useradd -m -u 1000 flowmason
USER flowmason

# Expose port
EXPOSE 8999

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8999/health || exit 1

# Start Studio
CMD ["fm", "studio", "start", "--host", "0.0.0.0", "--port", "8999"]
```

### Build and Push

```bash
# Build Python wheel first
python -m build --wheel

# Build Docker image
docker build -f docker/Dockerfile.studio -t flowmason/studio:0.4.0 .
docker tag flowmason/studio:0.4.0 flowmason/studio:latest

# Login to Docker Hub
docker login

# Push images
docker push flowmason/studio:0.4.0
docker push flowmason/studio:latest
```

### Docker Compose for Users

Create `docker-compose.yml` for documentation:

```yaml
version: '3.8'

services:
  studio:
    image: flowmason/studio:0.4.0
    ports:
      - "8999:8999"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/flowmason
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=flowmason
    volumes:
      - flowmason_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  flowmason_data:
```

### Users Deploy Via

```bash
# Simple
docker pull flowmason/studio:0.4.0
docker run -p 8999:8999 flowmason/studio:0.4.0

# Production
docker-compose up -d
```

---

## CI/CD Automation

### GitHub Actions (Private Repo)

`.github/workflows/release.yml`:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  # Build and publish Python package
  publish-pypi:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install build tools
        run: pip install build twine

      - name: Build wheel
        run: python -m build --wheel

      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*

  # Build and publish Docker image
  publish-docker:
    runs-on: ubuntu-latest
    needs: publish-pypi
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Build wheel
        run: |
          pip install build
          python -m build --wheel

      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Extract version
        id: version
        run: echo "VERSION=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/Dockerfile.studio
          push: true
          tags: |
            flowmason/studio:${{ steps.version.outputs.VERSION }}
            flowmason/studio:latest

  # Publish VSCode extension
  publish-vscode:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        working-directory: vscode-extension
        run: npm install

      - name: Publish to Marketplace
        working-directory: vscode-extension
        env:
          VSCE_PAT: ${{ secrets.VSCE_PAT }}
        run: |
          npm install -g @vscode/vsce
          vsce publish -p $VSCE_PAT
```

### Required Secrets

Add to GitHub repository Settings → Secrets:

| Secret | Description |
|--------|-------------|
| `PYPI_API_TOKEN` | PyPI API token |
| `DOCKERHUB_USERNAME` | Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub access token |
| `VSCE_PAT` | VS Code Marketplace PAT |

---

## Release Checklist

- [ ] Update version in:
  - [ ] `pyproject.toml`
  - [ ] `vscode-extension/package.json`
  - [ ] `docker/Dockerfile.studio` (if hardcoded)
- [ ] Update CHANGELOG
- [ ] Test locally:
  - [ ] `pip install dist/*.whl`
  - [ ] `code --install-extension *.vsix`
  - [ ] `docker build` and run
- [ ] Create git tag: `git tag v0.4.0 && git push --tags`
- [ ] CI/CD publishes automatically

---

## User Installation Summary

### For Developers (Local Development)

```bash
# 1. Install VSCode extension
# → Search "FlowMason" in Extensions panel

# 2. Install Python runtime
pip install flowmason

# 3. Initialize project
fm init
fm studio start
```

### For Operations (Production/Staging)

```bash
# Pull and run Docker image
docker pull flowmason/studio:0.4.0

# Or use docker-compose
curl -O https://flowmason.com/docker-compose.yml
docker-compose up -d
```

---

## Pricing Model Considerations

With closed-source distribution, you can implement:

| Model | How |
|-------|-----|
| **Free** | Publish everything, no restrictions |
| **Freemium** | Free local, paid production features |
| **License Key** | Check key on startup, disable without valid key |
| **Usage-Based** | Track API calls, charge based on usage |
| **Enterprise** | Private Docker registry, custom contracts |

The distribution channels (Marketplace, PyPI, Docker Hub) all support both free and commercial software.
