import concurrent.futures
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

import dateparser
import requests
from bs4 import BeautifulSoup

from event import DanceEvent
from timeutil import Weekday, weekly_event


# Parses any string that contains either time in the format
# `15` or `15:34`.
def parse_time(text: str) -> Tuple[int, int]:
    match = re.search(r"(\d{2}):?(\d{2})?", text)
    if match:
        hour, minute = match.groups()
        return int(hour), int(minute or 0)
    else:
        raise ValueError(f"Invalid time format: {text}")


def download_chris_event(url: str) -> Optional[DanceEvent]:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")

    base_date = datetime.strptime(
        soup.find(class_="news-list-date").text.strip(), "%d.%m.%Y"
    )

    try:
        start_hour, start_minute = parse_time(soup.find(class_="event-starttime").text)
        starts_at = base_date.replace(hour=int(start_hour), minute=int(start_minute))
    except Exception:
        # We cannot handle events that don't specify at least a starting time
        return None

    try:
        end_hour, end_minute = parse_time(soup.find(class_="event-endtime").text)
        ends_at = base_date.replace(hour=int(end_hour), minute=int(end_minute))
        if ends_at < starts_at:
            ends_at += timedelta(days=1)
    except AttributeError:
        ends_at = None

    # FIXME: Don't hardcode
    name = soup.select_one(".header > h2:nth-child(1)").text.strip()
    price = 700 if name == "Perfektion" else None

    return DanceEvent(
        starts_at=starts_at,
        ends_at=ends_at,
        name=name,
        price_euro_cent=price,
        description=soup.find(class_="news-text-wrap").text.strip(),
        dancing_school="Chris",
        website=url,
    )


# We need to download and parse HTML for chris events. Unfortunatly the
# event overview doesn't have all the events information. So we first
# need to gather the links for each individual event and then download them
# seperatly.
def download_chris_events() -> list[DanceEvent | None]:
    response = requests.get(
        "https://www.tanzschulechris.at/perfektionen/tanzcafe_wien_1", timeout=10
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")
    event_items = soup.find_all(class_="news-list-item")

    event_links = [
        "https://www.tanzschulechris.at" + e.find("a")["href"] for e in event_items
    ]

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, len(event_links))
    ) as executor:
        events = list(executor.map(download_chris_event, event_links))

    return events


def download_chris() -> list[DanceEvent]:
    return [e for e in download_chris_events() if e is not None]
