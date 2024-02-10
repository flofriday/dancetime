from event import DanceEvent
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
import concurrent.futures


def clean_name(name: str) -> str:
    # Some names start and end with a double quote for no reason
    if name.startswith('"') and name.endswith('"'):
        name = name[1:-1]

    # Sometimes words inside names are in ALL-CAPS which is just ugly
    def deupperice(text: str) -> str:
        return text.capitalize() if text.isupper() else text

    name = " ".join(map(deupperice, name.split(" ")))

    # Some events end in ...
    if name.endswith("..."):
        name = name[:-3]

    # And some events should just always be renamed
    rename_table = {
        "Vienna Salsa Splash": "Salsa Splash",
    }

    if name in rename_table:
        name = rename_table[name]

    return name


# For the ends_at we need to do a second request to the ticketing website
# because only there it says when the event will end. That is a bit of
# work so we are doing it here in a separate function.
def add_ends_at(event: DanceEvent):
    response = requests.get(event.website, timeout=10)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    date_text = soup.find("span", class_="end-date").text
    event.ends_at = dateparser.parse(date_text, languages=["de", "en"])

    # We don't parse the year so, the year it might assume, can be off by one.
    if event.starts_at > event.ends_at:
        event.ends_at += relativedelta(years=1)

    # FIXME: We could also include all prices and wether or not it is full.

    return event


# For ballsaal.at we need to download and parse html. This is more tedious than
# a JSON API but at least the format is very consistent.
def download_ballsaal() -> list[DanceEvent]:
    response = requests.get(
        "https://www.ballsaal.at/termine_tickets/?no_cache=1", timeout=10
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")
    event_items = soup.find_all(class_="event")

    events = []
    for event in event_items:
        name = event.find(class_="name").text
        name = clean_name(name)
        description = event.find(class_="short-description").text
        date_string = event.find(class_="date").text
        url = event.find(class_="button")["href"]

        date = datetime.strptime(date_string[4:], "%d.%m.%Y, %H:%M Uhr")
        events.append(
            DanceEvent(
                starts_at=date,
                name=name,
                description=description,
                dancing_school="Ballsaal",
                website=url,
            )
        )

    # Add the ends_at to each event event if
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max(1, len(events))
    ) as executor:
        events = list(executor.map(add_ends_at, events))

    return events
