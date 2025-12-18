# Design Fix: S3 Partition Cleanup Responsibility

## Problem Identified

The `ImageLoader._clean_sink_partitions()` method violated the **Separation of Concerns** principle by directly using boto3 to interact with S3, bypassing the `S3DataSink` abstraction.

### Original Design (INCORRECT)

```python
class ImageLoader:
    def __init__(self, s3_data_sink: S3DataSink, base_s3_path: str):
        self.s3_data_sink = s3_data_sink  # Used for writes
        ...

    def load(self, df: DataFrame):
        # Uses abstraction for writes ✅
        self.s3_data_sink.write_json(df, path, partitions)

        # But directly uses boto3 for cleanup ❌
        self._clean_sink_partitions(path, ...)

    def _clean_sink_partitions(self, ...):
        import boto3  # Direct boto3 usage in business logic!
        s3_client = boto3.client('s3')
        # ... cleanup logic ...
```

### Problems with Original Design

1. **Abstraction Violation**: ImageLoader directly accessed infrastructure (boto3) instead of using the S3DataSink abstraction
2. **Inconsistency**: Writes used abstraction, cleanup didn't
3. **Untestable**: Functional tests couldn't stub the cleanup operation without mocking boto3
4. **Inflexible**: Can't swap S3 implementation (e.g., MinIO, LocalFS) for cleanup

## Design Principle: Abstraction Boundaries

From `DEVELOPMENT_PHILOSOPHY.md`:

> **Factory Pattern & Dependency Injection**
> - Dependencies are injected, never created inside a class
> - Use composition over inheritance
> - Delegate to specialized services rather than implementing everything in one class

The `ImageLoader` should delegate **ALL** S3 operations to the `S3DataSink` abstraction, not just writes.

## Solution Applied

### 1. Extended S3DataSink Interface

Added `clean_partitions()` method to the abstract interface:

```python
class S3DataSink(ABC):
    """Interface for writing data to S3"""

    @abstractmethod
    def write_json(self, df: DataFrame, path: str, partition_by: list[str]) -> list[str]:
        """Write DataFrame to S3 as JSONL with partitioning"""
        pass

    @abstractmethod
    def clean_partitions(self, base_path: str, partition_summary, partition_columns: list[str]) -> int:
        """Delete existing data in target partitions before writing

        Returns:
            Number of objects deleted
        """
        pass
```

### 2. Implemented in SparkS3DataSink

Moved the cleanup logic from `ImageLoader` to `SparkS3DataSink`:

```python
class SparkS3DataSink(S3DataSink):
    """Production implementation using Spark to write to S3"""

    def write_json(self, df: DataFrame, path: str, partition_by: list[str]) -> list[str]:
        # ... existing implementation ...
        pass

    def clean_partitions(self, base_path: str, partition_summary, partition_columns: list[str]) -> int:
        """Delete existing data in target partitions before writing"""
        import boto3
        # ... cleanup logic moved here ...
        return deleted_count
```

**Key change**: boto3 is now encapsulated within the `SparkS3DataSink` implementation, not in business logic.

### 3. Updated ImageLoader to Use Abstraction

```python
class ImageLoader:
    def load(self, df: DataFrame, metrics=None, clean_sink: bool = True) -> None:
        # ... prepare data ...

        # Clean sink partitions if requested - delegate to S3DataSink abstraction
        if clean_sink:
            deleted_count = self.s3_data_sink.clean_partitions(
                output_path,
                partition_summary,
                partition_columns
            )
            print(f"[LOAD] Cleaned {deleted_count} objects from sink partitions")

        # Write data - also uses abstraction
        output_file_paths = self.s3_data_sink.write_json(out_df, output_path, partition_columns)
```

### 4. Updated Test Stub

```python
class StubbedS3DataSink(S3DataSink):
    """Stub for S3DataSink - captures job output."""

    def write_json(self, df: DataFrame, path: str, partition_columns: list = None):
        """Capture written DataFrame."""
        self._written_data = df
        return []

    def clean_partitions(self, base_path: str, partition_summary, partition_columns: list[str]) -> int:
        """Stub for partition cleaning - no-op in tests."""
        print(f"[StubbedS3DataSink] Skipping partition cleanup (stub)")
        return 0
```

## Benefits of Fixed Design

### 1. Proper Abstraction
- **All** S3 operations go through `S3DataSink` interface
- `ImageLoader` has no direct infrastructure dependencies
- Consistent use of abstraction throughout

### 2. Testability
- Functional tests can stub `clean_partitions()` just like `write_json()`
- No boto3 mocking required
- No special `clean_sink=False` workaround needed

### 3. Flexibility
- Easy to implement different backends (MinIO, LocalFS, HDFS)
- Different cleanup strategies per implementation
- Can add monitoring, retry logic, etc. in one place

### 4. Separation of Concerns
- **ImageLoader**: Business logic - what partitions to clean, when to clean
- **S3DataSink**: Infrastructure - how to interact with S3

## Comparison: Before vs After

### Before (VIOLATION)
```
ImageLoader (Business Logic Layer)
  ├── Uses s3_data_sink for writes ✅
  └── Uses boto3 directly for cleanup ❌
      └── boto3.client('s3')  # Direct infrastructure access!
```

### After (CORRECT)
```
ImageLoader (Business Logic Layer)
  └── Uses s3_data_sink for ALL S3 operations ✅
      ├── write_json()
      └── clean_partitions()

SparkS3DataSink (Infrastructure Layer)
  └── Encapsulates boto3 interactions
      ├── write logic
      └── cleanup logic
```

## Alignment with Framework Principles

This fix aligns with multiple framework principles:

### Design for Testability
✅ "All services designed with interfaces that can be implemented by Noops"
- `S3DataSink` is now a complete abstraction for all S3 operations
- Tests can use `StubbedS3DataSink` without any mocking

### Factory Pattern & Dependency Injection
✅ "Dependencies are injected, never created inside a class"
- `ImageLoader` receives `S3DataSink` via constructor
- No direct creation of boto3 clients in business logic

### Separation of Concerns
✅ "Each class has a single responsibility"
- `ImageLoader`: Orchestrate the load pipeline
- `S3DataSink`: Handle S3 interactions

### Explicit Over Implicit
✅ "Prefer explicit parameter passing over global state"
- Cleanup behavior controlled by `clean_sink` parameter
- Clear interface contract in abstract method

## Files Modified

1. **src/dwh/jobs/transform_images/load/image_loader.py**
   - Added `clean_partitions()` to `S3DataSink` abstract class
   - Implemented `clean_partitions()` in `SparkS3DataSink`
   - Removed `_clean_sink_partitions()` from `ImageLoader`
   - Updated `ImageLoader.load()` to use abstraction

2. **tests/functional/dwh/jobs/transform_images/test_transform_image_job.py**
   - Implemented `clean_partitions()` in `StubbedS3DataSink`
   - Removed workaround `clean_sink=False` parameter

## Testing

The functional test now:
1. Uses `clean_sink=True` (production default)
2. Exercises the complete business logic path
3. Stubs infrastructure cleanly without boto3 dependencies

```bash
pytest tests/functional/dwh/jobs/transform_images/test_transform_image_job.py -v
```

## Production Impact

**No behavioral changes to production code**:
- Same cleanup logic, just moved to proper layer
- Same parameters and configuration
- Same error handling and logging

The refactoring is **purely structural** - improving design without changing behavior.

## Lessons Learned

### When to Use Abstractions

If a class has an injected dependency (abstraction), **ALL** operations related to that dependency should go through the abstraction:

❌ **Bad**: Partial use of abstraction
```python
def process(self):
    self.data_sink.write(data)  # Uses abstraction
    boto3.client().delete()     # Bypasses abstraction!
```

✅ **Good**: Complete use of abstraction
```python
def process(self):
    self.data_sink.write(data)    # Uses abstraction
    self.data_sink.cleanup(path)  # Uses abstraction
```

### Design Smell: Direct Import in Business Logic

Any time you see:
```python
import boto3  # or requests, or psycopg2, etc.
```

In a business logic class, ask: "Should this go through an abstraction?"

Usually the answer is YES if:
- The class already has an injected dependency for similar operations
- You want the class to be testable without mocking
- You might need different implementations (prod, test, dev)

## Conclusion

This design fix:
1. Restores proper abstraction boundaries
2. Makes the code more testable
3. Improves flexibility for future changes
4. Aligns with framework principles
5. Maintains all business logic behavior

The refactoring transforms a design violation into a clean, maintainable architecture that follows the framework's core principles.
