from typing import List
from event import DanceEvent
from datetime import datetime
import requests


# Well, we couldn't really find any API and the Website itself seams a little
# janky to parse. But luckily there is the calendar which gets it's events from
# the server via json. So let's just pretend we are a weird calendar and we
# need some events.
def download_stanek() -> List[DanceEvent]:
    # FIXME calculate dates
    response = requests.get(
        "https://tanzschulestanek.at/wp-content/plugins/ts_kurse/api/ts_kalender.php?start=2022-12-30&end=2023-02-28&kategorie=&cache=0.9797512370776541"
    )
    data = response.json()

    # FIXME: We need to investigate if to where events really link.
    # At the time of writing there is only one event(party) that has an empty
    # link.
    allowed_urls = [
        "",
        "https://tanzschulestanek.at/tanzkurse/dance-times-perfektion/",
        "https://tanzschulestanek.at/veranstaltungen/",
    ]

    events = []
    for item in data:
        # Ignore courses that are not open to the public
        if not item["url"] in allowed_urls:
            continue

        url = item["url"]
        if url == "":
            url = "https://tanzschulestanek.at/veranstaltungen/"

        events.append(
            DanceEvent(
                starts_at=datetime.fromisoformat(item["start"]),
                name=item["title"],
                description="",
                location="Stanek",
                website=url,
            )
        )

    return events
