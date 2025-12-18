# Tests

This directory contains tests for the business logic package.

## Test Types

We have three types of tests:

1. **Unit Tests** (`tests/unit/`)
   - Tests a single component in isolation
   - Uses Noop implementations for dependencies
   - Fast execution, no external dependencies

2. **Functional Tests** (`tests/functional/`)
   - Tests complete features or workflows
   - Uses real implementations where possible
   - May be slower than unit tests

3. **Integration Tests** (`tests/integration/`)
   - Tests interactions between components
   - Uses real implementations or containerized services
   - May require external resources (databases, etc.)

## Test Templates

Each test type has a template file in its directory:

- Unit Test Template: `tests/unit/template.py`
- Functional Test Template: `tests/functional/template.py`
- Integration Test Template: `tests/integration/template.py`

Use these templates when creating new tests to ensure consistency and adherence to our testing standards.

## Critical Testing Standards

Remember these key rules for all test types:

1. **NO MOCKS OR PATCHES**
   - NEVER use Mock, Patch, or monkeypatching in tests
   - Use Noop implementations that implement the same interface

2. **USE REAL IMPLEMENTATIONS OR TEST DOUBLES**
   - For services, use Noop implementations that implement the same interface
   - Noops should be simple, predictable implementations without external dependencies

## Utilities

Common test utilities are available in the `tests/utils/` directory:

- `noop_factory.py`: Base classes for creating Noop implementations