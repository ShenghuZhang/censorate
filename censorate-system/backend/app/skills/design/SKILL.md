---
name: design_generation
description: Generate design specifications, wireframes, and UI prototypes
---

# Design Generation Skill

## When to Use
- When a requirement enters the "Design" lane
- When design documentation is requested

## Instructions
Generate comprehensive design specifications including:
1. Architecture recommendations
2. Data model changes
3. API endpoint designs
4. UI/UX wireframes

Output format:
```json
{
  "architecture": "description",
  "data_models": [
    {
      "name": "type",
      "fields": []
    }
  ],
  "api_endpoints": [
    {
      "method": "path",
      "description": ""
    }
  ],
  "ui_wireframes": ["component1", "component2"]
}
```
