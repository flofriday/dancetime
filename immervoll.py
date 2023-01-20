from event import DanceEvent
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


# Parses dates in the format: `Samstag, 21.01.2023 19:30 - 22:15 Uhr`
# which is quite common on the page.
def parse_datetimes(text: str) -> Tuple[datetime, datetime]:
    date_text, start_text, end_text = re.search(
        ", ([0-9\.]+) ([0-9:]+) - ([0-9:]+) Uhr", text
    ).groups()

    day = datetime.strptime(date_text, "%d.%m.%Y")
    start_hour = int(start_text.split(":")[0])
    start_min = int(start_text.split(":")[1])
    end_hour = int(end_text.split(":")[0])
    end_min = int(end_text.split(":")[1])

    return (
        day.replace(hour=start_hour, minute=start_min),
        day.replace(hour=end_hour, minute=end_min),
    )


def download_immervoll() -> List[DanceEvent]:
    response = requests.get("https://www.tanzschule-immervoll.at/events/")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")
    table_elements = soup.find_all("table")

    # Parse the events
    events = []
    events_table = table_elements[0]
    for row in events_table.find_all("tr"):
        # Check via the image if that is the right location (and yes this code
        # hurts me as much as it does you)
        if "standort_ac" in row.find("img")["src"]:
            # Auhof is technically in Vienna but it is a pain to get there so
            # no we won't list it on our page.
            continue

        info_td = row.find_all("td")[1]
        starts_at, ends_at = parse_datetimes(info_td.text)

        text: str = row.find("div").text
        name, description = text.split("|", maxsplit=1)
        name = " ".join(
            map(lambda s: s.capitalize(), name.strip().replace("-", " ").split(" "))
        )
        description = description.replace("|", "\n").strip()

        events.append(
            DanceEvent(
                starts_at=starts_at,
                ends_at=ends_at,
                name=name,
                description=description,
                dancing_school="Immervoll",
                website="https://www.tanzschule-immervoll.at/events/",
            )
        )

    # Parse perfections
    perfection_table = table_elements[2]
    for row in perfection_table.find_all("tr"):
        # Check via the image if that is the right location (and yes this code
        # hurts me as much as it does you)
        if "standort_ac" in row.find("img")["src"]:
            # Auhof is technically in Vienna but it is a pain to get there so
            # no we won't list it on our page.
            continue

        starts_at, ends_at = parse_datetimes(row.text.strip())

        events.append(
            DanceEvent(
                starts_at=starts_at,
                ends_at=ends_at,
                name="Perfektion",
                description="Altgasse 6, 1130 Wien\nKeine Voranmeldung notwendig. Teilnahme nur paarweise möglich.\nAbendbeitrag pro Paar: EUR 15,00\n\nVerschiedene Tanz- und Übungsabende runden unser Kursangebot ab! Hier kommen Schüler aus allen Kursstufen zusammen und perfektionieren ihr erworbenes Können. Gesellige Abende in unseren Tanzschulen bieten den optimalen Ausklang eines arbeitsreichen Tages.",
                dancing_school="Immervoll",
                website="https://www.tanzschule-immervoll.at/events/",
            )
        )

    return events
