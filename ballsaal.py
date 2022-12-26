from event import DanceEvent
from typing import List
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def download_ballsaal() -> List[DanceEvent]:
    response = requests.get("https://www.ballsaal.at/termine_tickets/?no_cache=1")

    soup = BeautifulSoup(response.text, features="html.parser")
    event_items = soup.find_all(class_="event")

    events = []
    for event in event_items:
        name = event.find(class_="name").text
        description = event.find(class_="short-description").text
        date_string = event.find(class_="date").text
        url = event.find(class_="button")["href"]

        date = datetime.strptime(date_string[4:], "%d.%m.%Y, %H:%M Uhr")
        events.append(
            DanceEvent(
                starts_at=date,
                name=name,
                description=description,
                location="Ballsaal",
                website=url,
            )
        )

    return events
