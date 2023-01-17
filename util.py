from datetime import datetime, timedelta
from typing import List


def repeat_weekly(date: datetime, n: int) -> List[datetime]:
    return [date + timedelta(weeks=i) for i in range(n)]


def next_weekday(day: str) -> datetime:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_index = days.index(day)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return today + timedelta(days=(day_index - today.weekday()) % 7)
