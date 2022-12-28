from event import DanceEvent
from typing import List
import requests
from bs4 import BeautifulSoup
import dateparser


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


def download_rueff() -> List[DanceEvent]:
    events = download_rueff_breakfast()
    return events
