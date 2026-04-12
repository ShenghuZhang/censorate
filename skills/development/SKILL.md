---
name: code_generation
description: Generate production-ready code, tests, and documentation
---

# Code Generation Skill

## Overview
This skill generates production-ready implementation code including core logic, unit tests, integration tests, and comprehensive documentation for approved design specifications.

## When to Use
- When a requirement enters the "Development" lane
- When code implementation is requested
- After design specifications are approved

## Instructions

### 1. Understand the Design
- Review all design specifications thoroughly
- Understand the architecture and data models
- Identify the tech stack requirements
- Check for existing code patterns to follow

### 2. Generate Core Implementation
Write clean, maintainable code:
- **Follow Conventions**: Use project naming and structure conventions
- **Type Safety**: Include proper type hints/annotations
- **Error Handling**: Implement comprehensive error handling
- **Logging**: Add appropriate logging statements
- **Comments**: Document complex logic (avoid obvious comments)

### 3. Implement Data Access Layer
- **Repository Pattern**: Create data access objects
- **Query Optimization**: Use indexes efficiently
- **Transaction Management**: Handle database transactions properly
- **Caching**: Implement caching where appropriate
- **Connection Pooling**: Manage database connections efficiently

### 4. Implement Business Logic
- **Service Layer**: Create service classes for business logic
- **Validation**: Input validation before processing
- **State Transitions**: Implement state machine logic
- **Business Rules**: Apply business rules correctly

### 5. API Implementation
- **Endpoints**: Create RESTful endpoints as specified
- **Middleware**: Implement authentication, authorization, validation
- **Request Parsing**: Handle request data correctly
- **Response Formatting**: Return consistent response formats
- **Error Responses**: Standardized error responses

### 6. Testing Strategy
Generate comprehensive tests:
- `Unit Tests`: Test individual functions and methods in isolation
- `Integration Tests`: Test interactions between components
- `E2E Tests`: Test critical user flows end-to-end
- `Mock Data`: Create realistic test data fixtures

### 7. Documentation
Generate helpful documentation:
- `Code Comments`: Document complex logic and algorithms
- `README Files`: Component and module documentation
- `API Docs`: Swagger/OpenAPI specifications
- `Type Definitions`: TypeScript/Python type definitions

### 8. Code Quality
Ensure high code quality:
- **Clean Code**: Remove dead code, unused variables
- **DRY Principle**: Don't Repeat Yourself
- **SOLID Principles**: Single responsibility, Open/closed, etc.
- **Performance**: Optimize algorithms and queries
- **Security**: Sanitize inputs, prevent injection attacks

### 9. Best Practices
- Use dependency injection for services
- Implement proper configuration management
- Add comprehensive error handling
- Use async/await patterns appropriately
- Implement proper resource cleanup
- Follow Git workflow best practices

## Output Format

Return results in this JSON structure:

```json
{
  "core_implementation": {
    "files": [
      {
        "path": "relative/path/to/file",
        "content": "file content or reference",
        "language": "python|typescript|sql",
        "purpose": "description"
      }
    ]
  },
  "data_access_layer": {
    "repositories": ["repository names"],
    "migrations": ["migration descriptions"]
  },
  "business_logic": {
    "services": ["service names"],
    "state_machines": ["state machine implementations"]
  },
  "api_implementation": {
    "endpoints": [
      {
        "path": "/api/v1/endpoint",
        "method": "GET|POST|PUT|DELETE",
        "description": "endpoint description"
      }
    ]
  },
  "testing": {
    "unit_tests": {
      "count": number,
      "coverage": "percentage",
      "files": ["test file paths"]
    },
    "integration_tests": {
      "count": number,
      "files": ["test file paths"]
    },
    "e2e_tests": {
      "scenarios": ["scenario descriptions"],
      "files": ["test file paths"]
    }
  },
  "documentation": {
    "readme": "README file content",
    "api_docs": "Swagger/OpenAPI spec",
    "type_definitions": "type definitions"
  },
  "code_quality": {
    "linting_results": "linting report",
    "complexity_metrics": "complexity scores",
    "performance_benchmarks": "performance data"
  },
  "deployment_instructions": {
    "environment_setup": "setup steps",
    "configuration": "required config",
    "build_commands": "build and deploy commands"
  }
}
```

## Available Tools

- `read_existing_code`: Access current codebase
- `check_dependencies`: Verify required libraries/packages
- `generate_tests`: Create test files
- `format_code`: Format code according to standards

## Best Practices

1. Write self-documenting code (docstrings, comments)
2. Use meaningful variable and function names
3. Keep functions small and focused (single responsibility)
4. Handle errors gracefully with proper logging
5. Write tests alongside code (TDD approach)
6. Use version control effectively (small, focused commits)
7. Ensure code is testable and maintainable
8. Follow security best practices (input validation, output encoding)
9. Optimize for performance (lazy loading, caching, pagination)
10. Consider future extensibility and maintainability
