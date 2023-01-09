from event import DanceEvent
from typing import List
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import concurrent.futures


def download_chris_event(url: str) -> DanceEvent:
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")

    base_date = datetime.strptime(
        soup.find(class_="news-list-date").text.strip(), "%d.%m.%Y"
    )

    start_hour, start_minute = (
        soup.find(class_="event-starttime").text.strip().split(":")
    )
    end_hour, end_minute = (
        soup.find(class_="event-endtime").text[2 : (2 + 5)].strip().split(":")
    )

    starts_at = base_date.replace(hour=int(start_hour), minute=int(start_minute))
    ends_at = base_date.replace(hour=int(end_hour), minute=int(end_minute))

    if ends_at < starts_at:
        ends_at += timedelta(days=1)

    return DanceEvent(
        starts_at=starts_at,
        ends_at=ends_at,
        name=soup.select_one(".header > h2:nth-child(1)").text.strip(),
        description=soup.find(class_="news-text-wrap").text.strip(),
        dancing_school="Chris",
        website=url,
    )


# We need to download and parse HTML for chris events. Unfortunatly the
# event overview doesn't have all the events information. So we first
# need to gather the links for each individual event and then download them
# seperatly.
def download_chris_events() -> List[DanceEvent]:
    response = requests.get(
        "https://www.tanzschulechris.at/perfektionen/tanzcafe_wien_1"
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")
    event_items = soup.find_all(class_="news-list-item")

    event_links = [
        "https://www.tanzschulechris.at" + e.find("a")["href"] for e in event_items
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        events = list(executor.map(lambda l: download_chris_event(l), event_links))

    return events


def download_chris() -> List[DanceEvent]:
    return download_chris_events()
