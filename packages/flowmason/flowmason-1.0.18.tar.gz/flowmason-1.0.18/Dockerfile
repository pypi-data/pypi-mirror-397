# FlowMason Studio Docker Image
# Multi-stage build: Node.js frontend + Python backend

# =============================================================================
# Stage 1: Build Frontend
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY studio/frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY studio/frontend/ ./

# Build frontend
RUN npm run build

# =============================================================================
# Stage 2: Python Runtime
# =============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLOWMASON_HOST=0.0.0.0 \
    FLOWMASON_PORT=8999

# Create non-root user for security
RUN groupadd -r flowmason && useradd -r -g flowmason flowmason

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python package files
COPY pyproject.toml README.md ./
COPY core/ ./core/
COPY studio/ ./studio/
COPY lab/ ./lab/

# Install FlowMason
RUN pip install --no-cache-dir -e .

# Copy built frontend to static directory
COPY --from=frontend-builder /app/frontend/dist /app/studio/frontend/dist

# Create directories for data persistence
RUN mkdir -p /app/data /app/pipelines && \
    chown -R flowmason:flowmason /app

# Switch to non-root user
USER flowmason

# Expose port
EXPOSE 8999

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8999/health || exit 1

# Default command - start Studio
CMD ["python", "-m", "uvicorn", "flowmason_studio.api.app:app", "--host", "0.0.0.0", "--port", "8999"]
