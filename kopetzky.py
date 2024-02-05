import dateparser
from event import DanceEvent
from typing import List
from timeutil import Weekday, weekly_event


# So the website for the dance perfections isn't easily parsable, so the best
# solution for now is to hardcode the events which we can read from the website:
# https://kopetzky.at/Perfektion
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> List[DanceEvent]:
    events = []
    # Every saturday and sunday evening
    for weekday in [Weekday.SAT, Weekday.SUN]:
        events += weekly_event(
            weekday,
            DanceEvent(
                starts_at=dateparser.parse("19:30"),
                ends_at=dateparser.parse("21:30"),
                name="Perfektion",
                description="€5,- pro Person\n Offener Tanzabend für alle! Kursteilnahme nicht notwendig.",
                dancing_school="Kopetzky",
                website="https://kopetzky.at/Perfektion",
            ),
        )

    return events


def download_kopetzky() -> List[DanceEvent]:
    return create_perfections()
