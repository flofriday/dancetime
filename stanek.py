from datetime import date, datetime, timedelta

import requests

from event import DanceEvent


# Well, we couldn't really find any API and the Website itself seams a little
# janky to parse. But luckily there is the calendar which gets it's events from
# the server via json. So let's just pretend we are a weird calendar and we
# need some events.
def download_stanek() -> list[DanceEvent]:
    # Calculate the dates and make the request
    start_date = date.today()
    end_date = start_date + timedelta(weeks=9)
    url = f"https://tanzschulestanek.at/wp-content/plugins/ts_kurse/api/ts_kalender.php?start={start_date.isoformat()}&end={end_date.isoformat()}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    # FIXME: We need to investigate if to where events really link.
    # At the time of writing there is only one event(party) that has an empty
    # link.
    allowed_urls = [
        "https://tanzschulestanek.at/tanzkurse/dance-times-perfektion/",
        "https://tanzschulestanek.at/veranstaltungen/",
    ]

    # Convert the json data to events
    events = []
    for item in data:
        # Ignore courses that are not open to the public
        if item["url"] not in allowed_urls:
            continue

        starts_at = datetime.fromisoformat(item["start"])
        url = item["url"]
        ends_at = None

        # Dance Nights seam to always end at 22:30h so for this kind of event
        # we set the end date manually.
        if "dance night" in item["title"].lower():
            ends_at = starts_at.replace(hour=22, minute=30)

        events.append(
            DanceEvent(
                starts_at=starts_at,
                ends_at=ends_at,
                name=item["title"],
                price_euro_cent=None,
                description="In der Dance Night könnt Ihr in der Tanzschule Stanek ausgiebig tanzen, Eure Tanzkenntnisse vertiefen und einen netten Abend verbringen",
                dancing_school="Stanek",
                website=url,
            )
        )

    return events
