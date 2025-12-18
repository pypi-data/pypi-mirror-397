from dwh.services.quality.quality_checker import QualityChecker
from dwh.services.quality.quality_models import QualityCheck, QualityResult


class TransformImagesQualityChecker(QualityChecker):
    """Quality checker for transform_images job."""

    def __init__(
        self,
        drop_rate_yellow: float = 0.05,
        drop_rate_red: float = 0.10,
        min_records: int = 0
    ):
        self.drop_rate_yellow = drop_rate_yellow
        self.drop_rate_red = drop_rate_red
        self.min_records = min_records

    def check(self, metrics: dict) -> QualityResult:
        """
        Run quality checks for transform_images job.

        Checks:
        - drop_rate: Percentage of records dropped during processing
        - min_records: Minimum number of records written

        Args:
            metrics: Job metrics dictionary with records_read, records_dropped, records_written

        Returns:
            QualityResult with overall status and individual checks
        """
        checks = []

        # Drop rate check
        records_read = metrics.get("records_read", 0)
        records_dropped = metrics.get("records_dropped", 0)
        drop_rate = records_dropped / records_read if records_read > 0 else 0

        if drop_rate >= self.drop_rate_red:
            checks.append(QualityCheck(
                name="drop_rate",
                status="RED",
                value=round(drop_rate, 4),
                threshold=self.drop_rate_red,
                message=f"Drop rate {drop_rate:.1%} exceeds threshold {self.drop_rate_red:.1%}"
            ))
        elif drop_rate >= self.drop_rate_yellow:
            checks.append(QualityCheck(
                name="drop_rate",
                status="YELLOW",
                value=round(drop_rate, 4),
                threshold=self.drop_rate_yellow,
                message=f"Drop rate {drop_rate:.1%} exceeds warning threshold {self.drop_rate_yellow:.1%}"
            ))
        else:
            checks.append(QualityCheck(
                name="drop_rate",
                status="GREEN",
                value=round(drop_rate, 4),
                threshold=self.drop_rate_yellow
            ))

        # Minimum records check
        records_written = metrics.get("records_written", 0)
        if self.min_records > 0 and records_written < self.min_records:
            checks.append(QualityCheck(
                name="min_records",
                status="RED",
                value=records_written,
                threshold=self.min_records,
                message=f"Records written {records_written:,} below minimum {self.min_records:,}"
            ))
        else:
            checks.append(QualityCheck(
                name="min_records",
                status="GREEN",
                value=records_written,
                threshold=self.min_records
            ))

        # Determine overall status (worst of all checks)
        overall = "GREEN"
        if any(c.status == "YELLOW" for c in checks):
            overall = "YELLOW"
        if any(c.status == "RED" for c in checks):
            overall = "RED"

        return QualityResult(status=overall, checks=checks)
