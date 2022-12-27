from typing import List
from event import DanceEvent
import requests
from datetime import datetime


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

        # FIXME: the description contains html instead of pure text.
        events.append(
            DanceEvent(
                starts_at=datetime.fromtimestamp(int(item["nc_begin"])),
                name=item["nc_name"],
                description=item["nc_description"],
                location="Schwebach",
                website="https://schwebach.at/events/" + item["webroute"],
            )
        )

    return events
