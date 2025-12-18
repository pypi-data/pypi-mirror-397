from dataclasses import dataclass, field
from typing import Any


@dataclass
class QualityCheck:
    """Individual quality check result."""
    name: str
    status: str  # GREEN, YELLOW, RED
    value: Any
    threshold: Any = None
    message: str = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "status": self.status,
            "value": float(self.value) if self.value is not None else None,
            "threshold": float(self.threshold) if self.threshold is not None else None,
            "message": self.message
        }


@dataclass
class QualityResult:
    """Aggregated quality check results."""
    status: str  # GREEN, YELLOW, RED (worst of all checks)
    checks: list[QualityCheck] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "checks": [c.to_dict() for c in self.checks]
        }

    @staticmethod
    def green() -> "QualityResult":
        """Create a default GREEN result with no checks."""
        return QualityResult(status="GREEN", checks=[])


class QualityCheckFailedError(Exception):
    """Raised when quality checks fail with RED status."""

    def __init__(self, quality_result: QualityResult):
        self.quality_result = quality_result
        failed_checks = [c for c in quality_result.checks if c.status == "RED"]
        check_names = ", ".join(c.name for c in failed_checks)
        super().__init__(f"Quality check failed: {check_names}")
