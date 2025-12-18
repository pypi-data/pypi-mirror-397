# Docker Deployment

FlowMason Studio provides Docker configurations for local development, staging, and production environments.

## Deployment Options

| Environment | Config File | Use Case |
|-------------|-------------|----------|
| **Local** | `docker-compose.yml` | Development, testing |
| **Development** | `docker-compose.dev.yml` | Hot reload, debugging |
| **Staging** | `docker-compose.staging.yml` | Pre-production testing |
| **Production** | `docker-compose.prod.yml` | Production deployment |

---

## Local Development

### Quick Start

```bash
# Start Studio (builds image if needed)
docker-compose up

# Studio is now available at http://localhost:8999
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLOWMASON_PORT` | `8999` | Port to expose Studio on |
| `PIPELINES_DIR` | `./pipelines` | Local directory to mount for pipelines |
| `OPENAI_API_KEY` | - | OpenAI API key for LLM providers |
| `ANTHROPIC_API_KEY` | - | Anthropic API key for Claude |

### Custom Port

```bash
FLOWMASON_PORT=3000 docker-compose up
```

### Custom Pipeline Directory

```bash
PIPELINES_DIR=/path/to/my/pipelines docker-compose up
```

### With API Keys

```bash
OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-ant-... docker-compose up
```

## Development Mode

For active development with hot reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This enables:
- **Hot reload**: Python code changes are automatically reloaded
- **Source mounting**: Local source code is mounted into the container
- **Debug logging**: More verbose logging output

## Docker Commands Reference

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild image (after code changes)
docker-compose build

# Remove all data (fresh start)
docker-compose down -v
```

## Architecture

The Docker setup uses a multi-stage build:

1. **Frontend Build Stage**: Builds the React frontend with Node.js
2. **Runtime Stage**: Python 3.11 slim image with:
   - FlowMason core, studio, and lab packages
   - Built frontend static files
   - Uvicorn ASGI server

## Data Persistence

Data is persisted in a Docker volume:

- **`flowmason-data`**: Contains SQLite database, run history, and settings

To completely reset:

```bash
docker-compose down -v
```

## Health Check

The container includes a health check that verifies Studio is responding:

```bash
# Check container health
docker-compose ps
```

The `/health` endpoint returns:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Troubleshooting

### Port Already in Use

```bash
# Use a different port
FLOWMASON_PORT=9000 docker-compose up
```

### Build Failures

```bash
# Rebuild without cache
docker-compose build --no-cache
```

### Permission Issues

If you encounter permission issues with mounted volumes:

```bash
# Run with current user (Linux)
docker-compose run --user $(id -u):$(id -g) studio
```

---

## Staging Deployment

The staging environment includes PostgreSQL, Redis, and Traefik with auto-SSL.

### Prerequisites

1. A server with Docker and Docker Compose installed
2. A domain name pointing to your server
3. Ports 80 and 443 available

### Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your values
nano .env
```

Required environment variables:
```bash
DOMAIN=flowmason.example.com
ACME_EMAIL=admin@example.com
POSTGRES_PASSWORD=your-strong-password
REDIS_PASSWORD=your-strong-password
```

### Deploy

```bash
# Start all services
docker-compose -f docker-compose.staging.yml up -d

# View logs
docker-compose -f docker-compose.staging.yml logs -f

# Check status
docker-compose -f docker-compose.staging.yml ps
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Traefik (Reverse Proxy)                                     │
│  - Auto-SSL via Let's Encrypt                               │
│  - HTTP → HTTPS redirect                                     │
│  - Ports: 80, 443                                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  FlowMason Studio                                            │
│  - Single instance                                           │
│  - Port: 8999 (internal)                                     │
└─────────────────────────────────────────────────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────────┐
│  PostgreSQL              │   │  Redis                       │
│  - Persistent storage    │   │  - Session cache             │
│  - Port: 5432 (internal) │   │  - Port: 6379 (internal)     │
└─────────────────────────┘   └─────────────────────────────┘
```

---

## Production Deployment

The production environment adds horizontal scaling, network isolation, and stricter security.

### Prerequisites

1. A production server (recommended: 4+ CPU, 8GB+ RAM)
2. A domain name with DNS configured
3. Docker Swarm or Compose v2 for replicas

### Setup

```bash
# Copy environment template
cp .env.example .env

# Configure required variables
nano .env
```

Required environment variables:
```bash
DOMAIN=flowmason.example.com
ACME_EMAIL=admin@example.com
POSTGRES_PASSWORD=very-strong-password-here
REDIS_PASSWORD=very-strong-password-here
FLOWMASON_SECRETS_KEY=$(openssl rand -base64 32)
VERSION=1.0.0
```

### Deploy

```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Scale Studio instances
docker-compose -f docker-compose.prod.yml up -d --scale studio=3

# View logs
docker-compose -f docker-compose.prod.yml logs -f studio
```

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Internet                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Traefik (Reverse Proxy)                                     │
│  - Production TLS with HSTS                                  │
│  - Security headers                                          │
│  - Load balancing                                            │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Studio #1      │ │  Studio #2      │ │  Studio #N      │
│  (replica)      │ │  (replica)      │ │  (replica)      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────────┐
│  PostgreSQL              │   │  Redis                       │
│  - Tuned for production  │   │  - LRU eviction              │
│  - Internal network only │   │  - Internal network only     │
└─────────────────────────┘   └─────────────────────────────┘
```

### Features

| Feature | Staging | Production |
|---------|---------|------------|
| Auto-SSL (Let's Encrypt) | Staging certs | Production certs |
| HSTS | No | Yes |
| Security headers | Basic | Full |
| Database | PostgreSQL | PostgreSQL (tuned) |
| Replicas | 1 | 2+ (configurable) |
| Network isolation | No | Yes (internal network) |
| Rolling updates | No | Yes |
| Resource limits | Basic | Strict |

### Security Considerations

1. **Required variables**: Production enforces required secrets
2. **Network isolation**: Database and Redis on internal-only network
3. **Auth required**: `FLOWMASON_REQUIRE_AUTH=true` by default
4. **Security headers**: HSTS, X-Content-Type-Options, X-XSS-Protection
5. **Non-root user**: Studio runs as non-root `flowmason` user

### Backup

```bash
# Backup PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres \
  pg_dump -U flowmason flowmason > backup.sql

# Backup Redis
docker-compose -f docker-compose.prod.yml exec redis \
  redis-cli -a $REDIS_PASSWORD BGSAVE
```

### Monitoring

```bash
# Container stats
docker stats

# Health check
curl -f https://flowmason.example.com/health

# Logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100
```

---

## Image Versioning

For production, always pin to a specific version:

```bash
# Build with version tag
docker build -t flowmason/studio:1.0.0 .

# Use in docker-compose
VERSION=1.0.0 docker-compose -f docker-compose.prod.yml up -d
```

## Resource Recommendations

| Environment | CPU | Memory | Storage |
|-------------|-----|--------|---------|
| Local | 1 | 1GB | 5GB |
| Staging | 2 | 4GB | 20GB |
| Production | 4+ | 8GB+ | 50GB+ |
