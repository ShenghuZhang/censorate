---
name: test_generation
description: Generate comprehensive test cases and test execution plans
---

# Test Generation Skill

## Overview
This skill generates comprehensive test suites including unit tests, integration tests, end-to-eend test scenarios, and performance test cases to ensure code quality and system reliability.

## When to Use
- When a requirement enters the "Testing" lane
- When test coverage needs improvement
- During code review or quality assurance

## Instructions

### 1. Analyze the Implementation
- Review the code implementation thoroughly
- Identify critical functionality that needs testing
- Determine test coverage requirements
- Check for edge cases and error conditions

### 2. Generate Unit Tests
Create unit tests for:
- **Functions**: Test individual functions with various inputs
- **Classes**: Test class methods and properties
- **Services**: Test service layer business logic
- **Repositories**: Test data access layer operations
- **Edge Cases**: Include boundary conditions, null values, invalid inputs

### 3. Generate Integration Tests
Create integration tests for:
- **Component Interactions**: Test interactions between services and repositories
- **API Endpoints**: Test API endpoints with realistic data
- **Database Operations**: Test database queries and transactions
- **External Integrations**: Mock external service calls appropriately
- **Error Flows**: Test error handling and recovery scenarios

### 4. Generate E2E Test Scenarios
Create end-to-end test scenarios for:
- **User Flows**: Test complete user journeys (happy path)
- **Error Scenarios**: Test error handling and recovery
- **Performance Scenarios**: Test system under load
- **Security Tests**: Test for common vulnerabilities
- **Accessibility Tests**: Verify WCAG compliance

### 5. Performance Test Cases
Generate performance tests for:
- **Load Testing**: Test system under various load levels
- **Stress Testing**: Identify breaking points
- **Response Time**: Ensure APIs respond within SLA
- **Database Queries**: Optimize and test slow queries
- **Memory Usage**: Monitor memory consumption

### 6. Security Test Cases
Generate security tests for:
- **Input Validation**: Test for XSS, SQL injection, etc.
- **Authentication/Authorization**: Test permission boundaries
- **Data Privacy**: Ensure sensitive data is protected
- **API Security**: Test rate limiting, CORS, CSRF protection
- **Session Management**: Test session hijacking scenarios

### 7. Test Data Management
Create test data fixtures:
- **Realistic Data**: Use realistic test data
- **Edge Cases**: Include unusual but valid data
- **Performance Data**: Large datasets for performance testing
- **Security Test Data**: Malicious inputs for security testing

### 8. Test Organization
Organize tests effectively:
- **Test Structure**: Follow standard test structure
```python
tests/
├── unit/
│   ├── test_services.py
│   ├── test_repositories.py
│   └── test_api.py
├── integration/
│   ├── test_workflows.py
│   └── test_external_integrations.py
└── e2e/
    ├── test_user_flows.py
    └── test_performance.py
```

- **Naming Conventions**: Use clear, descriptive test names
- **Test Independence**: Ensure tests don't depend on each other unnecessarily

### 9. Coverage Goals
Set coverage targets:
- **Unit Tests**: Minimum 80% coverage
- **Integration Tests**: Minimum 70% coverage
- **E2E Tests**: Cover all critical user flows (100%)
- **Line Coverage**: Monitor and report regularly

## Output Format

Return results in this JSON structure:

```json
{
  "unit_tests": {
    "files": [
      {
        "path": "tests/unit/test_module.py",
        "test_count": number,
        "coverage_target": "80%"
      }
    ],
    "total_tests": number,
    "framework": "pytest"
  },
  "integration_tests": {
    "files": [
      {
        "path": "tests/integration/test_workflow.py",
        "test_count": number,
        "coverage_target": "70%"
      }
    ],
    "total_tests": number,
    "framework": "pytest"
  },
  "e2e_tests": {
    "scenarios": [
      {
        "name": "scenario name",
        "description": "detailed description",
        "steps": ["step1", "step2"],
        "test_files": ["test file paths"],
        "coverage_target": "100%"
      }
    ],
    "framework": "playwright"
  },
  "performance_tests": {
    "scenarios": [
      {
        "name": "load test scenario",
        "description": "description",
        "target_load": "1000 req/sec",
        "duration": "5 min"
      }
    ]
  },
  "security_tests": {
    "vulnerability_checks": [
      {
        "type": "XSS|SQL Injection|CSRF",
        "description": "check description",
        "test_files": ["test file paths"]
      }
    ]
  },
  "test_data": {
    "fixtures": ["fixture file paths"],
    "generators": ["test data generators"]
  },
  "coverage_report": {
    "overall_coverage": "percentage",
    "by_module": {
      "module_name": "coverage percentage"
    }
  }
}
```

## Available Tools

- `read_implementation_code`: Access code to generate tests for
- `check_existing_tests`: Identify existing test coverage
- `generate_test_data`: Create test data fixtures
- `run_tests`: Execute tests and capture results

## Best Practices

1. Follow the Arrange-Act-Assert pattern for clear test structure
2. Use descriptive test names that explain what is being tested
3. Test both success and failure scenarios
4. Mock external dependencies appropriately
5. Make tests independent and repeatable
6. Use test fixtures for common test data
7. Parameterize tests for multiple similar scenarios
8. Include edge cases and boundary conditions
9. Test error messages and error codes
10. Clean up test resources in teardown methods
11. Use appropriate assertions (exact match, contains, raises)
12. Organize tests logically and maintain test hierarchy
13. Document complex test scenarios with comments
14. Run tests frequently during development (TDD approach)
15. Maintain high test coverage for critical paths

## Test Coverage Checklist

- [ ] All public API endpoints have tests
- [ ] All service methods have unit tests
- [ ] All repository methods have unit tests
- [ ] Error handling is tested
- [ ] Authentication/authorization is tested
- [ ] Database transactions are tested
- [ ] Input validation is tested
- [ ] Critical user flows have E2E tests
- [ ] Performance requirements are tested
- [ ] Security vulnerabilities are tested
- [ ] Edge cases and error conditions are tested
