from event import DanceEvent
from typing import List
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def clean_name(name: str) -> str:
    # Some names are in all-caps which is just ugly
    if name.isupper():
        name = " ".join([part.capitalize() for part in name.split(" ")])

    # Some names start and end with a double quote for now reason
    if name.startswith('"') and name.endswith('"'):
        name = name[1:-1]

    # And some events should just always be renamed
    rename_table = {
        "Vienna Salsa Splash": "Salsa Splash",
        "Ballsaal LIVE": "Ballsaal Live",
    }

    if name in rename_table:
        name = rename_table[name]

    return name


# For ballsaal.at we need to download and parse html. This is more tedious than
# a JSON API but at least the format is very consistent.
def download_ballsaal() -> List[DanceEvent]:
    response = requests.get("https://www.ballsaal.at/termine_tickets/?no_cache=1")

    soup = BeautifulSoup(response.text, features="html.parser")
    event_items = soup.find_all(class_="event")

    events = []
    for event in event_items:
        name = event.find(class_="name").text
        name = clean_name(name)
        description = event.find(class_="short-description").text
        date_string = event.find(class_="date").text
        url = event.find(class_="button")["href"]

        date = datetime.strptime(date_string[4:], "%d.%m.%Y, %H:%M Uhr")
        events.append(
            DanceEvent(
                starts_at=date,
                name=name,
                description=description,
                dancing_school="Ballsaal",
                website=url,
            )
        )

    return events
