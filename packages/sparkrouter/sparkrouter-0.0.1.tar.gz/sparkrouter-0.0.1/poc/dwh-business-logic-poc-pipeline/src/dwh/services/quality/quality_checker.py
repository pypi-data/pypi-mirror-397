from abc import ABC, abstractmethod

from dwh.services.quality.quality_models import QualityResult


class QualityChecker(ABC):
    """Abstract base class for job-specific quality checkers."""

    @abstractmethod
    def check(self, metrics: dict) -> QualityResult:
        """
        Run quality checks against job metrics.

        Args:
            metrics: Job metrics dictionary

        Returns:
            QualityResult with overall status and individual checks
        """
        raise NotImplementedError


class NoopQualityChecker(QualityChecker):
    """Quality checker that always returns GREEN. Used for testing or when quality checks are disabled."""

    def check(self, metrics: dict) -> QualityResult:
        return QualityResult.green()
