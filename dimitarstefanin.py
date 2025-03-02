from datetime import time

from event import DanceEvent
from timeutil import Weekday, weekly_event


def create_dance_events() -> list[DanceEvent]:
    events = []

    # Common event time
    start_time = time(19, 0)  # 19:00
    end_time = time(20, 0)  # 20:00

    # Passion Latina - 1st and 3rd Thursday
    events += weekly_event(
        Weekday.THU,
        DanceEvent(
            starts_at=start_time,
            ends_at=end_time,
            name="Passion Latina",
            price_euro_cent=1000,
            description="Fleischmarkt 3-5, 1010 Wien\nTanzvergnügen pur mit Dimitar Stefanin und Alexandra Scheriau. "
            "Intensive einstündige Übungseinheiten mit Fokus auf Latin. "
            "Persönliche Betreuung und individuelles Feedback in 10-minütigen Einheiten.",
            dancing_school="Dimitar Stefanin",
            website="https://dimitarstefanin.com/passion-latina/",
        ),
        weeks_of_month={1, 3},  # First and third week of the month
    )

    # Ballroom Excellence - 2nd and 4th Thursday
    events += weekly_event(
        Weekday.THU,
        DanceEvent(
            starts_at=start_time,
            ends_at=end_time,
            name="Ballroom Excellence",
            price_euro_cent=1000,
            description="Fleischmarkt 3-5, 1010 Wien\nTanzvergnügen pur mit Dimitar Stefanin und Alexandra Scheriau. "
            "Intensive einstündige Übungseinheiten mit Fokus auf Standardtanz. "
            "Persönliche Betreuung und individuelles Feedback in 10-minütigen Einheiten.",
            dancing_school="Dimitar Stefanin",
            website="https://dimitarstefanin.com/ballroom-excellence/",
        ),
        weeks_of_month={2, 4},  # Second and fourth week of the month
    )

    return events


def download_dimitarstefanin() -> list[DanceEvent]:
    return create_dance_events()
