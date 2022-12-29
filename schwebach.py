from typing import List
from event import DanceEvent
from datetime import datetime
import requests
from bs4 import BeautifulSoup


# After a bit of snooping around I found an API call the website makes to get
# the events, so instead of parsing html we can just call the API.
def download_schwebach() -> List[DanceEvent]:
    response = requests.get(
        "https://schwebach.at/wp-content/plugins/sieglsolutions_masterPlugin/getData/getEvents.php"
    )
    data = response.json()

    events = []
    for item in data["cdata"]["events"]:
        # Filter events that are not in Vienna
        if item["location_bez"] != "Wien":
            continue

        # The description is in html so let's convert it to text.
        description = BeautifulSoup(item["nc_description"], features="html.parser").text

        # FIXME: the description contains html instead of pure text.
        events.append(
            DanceEvent(
                starts_at=datetime.fromtimestamp(int(item["nc_begin"])),
                name=item["nc_name"],
                description=description,
                location="Schwebach",
                website="https://schwebach.at/events/" + item["webroute"],
            )
        )

    return events
