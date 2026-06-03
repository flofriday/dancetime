from datetime import date

import dateparser

from event import DanceEvent
from timeutil import Weekday, weekly_event

STROBL_WEBSITE = "https://www.tanzschule-strobl.at/perfektion.html"
STROBL_DESCRIPTION = "keine Anmeldung erforderlich."

# From https://www.tanzschule-strobl.at/perfektion.html — update when site changes.
SUNDAY_CANCELLED_DATE = date(2026, 5, 24)


# https://www.tanzschule-strobl.at/perfektion.html
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> list[DanceEvent]:
    template = DanceEvent(
        starts_at=dateparser.parse("19:00"),
        ends_at=dateparser.parse("21:30"),
        name="Perfektion",
        price_euro_cent=600,
        description=STROBL_DESCRIPTION,
        dancing_school="Strobl",
        website=STROBL_WEBSITE,
    )

    sunday_events = weekly_event(Weekday.SUN, template)
    events = [e for e in sunday_events if e.starts_at.date() != SUNDAY_CANCELLED_DATE]

    events += weekly_event(
        Weekday.WED,
        DanceEvent(
            starts_at=dateparser.parse("20:00"),
            ends_at=dateparser.parse("22:00"),
            name="Perfektion mit Karina",
            price_euro_cent=600,
            description=STROBL_DESCRIPTION,
            dancing_school="Strobl",
            website=STROBL_WEBSITE,
        ),
    )

    return events


def download_strobl() -> list[DanceEvent]:
    return create_perfections()
