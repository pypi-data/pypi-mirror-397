# Test Utilities

This directory contains utilities to help with testing.

## Noop Factory

The `noop_factory.py` file provides base classes and helpers for creating Noop implementations that follow our testing standards.

### NoopBase

A base class for Noop implementations that tracks method calls:

```python
from tests.utils.noop_factory import NoopBase

class NoopMyService(MyServiceInterface, NoopBase):
    def service_method(self, arg1, arg2):
        self._record_call('service_method', arg1, arg2)
        return "test_result"
```

### Common Noop Implementations

The module also includes common Noop implementations:

- `NoopDataFrameWrapper`: A simple wrapper that can be used in place of a DataFrame
- `NoopSparkSession`: A Noop implementation of SparkSession for testing

## Test Templates

Test templates have been moved to their respective test type directories:

- Unit Test Template: `tests/unit/template.py`
- Functional Test Template: `tests/functional/template.py`
- Integration Test Template: `tests/integration/template.py`