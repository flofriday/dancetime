from event import DanceEvent
from typing import List
from util import next_weekday, repeat_weekly


# So the website for the dance perfections isn't easily parsable, so the best
# solution for now is to hardcode the events which we can read from the website:
# https://tanzschulewien.at/Perfektionen/
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> List[DanceEvent]:
    events = []

    # Every thursday evening
    thursday = next_weekday("Thu")
    for date in repeat_weekly(thursday, 9):
        events.append(
            DanceEvent(
                starts_at=date.replace(hour=20, minute=00),
                ends_at=date.replace(hour=23, minute=30),
                name="Perfektion",
                description="Abendbeitrag € 5, - / Pers. Offener Tanzabend für alle! Kursteilnahme nicht notwendig.",
                dancing_school="Svabek",
                website="https://tanzschulewien.at/Perfektionen/",
            )
        )
    return events


def download_svabek() -> List[DanceEvent]:
    return create_perfections()
