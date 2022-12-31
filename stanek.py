from typing import List
from event import DanceEvent
from datetime import datetime, timedelta, date
import requests


# Well, we couldn't really find any API and the Website itself seams a little
# janky to parse. But luckily there is the calendar which gets it's events from
# the server via json. So let's just pretend we are a weird calendar and we
# need some events.
def download_stanek() -> List[DanceEvent]:
    # Calculate the dates and make the request
    start_date = date.today()
    end_date = start_date + timedelta(weeks=9)
    response = requests.get(
        f"https://tanzschulestanek.at/wp-content/plugins/ts_kurse/api/ts_kalender.php?start={start_date.isoformat()}&end={end_date.isoformat()}"
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

    # Convert the json data to events
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
