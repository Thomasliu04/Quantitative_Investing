from __future__ import annotations

# Fix period iteration: cleaner logic
def iter_report_periods(start_date: str, end_date: str) -> list[str]:
    """Generate quarter-end periods between start_date and end_date (YYYYMMDD)."""
    start_y = int(start_date[:4])
    end_y = int(end_date[:4])
    suffixes = ("0331", "0630", "0930", "1231")
    periods: list[str] = []
    for year in range(start_y - 1, end_y + 1):  # include prior year for lagging fina
        for suffix in suffixes:
            period = f"{year}{suffix}"
            # keep periods that can affect the research window
            if period > end_date:
                continue
            if period < f"{start_y - 1}0331":
                continue
            periods.append(period)
    return periods
