from typing import List
from event import DanceEvent
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def clean_name(name: str) -> str:
    # The dancebreakfasts also include the Month, Year and Weekday.
    # This is just noisy information as we see the date anyway so let's just
    # remove it.
    if name.startswith("Tanzfrühstück"):
        name = "Tanzfrühstück"

    return name


# After a bit of snooping around I found an API call the website makes to get
# the events, so instead of parsing html we can just call the API.
def download_schwebach_events() -> List[DanceEvent]:
    response = requests.get(
        "https://schwebach.at/wp-content/plugins/sieglsolutions_masterPlugin/getData/getEvents.php"
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


# I found another API to download the dancecafe dates. This one is a lot more
# awkward to use as it has to be a post request to download the events.
def download_schwebach_dancecafe() -> List[DanceEvent]:
    url = "https://schwebach.at/wp-content/plugins/sieglsolutions_masterPlugin/getData/getTanzcafeExternEvents.php"

    # NOTE: I have no f*cking idea what this payload is, but let's hope it is
    # static and doesn't change every n days.
    payload = "coursekey=WITCEX%25&daysfuture=63"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    response = requests.post(url, headers=headers, data=payload)
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
                description="Der gemütliche Mittelpunkt zum Tanzen und Entspannen!",
                dancing_school="Schwebach",
                website="https://schwebach.at/tanzcafe/",
            )
        )

    # FIXME: Every week there are two events on thursday, one from 15-18h and
    # one from 18-22:30. Since they have the same name, it would really makes
    # sense to merge them into one.

    return events


def download_schwebach() -> List[DanceEvent]:
    return download_schwebach_events() + download_schwebach_dancecafe()
