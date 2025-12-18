# Test Coverage Guide

This guide explains how to run tests with coverage for the DWH Business Logic project.

## Prerequisites

Make sure you have the following packages installed:
- pytest
- pytest-cov

These are already included in the `requirements-dev.txt` file.

## Running Tests with Coverage

### Using the run-coverage.sh Script

We've created a script that makes it easy to run tests with coverage:

```bash
# Run all tests with coverage
./run-coverage.sh

# Run only unit tests with coverage
./run-coverage.sh tests unit

# Run only integration tests with coverage
./run-coverage.sh tests integration

# Run only functional tests with coverage
./run-coverage.sh tests functional
```

### Using WSL (Windows Subsystem for Linux)

As per your project rules, you should use WSL instead of PowerShell:

```bash
# Navigate to your project directory in WSL
wsl cd /mnt/c/Users/j2cla/git/dwh-business-logic-poc/business-logic

# Run the coverage script
wsl ./run-coverage.sh
```

### Manual Commands

If you prefer to run the commands manually:

```bash
# Run all tests with coverage
python -m pytest tests -v --cov=src --cov-report=term --cov-report=html:coverage_html

# Run only unit tests with coverage
python -m pytest tests/unit -v --cov=src --cov-report=term --cov-report=html:coverage_html

# Run only integration tests with coverage
python -m pytest tests/integration -v -m "integration" --cov=src --cov-report=term --cov-report=html:coverage_html

# Run only functional tests with coverage
python -m pytest tests/functional -v -m "functional" --cov=src --cov-report=term --cov-report=html:coverage_html
```

## Coverage Reports

After running the tests with coverage, you'll get:

1. A terminal output showing the coverage percentage for each file
2. An HTML report in the `coverage_html` directory

To view the HTML report, open `coverage_html/index.html` in your web browser.

## Improving Test Coverage

The current test coverage is around 29%. Here are some strategies to improve it:

1. **Focus on Factory Classes**: Many factory classes have 0% coverage. These are typically easy to test.

2. **Test Utility Functions**: Utility classes like `named_parameter_sql.py` should have comprehensive tests.

3. **Service Implementation Tests**: Add tests for service implementations with low coverage.

4. **Test Abstract Classes**: Even though they're abstract, you can test their concrete methods.

5. **Prioritize by Usage**: Focus on testing the most frequently used code paths first.

## Continuous Integration

Consider adding coverage checks to your CI pipeline to ensure coverage doesn't decrease over time:

```yaml
# Example GitHub Actions step
- name: Run tests with coverage
  run: |
    cd business-logic
    ./run-coverage.sh
    
- name: Check coverage threshold
  run: |
    coverage report --fail-under=50
```

This will fail the build if coverage drops below 50% (adjust the threshold as needed).

## Best Practices

1. **Write Tests First**: Consider Test-Driven Development (TDD) for new features.
2. **Test Edge Cases**: Don't just test the happy path; test error conditions too.
3. **Use Mocks Sparingly**: As per your project rules, avoid mocks when possible.
4. **No Fallbacks**: Follow your project rule to throw exceptions rather than creating fallbacks.
5. **Regular Coverage Runs**: Run coverage reports regularly to track progress.