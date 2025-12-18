# Component Visual - Rich Cards

FlowMason Studio provides rich visual representations of components for building interactive pipeline editors.

## Overview

The Component Visual API provides:

- **Rich Cards**: Visual component cards with icons, colors, and badges
- **Port Visualization**: Input/output port definitions for connections
- **Categories & Themes**: Consistent visual categorization
- **Component Palette**: Organized component browser with groups
- **Pipeline Visualization**: Complete visual representation of pipelines
- **Favorites & Recent**: Quick access to commonly used components

## Quick Start

### Get All Component Visuals

```http
GET /api/v1/component-visual/components
```

**Response:**
```json
[
  {
    "component_type": "generator",
    "name": "Generator",
    "description": "Generate text content using LLM",
    "category": "ai",
    "theme": {
      "primary_color": "#8b5cf6",
      "secondary_color": "#a78bfa",
      "icon": "sparkles",
      "icon_color": "#ffffff",
      "gradient": "linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)"
    },
    "ports": [
      {
        "id": "input",
        "name": "Input",
        "direction": "input",
        "type": "any",
        "required": true
      },
      {
        "id": "prompt",
        "name": "Prompt",
        "direction": "input",
        "type": "string",
        "required": true
      },
      {
        "id": "output",
        "name": "Output",
        "direction": "output",
        "type": "any"
      }
    ],
    "badges": [
      {
        "id": "llm",
        "label": "LLM",
        "color": "primary",
        "icon": "sparkles",
        "tooltip": "Uses language model"
      }
    ],
    "capabilities": [
      {
        "id": "llm",
        "name": "LLM Integration",
        "description": "Uses language model",
        "level": "advanced"
      },
      {
        "id": "streaming",
        "name": "Streaming",
        "description": "Supports streaming output",
        "level": "standard"
      }
    ],
    "tags": ["ai", "llm", "text", "generation"],
    "usage_count": 42,
    "popularity_score": 0.42
  }
]
```

### Filter by Category

```http
GET /api/v1/component-visual/components?category=ai
```

Categories:
- `ai` - LLM-powered components
- `data` - Data processing components
- `integration` - External service integrations
- `control` - Control flow components
- `utility` - Helper components
- `custom` - User-defined components

## Component Palette

### Get the Full Palette

```http
GET /api/v1/component-visual/palette
```

**Response:**
```json
{
  "groups": [
    {
      "id": "ai",
      "name": "AI Components",
      "description": "LLM-powered components for generation and evaluation",
      "icon": "sparkles",
      "color": "#8b5cf6",
      "components": ["generator", "critic", "improver", "synthesizer", "selector"],
      "order": 1
    },
    {
      "id": "data",
      "name": "Data Processing",
      "description": "Transform and validate data",
      "icon": "database",
      "color": "#3b82f6",
      "components": ["filter", "json_transform", "schema_validate", "variable_set"],
      "order": 2
    },
    {
      "id": "integration",
      "name": "Integrations",
      "description": "Connect to external services",
      "icon": "plug",
      "color": "#10b981",
      "components": ["http_request", "webhook"],
      "order": 3
    },
    {
      "id": "control",
      "name": "Control Flow",
      "description": "Manage execution flow",
      "icon": "git-branch",
      "color": "#f59e0b",
      "components": ["loop", "foreach", "conditional", "parallel", "output_router"],
      "order": 4
    }
  ],
  "recently_used": ["generator", "filter", "json_transform"],
  "favorites": ["generator", "http_request"]
}
```

### Get Specific Group

```http
GET /api/v1/component-visual/palette/groups/ai
```

## Favorites & Recently Used

### Get Favorites

```http
GET /api/v1/component-visual/favorites
```

### Add to Favorites

```http
POST /api/v1/component-visual/favorites/generator
```

### Remove from Favorites

```http
DELETE /api/v1/component-visual/favorites/generator
```

### Update All Favorites

```http
PUT /api/v1/component-visual/favorites
Content-Type: application/json

{
  "favorites": ["generator", "filter", "http_request"]
}
```

### Get Recently Used

```http
GET /api/v1/component-visual/recent?limit=10
```

### Record Usage

```http
POST /api/v1/component-visual/recent/generator
```

## Port Definitions

Each component has input and output ports for visual connections:

```json
{
  "ports": [
    {
      "id": "input",
      "name": "Input",
      "direction": "input",
      "type": "any",
      "description": "Main input data",
      "required": true,
      "multiple": false
    },
    {
      "id": "output",
      "name": "Output",
      "direction": "output",
      "type": "any",
      "description": "Stage output data"
    }
  ]
}
```

### Port Types

| Type | Description |
|------|-------------|
| `string` | Text data |
| `number` | Numeric data |
| `boolean` | True/false |
| `object` | JSON object |
| `array` | JSON array |
| `any` | Any data type |

### Special Ports

Some components have multiple output ports:

**Filter:**
```json
[
  {"id": "filtered", "name": "Filtered", "direction": "output"},
  {"id": "excluded", "name": "Excluded", "direction": "output"}
]
```

**Conditional:**
```json
[
  {"id": "true_branch", "name": "True", "direction": "output"},
  {"id": "false_branch", "name": "False", "direction": "output"}
]
```

## Badges

Badges indicate component status and capabilities:

```json
{
  "badges": [
    {
      "id": "llm",
      "label": "LLM",
      "color": "primary",
      "icon": "sparkles",
      "tooltip": "Uses language model"
    },
    {
      "id": "favorite",
      "label": "Favorite",
      "color": "danger",
      "icon": "heart"
    }
  ]
}
```

### Badge Colors

- `primary` - Primary brand color
- `success` - Green, positive status
- `warning` - Yellow, caution
- `danger` - Red, important/favorite
- `info` - Blue, informational
- `gray` - Neutral

## Themes

Each category has a consistent visual theme:

| Category | Primary Color | Icon |
|----------|---------------|------|
| AI | `#8b5cf6` | sparkles |
| Data | `#3b82f6` | database |
| Integration | `#10b981` | plug |
| Control | `#f59e0b` | git-branch |
| Utility | `#6b7280` | wrench |
| Custom | `#ec4899` | puzzle-piece |

## Pipeline Visualization

### Get Pipeline Visual

```http
GET /api/v1/component-visual/pipelines/{pipeline_id}?include_execution_state=true
```

**Response:**
```json
{
  "pipeline_id": "my-pipeline",
  "name": "My Pipeline",
  "stages": [
    {
      "stage_id": "generator_1",
      "component": {
        "component_type": "generator",
        "name": "Generator",
        "theme": {...}
      },
      "position": {"x": 100, "y": 100},
      "size": {"width": 250, "height": 150},
      "collapsed": false,
      "status": "completed",
      "progress": 1.0
    },
    {
      "stage_id": "filter_1",
      "component": {...},
      "position": {"x": 450, "y": 100},
      "status": "running",
      "progress": 0.5
    }
  ],
  "connections": [
    {
      "id": "generator_1->filter_1",
      "source_stage": "generator_1",
      "source_port": "output",
      "target_stage": "filter_1",
      "target_port": "input",
      "style": {
        "type": "bezier",
        "color": "#94a3b8",
        "width": 2,
        "animated": true
      }
    }
  ],
  "viewport": {"x": 0, "y": 0, "zoom": 1.0},
  "grid_enabled": true,
  "snap_to_grid": true,
  "grid_size": 20
}
```

### Update Stage Position

```http
PUT /api/v1/component-visual/pipelines/{pipeline_id}/stages/{stage_id}/position
Content-Type: application/json

{
  "x": 200,
  "y": 150
}
```

### Update Viewport

```http
PUT /api/v1/component-visual/pipelines/{pipeline_id}/viewport
Content-Type: application/json

{
  "x": 100,
  "y": 50,
  "zoom": 1.5
}
```

## Connection Styles

### Get Recommended Style

```http
GET /api/v1/component-visual/connection-style?source_type=generator&target_type=filter
```

**Response:**
```json
{
  "type": "bezier",
  "color": "#8b5cf6",
  "width": 2,
  "animated": true,
  "dashed": false
}
```

### Connection Types

- `bezier` - Smooth curved lines (default)
- `straight` - Direct lines
- `step` - Right-angle steps
- `smoothstep` - Rounded right-angle steps

## Search Components

```http
GET /api/v1/component-visual/search?q=filter&limit=10
```

Searches component names, descriptions, and tags.

## Categories API

### List Categories

```http
GET /api/v1/component-visual/categories
```

**Response:**
```json
[
  {
    "category": "ai",
    "name": "AI Components",
    "description": "LLM-powered components for generation and evaluation",
    "color": "#8b5cf6",
    "icon": "sparkles",
    "component_count": 5
  }
]
```

## Frontend Integration

### React Example

```tsx
import { useState, useEffect } from 'react';

interface ComponentVisual {
  component_type: string;
  name: string;
  theme: {
    primary_color: string;
    icon: string;
  };
  ports: Port[];
  badges: Badge[];
}

function ComponentCard({ component }: { component: ComponentVisual }) {
  return (
    <div
      className="component-card"
      style={{
        borderColor: component.theme.primary_color,
        background: component.theme.gradient
      }}
    >
      <div className="component-header">
        <span className="icon">{component.theme.icon}</span>
        <span className="name">{component.name}</span>
      </div>

      <div className="badges">
        {component.badges.map(badge => (
          <span
            key={badge.id}
            className={`badge badge-${badge.color}`}
            title={badge.tooltip}
          >
            {badge.label}
          </span>
        ))}
      </div>

      <div className="ports">
        <div className="inputs">
          {component.ports
            .filter(p => p.direction === 'input')
            .map(port => (
              <div key={port.id} className="port input">
                {port.name}
              </div>
            ))}
        </div>
        <div className="outputs">
          {component.ports
            .filter(p => p.direction === 'output')
            .map(port => (
              <div key={port.id} className="port output">
                {port.name}
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}

function ComponentPalette() {
  const [palette, setPalette] = useState(null);

  useEffect(() => {
    fetch('/api/v1/component-visual/palette')
      .then(res => res.json())
      .then(setPalette);
  }, []);

  if (!palette) return <div>Loading...</div>;

  return (
    <div className="palette">
      {palette.groups.map(group => (
        <div key={group.id} className="group">
          <h3 style={{ color: group.color }}>
            {group.icon} {group.name}
          </h3>
          <div className="components">
            {group.components.map(type => (
              <ComponentCard
                key={type}
                component={/* fetch visual */}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/component-visual/components` | GET | List all component visuals |
| `/component-visual/components/{type}` | GET | Get specific component visual |
| `/component-visual/palette` | GET | Get component palette |
| `/component-visual/palette/groups` | GET | List all groups |
| `/component-visual/palette/groups/{id}` | GET | Get specific group |
| `/component-visual/favorites` | GET | Get favorites |
| `/component-visual/favorites` | PUT | Update all favorites |
| `/component-visual/favorites/{type}` | POST | Add to favorites |
| `/component-visual/favorites/{type}` | DELETE | Remove from favorites |
| `/component-visual/recent` | GET | Get recently used |
| `/component-visual/recent/{type}` | POST | Record usage |
| `/component-visual/pipelines/{id}` | GET | Get pipeline visual |
| `/component-visual/pipelines/{id}/stages/{sid}/position` | PUT | Update position |
| `/component-visual/pipelines/{id}/viewport` | PUT | Update viewport |
| `/component-visual/connection-style` | GET | Get connection style |
| `/component-visual/categories` | GET | List categories |
| `/component-visual/search` | GET | Search components |
