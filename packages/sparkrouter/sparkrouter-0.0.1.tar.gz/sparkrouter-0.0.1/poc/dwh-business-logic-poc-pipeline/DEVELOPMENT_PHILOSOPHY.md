# DWH Business Logic Development Philosophy

## Core Principles

This document outlines the fundamental development philosophy that guides all aspects of the DWH Business Logic framework. These principles are derived from our critical standards, testing practices, and architectural decisions that have proven essential for building reliable, maintainable data processing systems.

---

## 🎯 **Business Logic is Sacred**

### The Prime Directive
**Business logic is the highest priority and must never be compromised for technical convenience.**

- Business logic components are NEVER mocked, simplified, or removed to make tests pass
- Tests must be adapted to work with business logic, not the other way around
- If business logic is hard to test, refactor the architecture to make it more testable
- Implementation must match documented business specifications exactly

### Schema-Centric Design
**EVERYTHING revolves around schemas - schema functionality and testing is paramount to the entire framework.**

- All data operations must validate against schemas
- Schema services are the foundation of all business logic
- Schema validation failures must be explicit and actionable
- Tests MUST use actual production DDL files, never test-specific overrides

---

## 🏗️ **Architectural Excellence**

### Factory Pattern & Dependency Injection
- Use factory patterns for creating complex objects
- Factories handle configuration and dependency injection
- Dependencies are injected, never created inside a class
- Example: `DataSourceStrategyFactory.create_data_source_strategy(config)`

### Design for Testability
- All services designed with interfaces that can be implemented by Noops
- No static methods that can't be overridden in tests
- No static class usage for services (DDLFileReader, TableRegistry must be instances)
- Create proper abstractions that allow for proper test doubles

### Separation of Concerns
- Each class has a single responsibility
- Use composition over inheritance
- Delegate to specialized services rather than implementing everything in one class

### Explicit Over Implicit
- Prefer explicit parameter passing over global state
- Avoid hidden side effects
- Document all assumptions and requirements

---

## 🔒 **Fail-Fast Philosophy**

### No Fallbacks or Defensive Programming
- If something is not working, throw an exception
- Do not create fallbacks, default behaviors, or fallback values
- Make failures explicit so underlying issues can be fixed
- If a dependency is required, make it required and fail fast if not provided

### Precise Parameters Required
- Kwargs are ONLY allowed in abstract classes and factories
- Concrete implementations MUST use precise, named parameters
- Method parameters and return types must be type-annotated
- Variables are expected, they can never be set to default values
- Do not check for null or provide default values

### No Stubbed Implementations
- Stubbed or incomplete methods must raise NotImplementedError
- Do not leave TODO comments or empty method bodies
- Include descriptive error messages explaining what needs to be implemented

---

## 🧪 **Testing Philosophy**

### Three-Tier Testing Strategy

#### Unit Tests - Isolated Component Testing
- Test individual components in complete isolation
- Use Noop implementations for ALL dependencies
- Focus on component logic, validation, and error handling
- Should be fast and require no external resources

#### Functional Tests - Business Logic Testing
- Test complete business workflows with real processing logic
- **NEVER mock, stub, or replace business logic**
- Use real DDL schema services with actual DDL files
- Test complete end-to-end business workflows
- Exercise all business logic components in sequence

#### Integration Tests - System Interaction Testing
- Test interactions between multiple real components via Docker containers
- Use real implementations where possible, Noop only for external systems
- Test actual system integration points
- No local Spark sessions - complete Docker isolation required

### Test Doubles Philosophy
**Test doubles should simulate external dependencies, not business logic validation.**

#### What to Preserve (NEVER Mock)
- All validation and business constraint logic
- Configuration validation, parameter validation, business rules
- Transformation logic, data quality rules, schema enforcement
- Job orchestration and workflow logic

#### What to Simulate (Backend I/O Only)
- Data storage (S3, databases, file systems)
- Notification services (email, SMS, alerts)
- External APIs and web services
- Network operations

#### Examples
- ✅ NoopDatabaseConnection - simulates database I/O but validates SQL syntax
- ✅ NoopFileWriter - simulates file writing but validates file paths and permissions
- ❌ NoopFactory - bypasses all validation and accepts any configuration
- ❌ NoopValidator - always returns "valid" without checking business rules

### Schema Validation Standards
- Tests MUST use actual production DDL files
- Schema changes must break tests if business logic doesn't handle them
- Test data generators must conform to real schemas
- Any schema modification in tests indicates architectural problems

---

## 📊 **Data Standards**

### Absolute Strictness Required
**These data processing standards are NON-NEGOTIABLE and must be followed by all components.**

### Parquet File Standards
- **PyArrow for test data generation** - Integration test data MUST be generated using PyArrow
- **Microsecond timestamp precision** - ALL timestamps MUST use microsecond precision
- **Native parquet structures** - Complex nested types MUST be native parquet structures

### Schema Enforcement
- **Strict schema validation** - ALL data reads MUST enforce exact schema match
- **Fail-fast on violations** - ANY schema mismatch MUST cause immediate failure
- **No schema inference** - NO schema inference or best-effort parsing
- **No silent conversions** - NO silent type conversions

### Data Quality Philosophy
- **Fix process, not tests** - When tests fail due to data issues, fix business logic
- **Never weaken validation** - Don't accommodate broken processes
- **Comprehensive output validation** - Validate output data matches expected schemas exactly

---

## 🔧 **Configuration Management**

### Production Configuration is Sacred
- Production configuration files must NEVER be modified for testing needs
- These files define production requirements and must remain pure
- Integration tests must adapt to production configurations, not vice versa
- Changes to production configurations driven by production requirements only

### Test Adaptation Principle
- Integration tests must work with production configurations as-is
- If tests cannot work with production settings, the test design is flawed
- Tests should validate that production configurations work correctly

---

## 🔄 **Refactoring Standards**

### Complete Refactoring
- When refactoring, ALWAYS remove old code, files, and approaches
- Never leave both old and new implementations in the codebase
- Clean up all artifacts of the previous approach

### Maintain Consistency
- Ensure refactored code follows the same patterns as the rest of the codebase
- Update all related components to work with refactored code
- Don't leave parts of the system using the old approach

### Preserve Behavior
- Refactoring should change structure without changing behavior
- Ensure all tests pass after refactoring
- Document any intentional behavior changes separately

---

## 📝 **Documentation Standards**

### Maintain Application Context
- Keep application context up to date as changes are made
- Capture design decisions from conversations in appropriate documentation
- Update README files and architecture documents when designs evolve

### Document Design Decisions
- Record reasoning behind significant design choices
- Include alternatives considered and why they were rejected
- Document trade-offs and constraints that influenced the design

### Code-Adjacent Documentation
- Place documentation close to the code it describes
- Update class and method documentation when implementation changes
- Ensure examples in documentation match current implementation

---

## 📈 **Coverage & Quality Standards**

### Coverage Targets
- **Primary Goal**: 80% combined coverage (unit + functional)
- **Integration Focus**: Measure coverage of code paths in containers
- **Business Logic Priority**: Focus on testing business logic that can't be mocked

### Coverage Strategy
- **Host-Based Integration Coverage**: Tests run on host, connect to containerized services
- **Container-Instrumented Coverage**: Instrument containers to collect coverage
- **Hybrid Collection**: Combine both approaches for comprehensive coverage

### Quality Metrics
- **Schema Drift Detection**: 95% confidence in catching schema evolution issues
- **Business Logic Validation**: 95% confidence in business logic correctness
- **Production Readiness**: Comprehensive validation prevents production surprises

---

## 🚀 **Development Workflow**

### Test-Driven Development
- Write tests first for new features
- Use tests to isolate and reproduce issues
- Add tests to prevent regression
- This approach improves coverage while solving real problems

### Debugging Approach
- When encountering problems, write focused tests that isolate the issue
- Use tests to verify fixes work correctly
- Maintain tests in the suite to prevent regression

### Code Review Standards
- ANY pandas parquet I/O in integration tests MUST be rejected
- ANY pre-generated static test files MUST be rejected
- ANY schema validation bypasses MUST be rejected
- ANY fallback logic for complex types MUST be rejected

---

## 🎯 **Success Metrics**

### Technical Excellence
- **95% Schema Drift Detection**: Catch schema evolution issues before production
- **90% Business Logic Coverage**: Comprehensive testing of transformation logic
- **85% Error Handling Coverage**: Business logic error scenarios validated
- **80% Combined Coverage**: Unit + integration test coverage target

### Operational Excellence
- **Zero Production Surprises**: Comprehensive testing prevents deployment issues
- **Fast Feedback Loops**: Tests provide immediate feedback on changes
- **Maintainable Codebase**: Clear separation of concerns and explicit interfaces
- **Reliable Deployments**: Production configurations validated through testing

---

## 🔍 **Philosophy in Practice**

### What This Means for Daily Development

1. **When Writing Code**:
   - Design for testability from the start
   - Use dependency injection and factory patterns
   - Validate against real schemas
   - Fail fast on invalid inputs

2. **When Writing Tests**:
   - Never mock business logic
   - Use real DDL files and schema validation
   - Test complete workflows end-to-end
   - Focus on business outcomes, not implementation details

3. **When Refactoring**:
   - Remove old code completely
   - Maintain all existing tests
   - Update documentation
   - Preserve business behavior exactly

4. **When Debugging**:
   - Write tests that reproduce the issue
   - Fix the root cause, not symptoms
   - Add regression tests
   - Update documentation if needed

### What This Philosophy Prevents

- **Production Surprises**: Comprehensive testing catches issues early
- **Schema Drift**: Real DDL validation prevents compatibility issues
- **Technical Debt**: Complete refactoring prevents code accumulation
- **False Confidence**: Real business logic testing validates actual behavior
- **Configuration Drift**: Production configuration protection maintains consistency

---

## 📚 **Conclusion**

This development philosophy represents lessons learned from building reliable data processing systems. It prioritizes business logic correctness, comprehensive testing, and operational excellence over technical convenience.

**The core message**: Build systems that work reliably in production by testing them comprehensively during development, never compromising business logic for technical convenience, and maintaining the highest standards for code quality and documentation.

Every decision should be evaluated against these principles. When in doubt, choose the approach that:
1. Preserves business logic integrity
2. Provides comprehensive test coverage
3. Fails fast on invalid inputs
4. Maintains production configuration purity
5. Documents decisions clearly

This philosophy has proven essential for building data systems that teams can trust, maintain, and evolve with confidence.

---

**Last Updated**: 2025-01-08  
**Next Review**: When significant architectural decisions are made