import dateparser

from event import DanceEvent
from timeutil import Weekday, remove_events_between, weekly_event


# https://www.tanzschule-strobl.at/perfektion.html
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> list[DanceEvent]:
    events = []

    # Every sunday evening
    events += weekly_event(
        Weekday.SUN,
        DanceEvent(
            starts_at=dateparser.parse("19:00"),
            ends_at=dateparser.parse("21:30"),
            name="Perfektion",
            description="€ 5.50 pro Person - keine Anmeldung erforderlich.",
            dancing_school="Strobl",
            website="https://www.tanzschule-strobl.at/perfektion.html",
        ),
    )

    events += weekly_event(
        Weekday.WED,
        DanceEvent(
            starts_at=dateparser.parse("20:00"),
            ends_at=dateparser.parse("22:00"),
            name="Perfektion mit Karina",
            description="€ 5.50 pro Person - keine Anmeldung erforderlich.",
            dancing_school="Strobl",
            website="https://www.tanzschule-strobl.at/perfektion.html",
        ),
    )

    # No events in the semester holidays
    events = remove_events_between(
        dateparser.parse("2024-02-04 00:00"),
        dateparser.parse("2024-02-11 23:59"),
        events,
    )

    return events


def download_strobl() -> list[DanceEvent]:
    return create_perfections()
