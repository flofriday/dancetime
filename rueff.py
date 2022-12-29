from event import DanceEvent
from typing import List
import requests
from bs4 import BeautifulSoup
import dateparser
from datetime import datetime, timedelta


# Download the next dance breakfast from the website
def download_rueff_breakfast() -> List[DanceEvent]:
    response = requests.get("https://www.tanzschulerueff.at/fruehstueck.htm")

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
        starts_at = dateparser.parse(date_text, languages=["de"])

        events.append(
            DanceEvent(
                starts_at=starts_at,
                name="Tanzfrühstück",
                description="Tanzen und frühstücken am Sonntag in der Tanzschule Rueff!",
                location="Rueff",
                website="https://www.tanzschulerueff.at/fruehstueck.htm",
            )
        )

    return events


def repeat_weekly(date: datetime, n: int) -> List[datetime]:
    return [date + timedelta(weeks=i) for i in range(n)]


def next_weekday(day: str) -> datetime:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day_index = days.index(day)

    today = datetime.today()
    return today + timedelta((day_index - today.weekday()) % 7)


# So the website for the dance perfections isn't easily parsable, so the best
# solution for now is to hardcode the events which we can read from the website:
# https://www.tanzschulerueff.at/perfektionen.htm
# FIXME: yes this whole approach is a bit hacky and means that if the content
# on the website changes we need to change code. Even worse we probably won't
# notice that the website changes.
def create_perfections() -> List[DanceEvent]:
    # Every tuesday evening
    tuesday = next_weekday("Tue")
    tuesday = tuesday.replace(hour=20, minute=45)
    dates = repeat_weekly(tuesday, 9)

    # Every sunday evening
    sunday = next_weekday("Sun")
    sunday = sunday.replace(hour=20, minute=15)
    dates += repeat_weekly(sunday, 9)

    # Every friday afternoon
    friday = next_weekday("Fri")
    friday = friday.replace(hour=16, minute=15)
    dates += repeat_weekly(friday, 9)

    # Now convert the dates to events
    events = [
        DanceEvent(
            starts_at=date,
            name="Perfektion" if date.weekday() != 4 else "Afterwork Perfektion",
            description="Verbringen Sie einen angenehmen, netten Abend in unseren vielseitigen und beliebten Perfektionen und teilen Sie Ihr Tanzhobby mit Gleichgesinnten.",
            location="Rueff",
            website="https://www.tanzschulerueff.at/perfektionen.htm",
        )
        for date in dates
    ]
    return events


def download_rueff() -> List[DanceEvent]:
    events = download_rueff_breakfast()
    events += create_perfections()
    return events
