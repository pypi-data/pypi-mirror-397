# Pipeline Marketplace

FlowMason Studio includes a marketplace for sharing and discovering pipeline templates.

## Overview

The Pipeline Marketplace provides:

- **Discovery**: Browse and search pipeline templates
- **Publishing**: Share your pipelines with the community
- **Reviews**: Rate and review pipelines
- **Collections**: Curated sets of related pipelines
- **Versioning**: Publish new versions with changelogs
- **Installation**: One-click install to your workspace

## Quick Start

### Browse Featured Pipelines

```http
GET /api/v1/marketplace/featured
```

**Response:**
```json
[
  {
    "id": "listing_1",
    "slug": "content-summarizer",
    "name": "Content Summarizer",
    "tagline": "Summarize long articles into concise key points",
    "category": "ai_generation",
    "publisher": {
      "name": "FlowMason Team",
      "verified": true
    },
    "stats": {
      "downloads": 150,
      "average_rating": 4.8
    },
    "pricing": {
      "model": "free"
    },
    "featured": true
  }
]
```

### Search Pipelines

```http
POST /api/v1/marketplace/search
Content-Type: application/json

{
  "query": "summarize",
  "category": "ai_generation",
  "pricing": "free",
  "min_rating": 4.0,
  "sort_by": "downloads",
  "page": 1,
  "per_page": 20
}
```

Or use GET:
```http
GET /api/v1/marketplace/search?query=summarize&category=ai_generation&sort_by=downloads
```

### View Listing Details

```http
GET /api/v1/marketplace/listings/listing_1
```

Or by slug:
```http
GET /api/v1/marketplace/listings/by-slug/content-summarizer
```

**Response:**
```json
{
  "id": "listing_1",
  "slug": "content-summarizer",
  "name": "Content Summarizer",
  "tagline": "Summarize long articles into concise key points",
  "description": "A complete pipeline for summarizing long-form content...",
  "category": "ai_generation",
  "tags": ["summarization", "ai", "content", "nlp"],
  "status": "published",
  "publisher": {
    "id": "pub_flowmason",
    "name": "FlowMason Team",
    "verified": true,
    "total_listings": 5,
    "average_rating": 4.8
  },
  "pipeline_template": {
    "name": "content-summarizer",
    "stages": [...]
  },
  "readme": "# Content Summarizer\n\n...",
  "current_version": "1.0.0",
  "versions": [
    {
      "version": "1.0.0",
      "released_at": "2024-01-15T10:00:00Z",
      "changelog": "Initial release",
      "downloads": 150
    }
  ],
  "pricing": {
    "model": "free"
  },
  "stats": {
    "views": 500,
    "downloads": 150,
    "favorites": 25,
    "reviews": 10,
    "average_rating": 4.8
  }
}
```

## Categories

| Category | Description |
|----------|-------------|
| `ai_generation` | AI-powered content generation |
| `data_processing` | Transform, validate, and clean data |
| `integration` | Connect to external APIs and services |
| `automation` | Automate repetitive tasks |
| `analytics` | Analyze data and generate insights |
| `content` | Content moderation and management |
| `devops` | CI/CD, deployment, infrastructure |
| `other` | Miscellaneous pipelines |

### Get Categories

```http
GET /api/v1/marketplace/categories
```

### Browse by Category

```http
GET /api/v1/marketplace/categories/ai_generation?limit=20
```

## Installation

### Install a Listing

```http
POST /api/v1/marketplace/listings/{listing_id}/install
Content-Type: application/json

{
  "version": "1.0.0",
  "create_pipeline": true,
  "pipeline_name": "My Summarizer",
  "customizations": {
    "model": "gpt-4"
  }
}
```

**Response:**
```json
{
  "id": "install_xyz",
  "listing_id": "listing_1",
  "version": "1.0.0",
  "installed_at": "2024-01-15T12:00:00Z",
  "pipeline_id": "pipe_abc123",
  "customizations": {...}
}
```

### Get My Installations

```http
GET /api/v1/marketplace/installations
```

## Publishing

### Create a Listing

```http
POST /api/v1/marketplace/listings
Content-Type: application/json

{
  "name": "My Pipeline",
  "tagline": "A brief description of what it does",
  "description": "Detailed description of the pipeline...",
  "category": "ai_generation",
  "tags": ["ai", "automation"],
  "pipeline_template": {
    "name": "my-pipeline",
    "stages": [...]
  },
  "pricing": {
    "model": "free"
  },
  "readme": "# My Pipeline\n\n## Usage\n..."
}
```

### Update a Listing

```http
PATCH /api/v1/marketplace/listings/{listing_id}
Content-Type: application/json

{
  "tagline": "Updated tagline",
  "description": "Updated description",
  "tags": ["ai", "automation", "new-tag"]
}
```

### Submit for Review

```http
POST /api/v1/marketplace/listings/{listing_id}/submit
```

### Publish a New Version

```http
POST /api/v1/marketplace/listings/{listing_id}/versions
Content-Type: application/json

{
  "version": "1.1.0",
  "changelog": "Added support for multiple output formats",
  "pipeline_template": {
    "name": "my-pipeline",
    "stages": [...]
  },
  "min_flowmason_version": "0.7.0"
}
```

### Archive a Listing

```http
POST /api/v1/marketplace/listings/{listing_id}/archive
```

## Reviews

### Submit a Review

```http
POST /api/v1/marketplace/listings/{listing_id}/reviews
Content-Type: application/json

{
  "rating": 5,
  "title": "Excellent pipeline!",
  "content": "This pipeline saved me hours of work..."
}
```

### Get Reviews

```http
GET /api/v1/marketplace/listings/{listing_id}/reviews?limit=20&offset=0
```

### Mark Review Helpful

```http
POST /api/v1/marketplace/listings/{listing_id}/reviews/{review_id}/helpful
```

## User Library

### Get My Library

```http
GET /api/v1/marketplace/library
```

**Response:**
```json
{
  "user_id": "user_123",
  "purchased": ["listing_1", "listing_2"],
  "favorites": ["listing_1", "listing_3"],
  "installed": ["listing_1"],
  "recently_viewed": ["listing_1", "listing_4", "listing_5"]
}
```

### Add to Favorites

```http
POST /api/v1/marketplace/library/favorites/{listing_id}
```

### Remove from Favorites

```http
DELETE /api/v1/marketplace/library/favorites/{listing_id}
```

## Collections

Curated sets of related pipelines.

### List Collections

```http
GET /api/v1/marketplace/collections
```

**Response:**
```json
[
  {
    "id": "coll_1",
    "name": "AI Starter Kit",
    "description": "Essential AI pipelines for getting started",
    "slug": "ai-starter-kit",
    "listings": ["listing_1", "listing_2", "listing_3"],
    "curated_by": "user_curator",
    "featured": true
  }
]
```

### Get Collection

```http
GET /api/v1/marketplace/collections/{collection_id}
```

### Create Collection

```http
POST /api/v1/marketplace/collections
Content-Type: application/json

{
  "name": "My Collection",
  "description": "A collection of my favorite pipelines",
  "listing_ids": ["listing_1", "listing_2"]
}
```

### Add to Collection

```http
POST /api/v1/marketplace/collections/{collection_id}/listings/{listing_id}
```

## Publishers

### Get Publisher Profile

```http
GET /api/v1/marketplace/publishers/{publisher_id}
```

**Response:**
```json
{
  "id": "pub_flowmason",
  "name": "FlowMason Team",
  "username": "flowmason",
  "verified": true,
  "member_since": "2024-01-01T00:00:00Z",
  "total_listings": 5,
  "total_downloads": 1000,
  "average_rating": 4.8
}
```

### Get Publisher Listings

```http
GET /api/v1/marketplace/publishers/{publisher_id}/listings
```

## Statistics

### Get Marketplace Stats

```http
GET /api/v1/marketplace/stats
```

**Response:**
```json
{
  "total_listings": 150,
  "total_publishers": 45,
  "total_downloads": 10000,
  "total_reviews": 500,
  "categories": {
    "ai_generation": 45,
    "data_processing": 30,
    "integration": 25,
    "automation": 20,
    "analytics": 15,
    "content": 10,
    "devops": 5
  },
  "trending": ["listing_1", "listing_5", "listing_3"],
  "new_this_week": 12
}
```

## Pricing Models

| Model | Description |
|-------|-------------|
| `free` | Free to use |
| `one_time` | One-time purchase |
| `subscription` | Monthly/yearly subscription |
| `usage_based` | Pay per execution |

## Listing Status

| Status | Description |
|--------|-------------|
| `draft` | Not yet submitted |
| `pending_review` | Awaiting review |
| `published` | Live in marketplace |
| `rejected` | Review rejected |
| `archived` | No longer available |

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/marketplace/featured` | GET | Get featured listings |
| `/marketplace/trending` | GET | Get trending listings |
| `/marketplace/new` | GET | Get newest listings |
| `/marketplace/categories` | GET | List categories |
| `/marketplace/categories/{cat}` | GET | Get category listings |
| `/marketplace/search` | GET/POST | Search listings |
| `/marketplace/listings` | POST | Create listing |
| `/marketplace/listings/{id}` | GET | Get listing |
| `/marketplace/listings/{id}` | PATCH | Update listing |
| `/marketplace/listings/{id}/submit` | POST | Submit for review |
| `/marketplace/listings/{id}/archive` | POST | Archive listing |
| `/marketplace/listings/{id}/versions` | POST | Publish version |
| `/marketplace/listings/{id}/install` | POST | Install listing |
| `/marketplace/listings/{id}/reviews` | GET | Get reviews |
| `/marketplace/listings/{id}/reviews` | POST | Submit review |
| `/marketplace/installations` | GET | Get my installations |
| `/marketplace/library` | GET | Get my library |
| `/marketplace/library/favorites/{id}` | POST | Add favorite |
| `/marketplace/library/favorites/{id}` | DELETE | Remove favorite |
| `/marketplace/collections` | GET | List collections |
| `/marketplace/collections` | POST | Create collection |
| `/marketplace/collections/{id}` | GET | Get collection |
| `/marketplace/publishers/{id}` | GET | Get publisher |
| `/marketplace/publishers/{id}/listings` | GET | Publisher listings |
| `/marketplace/stats` | GET | Get marketplace stats |
