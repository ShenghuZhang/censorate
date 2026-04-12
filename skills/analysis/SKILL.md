---
name: requirement_analysis
description: Analyze requirements, detect duplicates, and provide triage information
---

# Requirement Analysis Skill

## Overview
This skill provides comprehensive requirement analysis including priority assessment, complexity estimation, and duplicate detection using vector search.

## When to Use
- When a requirement enters the "Analysis" lane
- When explicitly requested by a user
- During backlog prioritization

## Instructions

### 1. Analyze the Requirement
- Read the requirement title and description carefully
- Identify key features and components
- Determine technical complexity (1-10 scale)
- Estimate business impact and urgency

### 2. Determine Priority
**High Priority** if:
- Business critical feature
- Security vulnerability or issue
- Blocked other work
- Timeline pressure

**Medium Priority** if:
- Standard feature request
- Enhancement to existing functionality
- Normal timeline

**Low Priority** if:
- Nice-to-have feature
- Minor improvement
- Flexible timeline

### 3. Complexity Assessment
Rate complexity on a 1-10 scale based on:
- Number of components involved
- Integration complexity
- Technical difficulty
- Dependencies on other systems
- Data model changes required

### 4. Required Skills
Identify and list technical skills needed:
- Frontend technologies
- Backend technologies
- Database operations
- Third-party integrations
- Domain knowledge

### 5. Suggested Assignee
Recommend a team member or AI agent for this requirement based on:
- Required skills match
- Current workload
- Past performance on similar tasks
- Domain expertise

### 6. Time Estimation
Provide realistic time estimates:
- Analysis: 1-2 hours
- Design: 2-4 hours (if needed)
- Development: Multiply complexity by 1-5 days
- Testing: 20-50% of development time

### 7. Risk Assessment
Identify potential risks:
- Technical challenges
- Dependencies on external systems
- Knowledge gaps in team
- Integration complexity
- Performance concerns

## Output Format

Return results in this JSON structure:

```json
{
  "priority": "high|medium|low",
  "complexity": 1-10,
  "estimated_days": number,
  "required_skills": ["skill1", "skill2", "..."],
  "suggested_assignee": "username or ai-agent",
  "reasoning": "brief explanation of the assessment",
  "risk_assessment": {
    "technical_complexity": "low|medium|high",
    "dependencies": ["dep1", "dep2"],
    "potential_challenges": ["challenge1", "challenge2"]
  },
  "duplicate_check": {
    "found_duplicates": true|false,
    "similar_requirements": [
      {
        "id": "req-id",
        "req_number": 123,
        "title": "similar title",
        "similarity_score": 0.95
      }
    ]
  }
}
```

## Available Tools

- `search_database`: Search for similar requirements
- `query_ai_knowledge`: Access internal knowledge base
- `check_dependencies`: Analyze requirement dependencies

## Best Practices

1. Be conservative with time estimates - better to under-deliver than over-promise
2. Consider team velocity when estimating
3. Flag requirements that need domain expertise
4. Always provide reasoning for priority decisions
5. Suggest breaking down large requirements (>5 days estimated)
