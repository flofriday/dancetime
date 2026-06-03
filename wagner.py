from datetime import date

import dateparser

from event import DanceEvent
from timeutil import Weekday, weekly_event

WAGNER_WEBSITE = "https://tanzschule-wagner.at/kurse/mehr.html"
WAGNER_DESCRIPTION = (
    "Griechengasse 6 / Fleischmarkt 3-5, 1010 Wien\n"
    "Übungsabend — Mitglieder gratis, externe Gäste €8."
)

# From https://tanzschule-wagner.at/aktuelles/news/ — update when site changes.
CANCELLED_DATES: set[date] = {
    date(2026, 5, 2),
    date(2026, 5, 3),
    date(2026, 5, 16),
    date(2026, 5, 17),
    date(2026, 5, 23),
    date(2026, 5, 24),
}


def _is_summer(d: date) -> bool:
    return d.month in (7, 8, 9)


def _filter_cancelled(events: list[DanceEvent]) -> list[DanceEvent]:
    return [e for e in events if e.starts_at.date() not in CANCELLED_DATES]


def create_winter_season() -> list[DanceEvent]:
    sat = DanceEvent(
        starts_at=dateparser.parse("18:00"),
        ends_at=dateparser.parse("21:00"),
        name="Perfektion",
        price_euro_cent=800,
        description=WAGNER_DESCRIPTION,
        dancing_school="Wagner",
        website=WAGNER_WEBSITE,
    )
    sun = DanceEvent(
        starts_at=dateparser.parse("18:00"),
        ends_at=dateparser.parse("20:00"),
        name="Perfektion",
        price_euro_cent=800,
        description=WAGNER_DESCRIPTION,
        dancing_school="Wagner",
        website=WAGNER_WEBSITE,
    )

    events = []
    for starts in weekly_event(Weekday.SAT, sat) + weekly_event(Weekday.SUN, sun):
        if not _is_summer(starts.starts_at.date()):
            events.append(starts)

    return events


def create_summer_season() -> list[DanceEvent]:
    template = DanceEvent(
        starts_at=dateparser.parse("19:00"),
        ends_at=dateparser.parse("21:00"),
        name="Sommerperfektion",
        price_euro_cent=800,
        description=WAGNER_DESCRIPTION,
        dancing_school="Wagner",
        website="https://tanzschule-wagner.at/sommer/",
    )

    events = []
    for event in weekly_event(Weekday.TUE, template):
        if _is_summer(event.starts_at.date()):
            events.append(event)

    return events


def download_wagner() -> list[DanceEvent]:
    return _filter_cancelled(create_winter_season() + create_summer_season())
