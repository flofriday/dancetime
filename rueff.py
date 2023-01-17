from event import DanceEvent
from typing import List
import requests
from bs4 import BeautifulSoup
import dateparser
from util import repeat_weekly, next_weekday


# Download the next dance breakfast from the website
def download_rueff_breakfast() -> List[DanceEvent]:
    response = requests.get("https://www.tanzschulerueff.at/fruehstueck.htm")
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
        starts_at = dateparser.parse(date_text, languages=["de"])

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
def create_perfections() -> List[DanceEvent]:
    events = []

    # Every tuesday evening
    tuesday = next_weekday("Tue")
    for date in repeat_weekly(tuesday, 9):
        events.append(
            DanceEvent(
                starts_at=date.replace(hour=20, minute=45),
                ends_at=date.replace(hour=22, minute=15),
                name="Perfektion",
                description="Verbringen Sie einen angenehmen, netten Abend in unseren vielseitigen und beliebten Perfektionen und teilen Sie Ihr Tanzhobby mit Gleichgesinnten.",
                dancing_school="Rueff",
                website="https://www.tanzschulerueff.at/perfektionen.htm",
            )
        )

    # Every sunday evening
    sunday = next_weekday("Sun")
    for date in repeat_weekly(sunday, 9):
        events.append(
            DanceEvent(
                starts_at=date.replace(hour=20, minute=15),
                ends_at=date.replace(hour=21, minute=45),
                name="Perfektion",
                description="Verbringen Sie einen angenehmen, netten Abend in unseren vielseitigen und beliebten Perfektionen und teilen Sie Ihr Tanzhobby mit Gleichgesinnten.",
                dancing_school="Rueff",
                website="https://www.tanzschulerueff.at/perfektionen.htm",
            )
        )

    # Every friday afternoon
    friday = next_weekday("Fri")
    for date in repeat_weekly(friday, 9):
        events.append(
            DanceEvent(
                starts_at=date.replace(hour=16, minute=15),
                ends_at=date.replace(hour=17, minute=45),
                name="Afterwork Perfektion",
                description="Verbringen Sie einen angenehmen, netten Abend in unseren vielseitigen und beliebten Perfektionen und teilen Sie Ihr Tanzhobby mit Gleichgesinnten.",
                dancing_school="Rueff",
                website="https://www.tanzschulerueff.at/perfektionen.htm",
            )
        )

    return events


def download_rueff() -> List[DanceEvent]:
    return download_rueff_breakfast() + create_perfections()
