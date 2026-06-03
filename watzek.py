from datetime import date

import dateparser

from event import DanceEvent
from timeutil import Weekday, weekly_event

WATZEK_WEBSITE = "https://www.watzek.at/tanzschule/perfektion.php"
WATZEK_DESCRIPTION = (
    "Palais Palffy, Josefsplatz 6, 1010 Wien\n"
    "Keine Voranmeldung. Betreute Übungszeit für alle Levels."
)
SUNDAY_LAST_DATE = date(2026, 6, 21)
SUNDAY_CANCELLED_DATE = date(2026, 5, 24)


# https://www.watzek.at/tanzschule/perfektion.php
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> list[DanceEvent]:
    template = DanceEvent(
        starts_at=dateparser.parse("17:45"),
        ends_at=dateparser.parse("19:15"),
        name="Perfektion",
        price_euro_cent=500,
        description=WATZEK_DESCRIPTION,
        dancing_school="Watzek",
        website=WATZEK_WEBSITE,
    )

    events = weekly_event(Weekday.MON, template)

    sunday_template = DanceEvent(
        starts_at=dateparser.parse("18:00"),
        ends_at=dateparser.parse("19:30"),
        name="Perfektion",
        price_euro_cent=500,
        description=WATZEK_DESCRIPTION,
        dancing_school="Watzek",
        website=WATZEK_WEBSITE,
    )
    sunday_events = weekly_event(Weekday.SUN, sunday_template)
    events += [
        e
        for e in sunday_events
        if e.starts_at.date() <= SUNDAY_LAST_DATE
        and e.starts_at.date() != SUNDAY_CANCELLED_DATE
    ]

    return events


def download_watzek() -> list[DanceEvent]:
    return create_perfections()
