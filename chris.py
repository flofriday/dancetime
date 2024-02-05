from event import DanceEvent
from typing import Tuple, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import concurrent.futures
from timeutil import Weekday, weekly_event
import re
import dateparser


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
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")

    base_date = datetime.strptime(
        soup.find(class_="news-list-date").text.strip(), "%d.%m.%Y"
    )

    try:
        start_hour, start_minute = parse_time(soup.find(class_="event-starttime").text)
    except Exception:
        # We cannot handle events that don't specify at least a starting time
        return None
    end_hour, end_minute = parse_time(soup.find(class_="event-endtime").text)

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
def download_chris_events() -> list[DanceEvent]:
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


# FIXME: This is hacky and doesn't reflect any changes on the website
# https://www.tanzschulechris.at/perfektionen/tanzcafe_wien_1
def create_perfektions() -> list[DanceEvent]:
    # Every Friday from 20-22h, except on holidays
    return weekly_event(
        Weekday.FRI,
        DanceEvent(
            starts_at=dateparser.parse("20:00"),
            ends_at=dateparser.parse("22:00"),
            name="Perfektion",
            description="Jeden Freitag von 20-22 Uhr spielen wir die beste Tanzmusik für euch: Standard, Latein, Boogie, Latino, West Coast Swing, u.v.m. An unserer Bar verwöhnen euch Nando & Maria Viktoria mit coolen Drinks & den besten Cocktails der Stadt.",
            dancing_school="Chris",
            website="https://www.tanzschulechris.at/perfektionen/tanzcafe_wien_1",
        ),
        exclude_holiday=True,
    )


def download_chris() -> list[DanceEvent]:
    return [e for e in download_chris_events() + create_perfektions() if e is not None]
