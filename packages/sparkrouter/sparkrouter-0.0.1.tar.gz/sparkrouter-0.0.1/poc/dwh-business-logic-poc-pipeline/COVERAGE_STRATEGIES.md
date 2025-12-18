# Coverage Strategies for Containerized Integration Tests

This document outlines multiple strategies for measuring code coverage in our containerized environment where business logic runs in Docker containers.

## 🎯 Coverage Targets

- **Primary Goal**: 80% combined coverage (unit + integration)
- **Integration Focus**: Measure coverage of code paths that run inside containers
- **Business Logic Priority**: Focus on testing business logic that can't be mocked

## 📊 Strategy Overview

### 1. **Host-Based Integration Coverage** ⭐ **(Recommended Start)**

**What**: Tests run on host, connect to containerized services
**Best For**: Service classes, database connections, API interactions
**Coverage**: Measures code executed on the host during integration tests

```bash
# Already implemented in integration-tests.sh
./integration-tests.sh  # Automatically collects coverage
./run-coverage.sh       # Combines unit + integration coverage
```

**Pros**:
- ✅ Easy to implement (already done!)
- ✅ No container modifications needed  
- ✅ Standard Python coverage tools work
- ✅ Combines easily with unit test coverage

**Cons**:
- ❌ Doesn't measure code that only runs inside containers
- ❌ May miss some execution paths

---

### 2. **Container-Instrumented Coverage** 🔧 **(Advanced)**

**What**: Instrument containers to collect coverage when code runs inside them
**Best For**: Jobs that execute entirely within containers
**Coverage**: Measures actual code execution inside containers

```bash
# Enable coverage for containerized execution
export COVERAGE_ENABLED=true

# Run container job with coverage
docker-compose -f docker/docker-compose.yml run --rm \
  -e COVERAGE_ENABLED=true \
  python-submit \
  --module_name dwh.jobs.spark_example.spark_example_job_factory
  
# Coverage data is saved to docker/python-data/.coverage.container
```

**Implementation Status**: ✅ **Already implemented** in `python-submit.sh`

**Pros**:
- ✅ Measures actual container execution
- ✅ Captures code paths unique to containerized environment
- ✅ Real infrastructure interaction coverage

**Cons**:
- ❌ More complex setup
- ❌ Requires container volume mounts for coverage data
- ❌ May impact performance

---

### 3. **Hybrid Coverage Collection** 🔀 **(Best of Both Worlds)**

**What**: Combine host-based + container-instrumented coverage
**Best For**: Comprehensive coverage across all execution environments

```bash
#!/bin/bash
# Enhanced run-coverage.sh (future improvement)

# 1. Run unit tests
python -m coverage run --source=src -m pytest tests/unit/

# 2. Run host-based integration tests  
python -m coverage run --source=src -m pytest tests/integration/

# 3. Run container-instrumented jobs
export COVERAGE_ENABLED=true
docker-compose run python-submit --module_name job1
docker-compose run python-submit --module_name job2

# 4. Combine all coverage data
coverage combine .coverage* docker/python-data/.coverage.*
coverage report
```

---

### 4. **Code Coverage in CI/CD** 🤖 **(Production Ready)**

**What**: Automated coverage collection in continuous integration
**Best For**: Ensuring coverage targets are maintained

```yaml
# .github/workflows/coverage.yml (example)
- name: Run Comprehensive Coverage
  run: |
    ./run-coverage.sh
    
- name: Check Coverage Threshold
  run: |
    COVERAGE=$(coverage report | tail -1 | grep -o '[0-9]*%' | tr -d '%')
    if [ $COVERAGE -lt 80 ]; then
      echo "Coverage $COVERAGE% below 80% threshold"
      exit 1
    fi
```

---

## 🛠 Current Implementation Status

### ✅ **Already Implemented**

1. **Host-Based Integration Coverage**
   - Modified `integration-tests.sh` to collect coverage
   - Enhanced `run-coverage.sh` for combined reporting
   - Generates separate unit, integration, and combined reports

2. **Container Coverage Support**
   - Modified `python-submit.sh` to support coverage collection
   - Uses `COVERAGE_ENABLED` environment variable
   - Saves coverage data to shared volumes

### 🔄 **Next Steps for Maximum Coverage**

1. **Identify Container-Only Code Paths**
   ```bash
   # Run current coverage analysis
   ./run-coverage.sh
   
   # Check htmlcov_combined/index.html for:
   # - Low coverage files
   # - Code paths only hit in containers
   # - Integration-specific logic
   ```

2. **Add Container Coverage Collection**
   ```bash
   # For jobs that need container coverage
   export COVERAGE_ENABLED=true
   
   # Run specific job with coverage
   docker-compose run python-submit --module_name dwh.jobs.revenue_recon.revenue_recon_job_factory
   
   # Collect coverage data
   cp docker/python-data/.coverage.* .
   coverage combine
   ```

3. **Target Specific Coverage Gaps** [[memory:5295908149915017377]]
   - Look for business logic requiring mocking
   - Refactor to pure functions where possible
   - Add integration tests for infrastructure-heavy code

---

## 📈 Coverage Improvement Workflow

### Phase 1: Baseline (Current)
```bash
./run-coverage.sh
# Review combined_coverage.txt for current baseline
```

### Phase 2: Integration Enhancement
```bash
# Add more integration tests for low-coverage areas
# Focus on service classes and job factories
```

### Phase 3: Container Coverage (If Needed)
```bash
# Enable container coverage for specific jobs
export COVERAGE_ENABLED=true
# Run containerized jobs with coverage collection
```

### Phase 4: Business Logic Refactoring [[memory:5295908149915017377]]
```bash
# For any code that can't be tested without mocking:
# 1. Extract pure functions
# 2. Add comprehensive unit tests
# 3. Keep infrastructure code minimal
```

---

## 🎯 **Immediate Action Plan**

1. **Run Current Coverage Analysis**
   ```bash
   ./run-coverage.sh
   ```

2. **Identify Top Coverage Gaps**
   - Check `htmlcov_combined/index.html`
   - Focus on files with <50% coverage
   - Prioritize business logic over infrastructure

3. **Choose Coverage Strategy Based on Gaps**
   - If gaps are in host-testable code → Add more integration tests
   - If gaps are in container-only code → Enable container coverage
   - If gaps are in hard-to-test code → Refactor to pure functions

4. **Monitor Progress Toward 80% Target**
   - Run `./run-coverage.sh` regularly
   - Track improvement over time
   - Document any business logic that needs refactoring

---

## 🔍 **Debugging Coverage Issues**

### Common Issues:
1. **Low Integration Coverage**: Add more integration tests
2. **Container Code Not Measured**: Enable `COVERAGE_ENABLED=true`
3. **Business Logic Untestable**: Refactor to pure functions
4. **Coverage Data Missing**: Check file permissions and volume mounts

### Troubleshooting:
```bash
# Check coverage files
ls -la .coverage*
ls -la docker/python-data/.coverage*

# Verify coverage data
python -m coverage report --show-missing

# Debug container coverage
docker-compose run -e COVERAGE_ENABLED=true python-submit --help
``` 