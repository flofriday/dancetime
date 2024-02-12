import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from event import DanceEvent


def clean_name(name: str) -> str:
    # Many events contain one (or many) of the following things in their name:
    # - The year of the event
    # - The month of the event (in german)
    # - The weekday abbreviation (in german) of the event. eg: "(Sa)"
    # These are just noise for our usage though because we display the date and
    # time anyway.
    name = re.subn(
        r"([0-9]{4}|\([a-zA-Z]{2}\)|Jänner|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)",
        "",
        name,
    )[0].strip()

    if name.endswith(" - Schwebachs Tanzparty"):
        name = name.removesuffix(" - Schwebachs Tanzparty")

    return name


# After a bit of snooping around I found an API call the website makes to get
# the events, so instead of parsing html we can just call the API.
def download_schwebach_events() -> list[DanceEvent]:
    response = requests.get(
        "https://schwebach.at/wp-content/plugins/sieglsolutions_masterPlugin/getData/getEvents.php",
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    events = []
    for item in data["cdata"]["events"]:
        # Filter events that are not in Vienna
        if item["location_bez"] != "Wien":
            continue

        # Ceanup the name
        name = clean_name(item["nc_name"])

        # The description is in html so let's convert it to text.
        description = item["nc_shortDescription"]
        if description == "":
            description = BeautifulSoup(
                item["nc_description"], features="html.parser"
            ).text

        events.append(
            DanceEvent(
                starts_at=datetime.fromtimestamp(int(item["nc_begin"])),
                ends_at=datetime.fromtimestamp(int(item["nc_end"])),
                name=name,
                description=description.strip(),
                dancing_school="Schwebach",
                website="https://schwebach.at/events/" + item["webroute"],
            )
        )

    return events


# Every week there are two events on thursday, one from 15-18h and
# one from 18-22:30. Since they have the same name, it would really makes
# sense to merge them into one.
def merge_events(events: list[DanceEvent]) -> list[DanceEvent]:
    if len(events) == 0:
        return []

    events = sorted(events, key=lambda e: e.starts_at)

    merged_events = events[:1]
    for event in events[1:]:
        last_event = merged_events[-1]
        if event.name == last_event.name and event.starts_at <= last_event.ends_at:
            last_event.ends_at = max(event.ends_at, last_event.ends_at)
        else:
            merged_events.append(event)

    return merged_events


# I found another API to download the dancecafe dates. This one is a lot more
# awkward to use as it has to be a post request to download the events.
def download_schwebach_dancecafe() -> list[DanceEvent]:
    url = "https://schwebach.at/wp-content/plugins/sieglsolutions_masterPlugin/getData/getTanzcafeExternEvents.php"

    # NOTE: I have no f*cking idea what this payload is, but let's hope it is
    # static and doesn't change every n days.
    payload = "coursekey=WITCEX%25&daysfuture=63"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    response = requests.post(url, headers=headers, data=payload, timeout=10)
    response.raise_for_status()
    data = response.json()

    events = []
    for item in data["cdata"]["courses"][0]:
        # Filter events that are not in Vienna
        if item["standort_longname"] != "Wien":
            continue

        # Create the name and append "ausgebucht" if it is already full.
        # However, we still show it because suddenly disappearing items might
        # be confusing.
        name = item["nc_displayName"]
        if int(item["nc_isFull"]) == 1:
            name += " [ausgebucht]"

        events.append(
            DanceEvent(
                starts_at=datetime.fromtimestamp(int(item["nc_start_timeU"])),
                ends_at=datetime.fromtimestamp(int(item["nc_end_timeU"])),
                name=name,
                description="€12,- pro Person\nVoranmeldung erforderlich.\n\nDer gemütliche Mittelpunkt zum Tanzen und Entspannen!",
                dancing_school="Schwebach",
                website="https://schwebach.at/tanzcafe/",
            )
        )

    # Some events are kinda duplicated in their API so we merge them together.
    events = merge_events(events)
    return events


def download_schwebach() -> list[DanceEvent]:
    return download_schwebach_events() + download_schwebach_dancecafe()
