---
name: requirement_analysis
description: Analyze requirements, detect duplicates, and provide triage information
---

# Requirement Analysis Skill

## Overview
This skill provides comprehensive requirement analysis including priority assessment, complexity estimation, and duplicate detection.

## When to Use
- When a requirement enters the "Analysis" lane
- When explicitly requested by a user
- During backlog prioritization

## Instructions
1. **Analyze the requirement**:
   - Read the title and description carefully
   - Identify key features and components
   - Estimate complexity (1-10 scale)

2. **Determine priority**:
   - High: Business critical, security issues, major features
   - Medium: Standard features, enhancements
   - Low: Nice-to-have, minor fixes

3. Provide output as JSON:
```json
{
  "priority": "high|medium|low",
  "complexity": 1-10,
  "estimated_days": 7,
  "required_skills": ["skill1", "skill2"],
  "suggested_assignee": "username or null",
  "risk_assessment": {
    "technical_complexity": "low|medium|high",
    "dependencies": ["dependency1", "dependency2"],
    "potential_challenges": ["challenge1"]
  }
}
```

## Available Tools
- search_database: Search for similar requirements
- query_ai_knowledge: Access internal knowledge base
