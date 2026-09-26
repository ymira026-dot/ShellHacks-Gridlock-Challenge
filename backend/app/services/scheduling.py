from datetime import date


def overlapping_days(
    start_date_a: date,
    end_date_a: date,
    start_date_b: date,
    end_date_b: date,
) -> int:
    """Return inclusive overlap days, or zero when schedules do not overlap."""
    overlap_start = max(start_date_a, start_date_b)
    overlap_end = min(end_date_a, end_date_b)
    if overlap_start > overlap_end:
        return 0
    return (overlap_end - overlap_start).days + 1


def starts_within_days(
    start_date_a: date,
    start_date_b: date,
    threshold_days: int,
) -> bool:
    """Detect nearby starts even when project date ranges do not overlap."""
    return abs((start_date_a - start_date_b).days) <= threshold_days