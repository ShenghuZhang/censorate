---
name: design_generation
description: Generate design specifications, wireframes, and UI prototypes
---

# Design Generation Skill

## Overview
This skill generates comprehensive design specifications including architecture recommendations, data model changes, API endpoint designs, and UI/UX wireframes for approved requirements.

## When to Use
- When a requirement enters the "Design" lane
- When design documentation is explicitly requested
- After requirement analysis is completed

## Instructions

### 1. Understand the Context
- Review the requirement analysis results
- Understand the existing system architecture
- Identify related components and systems
- Check for design system consistency requirements

### 2. Architecture Recommendations
Provide architectural guidance:
- **Component Structure**: Suggest how to organize components
- **State Management**: Recommend state flow
- **Data Flow**: Define data flow between components
- **Integration Points**: Identify integration with existing systems
- **Performance Considerations**: Caching, lazy loading, etc.

### 3. Data Model Design
Design or update data models:
- **Entities**: Define tables/collections needed
- **Relationships**: One-to-one, one-to-many, many-to-many
- **Indexes**: Suggest indexes for performance
- **Constraints**: Data validation rules
- **Migrations**: Suggest migration strategy

### 4. API Endpoint Design
Design RESTful API endpoints:
- **Endpoints**: List all CRUD and action endpoints
- **Request/Response Schemas**: Define data structures
- **Authentication**: Specify auth requirements per endpoint
- **Validation**: Request validation rules
- **Error Handling**: Standard error responses

### 5. UI/UX Wireframes
Create detailed UI specifications:
- **Component Hierarchy**: Break down into reusable components
- **User Flows**: Design user journey flows
- **State Transitions**: Define UI states and transitions
- **Responsive Design**: Mobile, tablet, desktop layouts
- **Accessibility**: ARIA labels, keyboard navigation

### 6. Design System Consistency
Ensure consistency with existing:
- **Typography**: Font sizes, weights, line heights
- **Color Palette**: Use design system colors
- **Spacing**: Maintain consistent spacing scale
- **Components**: Reuse existing component patterns
- **Layouts**: Follow established layout patterns

### 7. Technical Specifications
Provide implementation details:
- **Tech Stack**: Recommend specific technologies/libraries
- **Code Structure**: Suggest file/folder organization
- **Naming Conventions**: File and variable naming
- **Performance**: Optimization suggestions
- **Testing Strategy**: Unit, integration, E2E test plans

## Output Format

Return results in this JSON structure:

```json
{
  "architecture": {
    "overview": "high-level architecture description",
    "components": [
      {
        "name": "ComponentName",
        "purpose": "description",
        "dependencies": ["dep1", "dep2"],
        "tech_stack": ["React", "TypeScript"]
      }
    ],
    "data_flow": "description of data flow"
  },
  "data_models": {
    "new_entities": [
      {
        "name": "EntityName",
        "fields": [
          {
            "name": "fieldName",
            "type": "string|integer|boolean|date|uuid",
            "required": true|false,
            "constraints": "validation rules"
          }
        ],
        "relationships": [
          {
            "from": "Entity",
            "to": "RelatedEntity",
            "type": "one-to-one|one-to-many|many-to-many"
          }
        ]
      }
    ],
    "indexes": ["index1", "index2"],
    "migration_strategy": "description"
  },
  "api_endpoints": [
    {
      "method": "GET|POST|PUT|DELETE",
      "path": "/api/v1/resource",
      "description": "endpoint description",
      "auth_required": true|false,
      "request_schema": {...},
      "response_schema": {...}
    }
  ],
  "ui_wireframes": [
    {
      "component": "ComponentName",
      "purpose": "description",
      "props": {...},
      "states": ["state1", "state2"],
      "user_flow": "step-by-step description"
    }
  ],
  "design_consistency": {
    "follows_system": true,
    "deviations": ["notable deviations if any"],
    "new_patterns": ["new design patterns to follow"]
  },
  "technical_specs": {
    "tech_stack_recommendations": ["library1", "library2"],
    "code_structure": "suggested folder structure",
    "performance_optimizations": ["optimization1", "optimization2"],
    "testing_strategy": "testing approach"
  }
}
```

## Available Tools

- `read_existing_designs`: Access current design documentation
- `check_component_library`: Search for reusable components
- `generate_wireframe`: Create visual wireframe (if tool available)

## Best Practices

1. Follow SOLID principles for component design
2. Use established design system tokens
3. Design mobile-first for responsive layouts
4. Consider progressive enhancement strategy
5. Document design decisions and rationale
6. Include edge cases and error states in designs
7. Ensure accessibility from initial design (WCAG 2.1 AA)
8. Plan for internationalization if applicable
