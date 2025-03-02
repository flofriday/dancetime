from dataclasses import replace
from datetime import datetime, timedelta
from enum import Enum

from event import DanceEvent
from holiday import holidays


class Weekday(Enum):
    MON = 0
    TUE = 1
    WED = 2
    THU = 3
    FRI = 4
    SAT = 5
    SUN = 6


def remove_events_between(
    start: datetime, end: datetime, events: list[DanceEvent]
) -> list[DanceEvent]:
    return [e for e in events if e.starts_at < start or e.ends_at > end]


def weekly_event(
    day: Weekday,
    template: DanceEvent,
    exclude_holiday=False,
    weeks_of_month: list[int] | int | None = None,
) -> list[DanceEvent]:
    events = []

    for date in repeat_weekly(next_weekday(day), 9):
        if exclude_holiday and date.date() in holidays():
            continue

        # Skip if weeks_of_month is specified and doesn't match
        if weeks_of_month is not None:
            current_week = (date.day - 1) // 7 + 1
            # Handle both list and single integer inputs
            weeks = (
                [weeks_of_month] if isinstance(weeks_of_month, int) else weeks_of_month
            )
            if current_week not in weeks:
                continue

        event = replace(
            template,
            starts_at=date.replace(
                hour=template.starts_at.hour, minute=template.starts_at.minute
            ),
            ends_at=date.replace(
                hour=template.ends_at.hour, minute=template.ends_at.minute
            ),
        )
        events.append(event)

    return events


def repeat_weekly(date: datetime, n: int) -> list[datetime]:
    return [date + timedelta(weeks=i) for i in range(n)]


def next_weekday(day: Weekday) -> datetime:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return today + timedelta(days=(day.value - today.weekday()) % 7)
