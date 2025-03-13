#file: backend/utils.py

from datetime import datetime
import pytz
from typing import Dict, Tuple

def get_current_time() -> str:
    """Get current UTC time as a formatted string."""
    return datetime.now(pytz.utc).isoformat()

def adjust_time_range(start: datetime.date, end: datetime.date) -> Tuple[str, str]:
    """Adjust time range to ensure start_date <= end_date."""
    return start, max(start, end)

def available_aggregation_options(start_date: datetime.date, end_date: datetime.date) -> Dict[str, str]:
    """Determine available aggregation options based on date range."""
    days = (end_date - start_date).days
    options = {"Hour": "1h"}
    if days >= 1:
        options["Day"] = "1d"
    if days >= 7:
        options["Week"] = "7d"
    if days >= 30:
        options["Month"] = "30d"
    return options