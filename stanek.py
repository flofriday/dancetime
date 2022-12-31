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

        starts_at = datetime.fromisoformat(item["start"])

        url = item["url"]
        if url == "":
            url = "https://tanzschulestanek.at/veranstaltungen/"

        ends_at = None

        # Dance Nights seam to always end at 22h so for this kind of event we
        # set the end date manually.
        if "dance night" in item["title"].lower():
            ends_at = starts_at.replace(hour=22, minute=00)

        events.append(
            DanceEvent(
                starts_at=starts_at,
                ends_at=ends_at,
                name=item["title"],
                description="",
                dancing_school="Stanek",
                website=url,
            )
        )

    return events
