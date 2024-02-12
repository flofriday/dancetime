import requests
from bs4 import BeautifulSoup
from dateparser import parse

from event import DanceEvent
from timeutil import Weekday, remove_events_between, weekly_event


# Download the next dance breakfast from the website
def download_rueff_breakfast() -> list[DanceEvent]:
    response = requests.get(
        "https://www.tanzschulerueff.at/fruehstueck.htm", timeout=10
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    select = soup.find("select", {"name": "Auswahl"})
    options = select.find_all("option")

    events = []
    for option in options:
        # Ignore the "Termin auswählen"
        if "termin" in option.text.lower():
            continue

        # The format is: 18.Dezember 2022 / 10:00 - 1300 Uhr
        date_text = option.text
        date_text = date_text.split("-")[0]
        starts_at = parse(date_text, languages=["de"])

        events.append(
            DanceEvent(
                starts_at=starts_at,
                ends_at=starts_at.replace(hour=13, minute=00),
                name="Tanzfrühstück",
                description="Tanzen und frühstücken am Sonntag in der Tanzschule Rueff!",
                dancing_school="Rueff",
                website="https://www.tanzschulerueff.at/fruehstueck.htm",
            )
        )

    return events


# So the website for the dance perfections isn't easily parsable, so the best
# solution for now is to hardcode the events which we can read from the website:
# https://www.tanzschulerueff.at/perfektionen.htm
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> list[DanceEvent]:
    events = []

    # Every tuesday evening
    events += weekly_event(
        Weekday.TUE,
        DanceEvent(
            starts_at=parse("20:45"),
            ends_at=parse("22:15"),
            name="Perfektion",
            description="Verbringen Sie einen angenehmen, netten Abend in unseren vielseitigen und beliebten Perfektionen und teilen Sie Ihr Tanzhobby mit Gleichgesinnten.",
            dancing_school="Rueff",
            website="https://www.tanzschulerueff.at/perfektionen.htm",
        ),
    )

    # Every friday afternoon
    events += weekly_event(
        Weekday.FRI,
        DanceEvent(
            starts_at=parse("16:15"),
            ends_at=parse("17:34"),
            name="Afterwork Perfektion",
            description="Verbringen Sie einen angenehmen, netten Abend in unseren vielseitigen und beliebten Perfektionen und teilen Sie Ihr Tanzhobby mit Gleichgesinnten.",
            dancing_school="Rueff",
            website="https://www.tanzschulerueff.at/perfektionen.htm",
        ),
    )

    # Every sunday evening
    events += weekly_event(
        Weekday.SUN,
        DanceEvent(
            starts_at=parse("20:15"),
            ends_at=parse("21:45"),
            name="Perfektion",
            description="Verbringen Sie einen angenehmen, netten Abend in unseren vielseitigen und beliebten Perfektionen und teilen Sie Ihr Tanzhobby mit Gleichgesinnten.",
            dancing_school="Rueff",
            website="https://www.tanzschulerueff.at/perfektionen.htm",
        ),
    )

    # Special timeslot for semester holidays 2024
    events = remove_events_between(
        parse("2024-02-05 00:00"), parse("2024-02-11 23:59"), events
    )
    semester_perfections = [
        ("2024-02-05 19:30", "2024-02-05 22:00"),
        ("2024-02-06 20:45", "2024-02-06 22:15"),
        ("2024-02-07 19:30", "2024-02-07 22:00"),
        ("2024-02-08 19:30", "2024-02-08 22:00"),
        ("2024-02-09 19:30", "2024-02-09 22:00"),
    ]
    for starts_at, ends_at in semester_perfections:
        events.append(
            DanceEvent(
                starts_at=parse(starts_at),
                ends_at=parse(ends_at),
                name="Perfektion",
                description="Verbringen Sie einen angenehmen, netten Abend in unseren vielseitigen und beliebten Perfektionen und teilen Sie Ihr Tanzhobby mit Gleichgesinnten.",
                dancing_school="Rueff",
                website="https://www.tanzschulerueff.at/perfektionen.htm",
            )
        )

    return events


def download_rueff() -> list[DanceEvent]:
    return download_rueff_breakfast() + create_perfections()
