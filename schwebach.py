import re
from datetime import date, datetime, timedelta
from typing import List

from event import DanceEvent


def clean_name(name: str) -> str:
    # Many events contain one (or many) of the following things in their name:
    # - The year of the event
    # - The month of the event (in german)
    # - The weekday abbreviation (in german) of the event. eg: "(Sa)"
    # These are just noise for our usage though because we display the date and
    # time anyway.
    name = re.subn(
        r"([0-9]{4}|\([a-zA-Z]{2}\)|Jänner|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)",
        "",
        name,
    )[0].strip()

    # Some events end with the time, which we already have in sepperate fields.
    # The format looks like: `- Nachmittag 15-18 Uhr`
    name = re.subn(
        r" - [A-Za-z]+ \d{2}-\d{2} Uhr$",
        "",
        name,
    )[0].strip()

    # Some events end with "Schwebach Tanzparty" which is also just unecessary
    name = re.subn(
        r" - (Schwebachs )?Tanzparty$",
        "",
        name,
    )[0].strip()

    return name


def get_next_weekday(d: date, weekday: int) -> date:
    """Get the next date for a given weekday (0=Monday, 6=Sunday)"""
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + timedelta(days_ahead)


def generate_tanzcafe_events(start_date: datetime) -> List[DanceEvent]:
    """Generate Tanzcafe events for the next few weeks based on fixed schedule"""
    events = []

    # Schedule mapping: (weekday, start_hour, end_hour)
    afternoon_schedule = [
        (1, 15, 18),  # Tuesday
        (2, 15, 18),  # Wednesday
        (3, 15, 18),  # Thursday
    ]

    evening_schedule = [
        (3, 18, 22.5),  # Thursday
        (4, 17, 22.5),  # Friday
    ]

    # Generate events for the next 4 weeks
    base_date = start_date.date()
    for _ in range(4):  # 4 weeks ahead
        for weekday, start_hour, end_hour in afternoon_schedule + evening_schedule:
            event_date = get_next_weekday(base_date, weekday)

            # Skip if it's before our start date
            if event_date < base_date:
                continue

            starts_at = datetime.combine(
                event_date, datetime.min.time().replace(hour=int(start_hour))
            )
            ends_at = datetime.combine(
                event_date,
                datetime.min.time().replace(
                    hour=int(end_hour), minute=30 if end_hour % 1 else 0
                ),
            )

            price = 1200  # €12
            description = (
                "Voranmeldung erforderlich.\n\n"
                "Der gemütliche Mittelpunkt zum Tanzen und Entspannen!\n\n"
                "Am Nachmittag bis 17:00 Uhr inklusive Kaffee und Kuchen."
            )

            events.append(
                DanceEvent(
                    starts_at=starts_at,
                    ends_at=ends_at,
                    name="Tanzcafe",
                    price_euro_cent=price,
                    description=description,
                    dancing_school="Schwebach",
                    website="https://schwebach.at/tanzcafe/",
                )
            )

        base_date += timedelta(days=7)

    return events


def download_schwebach() -> List[DanceEvent]:
    """Get all Schwebach events - only Tanzcafe for now since they updated their website"""
    now = datetime.now()
    return generate_tanzcafe_events(now)
