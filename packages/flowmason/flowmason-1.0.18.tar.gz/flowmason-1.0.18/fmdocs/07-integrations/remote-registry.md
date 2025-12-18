# Remote Registry

FlowMason supports remote package registries for sharing and distributing components across teams and projects.

## Overview

The remote registry system enables:
- **Package Discovery**: Search for packages across multiple registries
- **Version Management**: Install specific versions with dependency resolution
- **Package Distribution**: Publish packages to registries
- **Multi-Registry Support**: Configure multiple registries with priorities
- **Local Caching**: Downloaded packages are cached locally

## CLI Commands

### Managing Registries

```bash
# List configured registries
fm registry list

# Add a new registry
fm registry add my-registry https://registry.example.com

# Add with authentication
fm registry add private-registry https://registry.example.com --token $TOKEN

# Set as default
fm registry add my-registry https://registry.example.com --default

# Remove a registry
fm registry remove my-registry

# Set default registry
fm registry set-default my-registry
```

### Searching Packages

```bash
# Search all registries
fm search summarizer

# Search specific registry
fm search summarizer --registry my-registry

# Filter by category
fm search filter --category transformers

# Output as JSON
fm search summarizer --json
```

### Installing Packages

```bash
# Install latest version
fm install my-package

# Install specific version
fm install my-package --version 1.2.0

# Install from specific registry
fm install my-package --registry my-registry

# Install to custom directory
fm install my-package --dir ./packages
```

### Publishing Packages

```bash
# Publish to default registry
fm publish my-package-1.0.0.fmpkg

# Publish to specific registry
fm publish my-package-1.0.0.fmpkg --registry my-registry
```

### Cache Management

```bash
# View cache stats
fm registry cache

# Clear all cached packages
fm registry cache --clear

# Clear packages older than 30 days
fm registry cache --clear --older-than 30
```

## Configuration

Registries are configured in `~/.flowmason/registries.json`:

```json
{
  "registries": [
    {
      "name": "local",
      "url": "http://localhost:8999",
      "priority": 50,
      "enabled": true,
      "is_default": true,
      "can_publish": true,
      "requires_auth": false,
      "description": "Local FlowMason Studio"
    },
    {
      "name": "company",
      "url": "https://registry.company.com",
      "auth_token": "...",
      "priority": 100,
      "enabled": true,
      "can_publish": true,
      "requires_auth": true
    }
  ]
}
```

### Configuration Options

| Option | Description |
|--------|-------------|
| `name` | Unique identifier for the registry |
| `url` | Base URL of the registry |
| `auth_token` | Optional authentication token |
| `priority` | Lower = higher priority (default: 100) |
| `enabled` | Whether the registry is active |
| `is_default` | Use as default for operations |
| `can_publish` | Whether publishing is allowed |
| `requires_auth` | Whether authentication is required |

## Running a Registry Server

FlowMason Studio can act as a registry server. When Studio is running, it exposes registry API endpoints.

### Start Studio as Registry

```bash
fm studio start
```

The registry API is available at `http://localhost:8999/api/v1/registry/`.

### Registry API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/registry/health` | GET | Check registry health |
| `/registry/packages/search` | GET | Search packages |
| `/registry/packages/{name}` | GET | Get package info |
| `/registry/packages/{name}/{version}` | GET | Get specific version |
| `/registry/packages/{name}/versions` | GET | List all versions |
| `/registry/packages/{name}/{version}/download` | GET | Download package |
| `/registry/packages/upload` | POST | Upload package |
| `/registry/categories` | GET | List categories |
| `/registry/stats` | GET | Registry statistics |

## Python API

```python
from flowmason_core.registry import (
    get_remote_registry,
    RemoteRegistryClient,
)

# Get the global client
client = get_remote_registry()

# Add a registry
client.add_registry(
    name="my-registry",
    url="https://registry.example.com",
    auth_token="...",
    priority=100,
)

# Search for packages
results = client.search("summarizer")
for pkg in results.packages:
    print(f"{pkg.name} v{pkg.version}: {pkg.description}")

# Get package info
pkg = client.get_package("my-package")
print(f"Components: {pkg.components}")

# Download and install
install_path = client.install("my-package", version="1.0.0")
print(f"Installed to: {install_path}")

# Publish a package
from pathlib import Path
pkg_info = client.publish(Path("my-package-1.0.0.fmpkg"))
print(f"Published: {pkg_info.name}@{pkg_info.version}")
```

## Package Verification

Downloaded packages are verified using SHA256 checksums:

```python
# Downloads automatically verify checksum
client.download("my-package", verify=True)

# Skip verification (not recommended)
client.download("my-package", verify=False)
```

## Multi-Registry Resolution

When searching or installing, registries are queried in priority order:

1. Registries with lower priority numbers are checked first
2. First match is used for installation
3. Search aggregates results from all enabled registries

```python
# Configure priorities
client.add_registry("primary", "https://primary.example.com", priority=10)
client.add_registry("fallback", "https://fallback.example.com", priority=100)

# primary will be checked first
client.install("my-package")
```

## Authentication

### Token-Based Auth

```bash
# Add registry with token
fm registry add private https://registry.example.com --token $MY_TOKEN
```

### Environment Variables

You can also set tokens via environment variables:

```bash
export FLOWMASON_REGISTRY_TOKEN=your-token
```

## Best Practices

1. **Use Specific Versions**: Always specify versions in production
2. **Private Registries**: Use authentication for private packages
3. **Cache Management**: Periodically clean old cached packages
4. **Checksum Verification**: Always verify package checksums
5. **Priority Planning**: Set priorities to control resolution order

## Troubleshooting

### Connection Issues

```bash
# Check registry health
curl https://registry.example.com/api/v1/registry/health
```

### Authentication Errors

```bash
# Verify token is set
fm registry list --all

# Re-add with correct token
fm registry remove my-registry
fm registry add my-registry https://... --token $TOKEN
```

### Package Not Found

```bash
# Check available versions
fm search my-package --json

# Try specific registry
fm install my-package --registry other-registry
```
