import dateparser

from event import DanceEvent
from timeutil import Weekday, weekly_event

KOPETZKY_WEBSITE = "https://kopetzky.at/Perfektion"
KOPETZKY_DESCRIPTION = (
    "Neubaugasse 7/9, 1070 Wien\n"
    "Offener Tanzabend für alle! Kursteilnahme nicht notwendig.\n"
    "Gratis für Kursteilnehmer der Tanzschule Kopetzky."
)


# https://kopetzky.at/Perfektion
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> list[DanceEvent]:
    events = []
    for weekday in [Weekday.SAT, Weekday.SUN]:
        events += weekly_event(
            weekday,
            DanceEvent(
                starts_at=dateparser.parse("19:30"),
                ends_at=dateparser.parse("21:30"),
                name="Perfektion",
                price_euro_cent=600,
                description=KOPETZKY_DESCRIPTION,
                dancing_school="Kopetzky",
                website=KOPETZKY_WEBSITE,
            ),
        )

    return events


def download_kopetzky() -> list[DanceEvent]:
    return create_perfections()
