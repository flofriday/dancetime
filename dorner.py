import dateparser

from event import DanceEvent
from timeutil import Weekday, weekly_event


# So the website for the dance perfections isn't easily parsable, so the best
# solution for now is to hardcode the events which we can read from the website:
# https://tanzdorner.at/#perfektion
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> list[DanceEvent]:
    events = []
    # Every friday evening
    for weekday in [Weekday.FRI]:
        events += weekly_event(
            weekday,
            DanceEvent(
                starts_at=dateparser.parse("20:15"),
                ends_at=dateparser.parse("22:15"),
                name="Perfektion",
                price_euro_cent=700,
                description="Favoritenstraße 20, 1040 Wien\nFreitagsperfektion TanzZeit\nIm Dorner Club inkludiert I Dorner Schüler:innen € 5,-- I Gäste € 7,-",
                dancing_school="Dorner",
                website="https://tanzdorner.at/#perfektion",
            ),
        )

    return events


def download_dorner() -> list[DanceEvent]:
    return create_perfections()
