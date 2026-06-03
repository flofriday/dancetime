import dateparser

from event import DanceEvent
from timeutil import Weekday, weekly_event

STANEK_WEBSITE = "https://www.tanzschulestanek.at/about-4"
STANEK_DESCRIPTION = (
    "Grashofgasse 1A, 1010 Wien\nRaum zum Üben und Verbessern in angenehmer Atmosphäre."
)


# https://www.tanzschulestanek.at/about-4
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_open_dance_floor() -> list[DanceEvent]:
    template = DanceEvent(
        starts_at=dateparser.parse("18:30"),
        ends_at=dateparser.parse("20:00"),
        name="Open Dance Floor",
        price_euro_cent=None,
        description=STANEK_DESCRIPTION,
        dancing_school="Stanek",
        website=STANEK_WEBSITE,
    )

    events = []
    for weekday in [Weekday.SUN, Weekday.MON, Weekday.TUE, Weekday.WED, Weekday.THU]:
        events += weekly_event(weekday, template)

    return events


def create_dance_night() -> list[DanceEvent]:
    template = DanceEvent(
        starts_at=dateparser.parse("20:00"),
        ends_at=dateparser.parse("22:30"),
        name="Dance Night",
        price_euro_cent=None,
        description=(
            f"{STANEK_DESCRIPTION}\n"
            "Perfektion / Dance Night mit DJ und Tanzlehrer:innen bei Bedarf."
        ),
        dancing_school="Stanek",
        website="https://www.tanzschulestanek.at/booking-calendar/dance-night-2",
    )

    events = []
    for weekday in [Weekday.FRI, Weekday.SAT]:
        events += weekly_event(weekday, template)

    return events


def download_stanek() -> list[DanceEvent]:
    return create_open_dance_floor() + create_dance_night()
