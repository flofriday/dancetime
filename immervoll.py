import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from event import DanceEvent

IMMERVOLL_WEBSITE = "https://www.tanzschule-immervoll.at/events/"
DATE_PATTERN = re.compile(r", ([0-9\\.]+) ([0-9:]+) - ([0-9:]+) Uhr")

BASE_DESCRIPTION = "Altgasse 6, 1130 Wien\nKeine Voranmeldung notwendig."


# Parses dates like `Samstag, 21.01.2023 19:30 - 22:15 Uhr` from table rows.
def parse_datetimes(text: str) -> tuple[datetime, datetime]:
    date_text, start_text, end_text = DATE_PATTERN.search(text).groups()

    day = datetime.strptime(date_text, "%d.%m.%Y")
    start_hour, start_min = (int(x) for x in start_text.split(":"))
    end_hour, end_min = (int(x) for x in end_text.split(":"))

    return (
        day.replace(hour=start_hour, minute=start_min),
        day.replace(hour=end_hour, minute=end_min),
    )


def _section_heading(table) -> str:
    heading = table.find_previous("h2")
    return heading.get_text(strip=True) if heading else ""


def _event_from_row(
    starts_at: datetime,
    ends_at: datetime,
    section: str,
    row_text: str,
) -> DanceEvent | None:
    if (
        "festlicher Abschluss" in row_text
        or "Saisonabschluss" in row_text.lower()
        or "Allgemein" in section
    ):
        name = "Saisonabschluss"
        price = 1600
        description = (
            f"{BASE_DESCRIPTION}\n"
            "Teilnahme nur paarweise möglich.\n"
            "Ein festlicher Abschluss der Tanzsaison."
        )
    elif "Anfänger" in section or "Bronze" in section:
        name = "Anfänger Perfektion"
        price = 850
        description = (
            f"{BASE_DESCRIPTION}\n"
            "Teilnahme nur paarweise möglich.\n"
            "Für Anfänger bis Bronze — Tanzlehrer im Saal."
        )
    elif "Jugendliche" in section:
        name = "Perfektion Jugendliche"
        price = 600
        description = (
            f"{BASE_DESCRIPTION}\nFür Jugendliche — Teilnahme auch einzeln möglich."
        )
    elif "Slowfox" in section or "Slowfox" in row_text:
        name = "Slowfox Übungsabend"
        price = 1000
        description = (
            f"{BASE_DESCRIPTION}\n"
            "Teilnahme nur paarweise möglich.\n"
            "Slowfox-Übungsabend mit aktiver Betreuung."
        )
    elif "Paare" in section:
        name = "Perfektion"
        match starts_at.weekday():
            case 1:
                price = 850
            case 5:
                price = 950
            case _:
                price = None
        description = (
            f"{BASE_DESCRIPTION}\n"
            "Teilnahme nur paarweise möglich.\n"
            "Verschiedene Tanz- und Übungsabende für alle Kursstufen."
        )
    else:
        return None

    return DanceEvent(
        starts_at=starts_at,
        ends_at=ends_at,
        name=name,
        price_euro_cent=price,
        description=description,
        dancing_school="Immervoll",
        website=IMMERVOLL_WEBSITE,
    )


def download_immervoll() -> list[DanceEvent]:
    response = requests.get(
        IMMERVOLL_WEBSITE,
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, features="html.parser")
    events: list[DanceEvent] = []
    seen_starts: set[datetime] = set()

    for table in soup.find_all("table"):
        section = _section_heading(table)
        for row in table.find_all("tr"):
            img = row.find("img")
            src = img.get("src") if img else None
            if src is None:
                continue
            # standort_ac = Auhof-Center; standort_ag = Altgasse — list Altgasse only.
            if "standort_ac" in src:
                continue

            row_text = row.get_text(" ", strip=True)
            if not DATE_PATTERN.search(row_text):
                continue

            starts_at, ends_at = parse_datetimes(row_text)
            if starts_at in seen_starts:
                continue

            event = _event_from_row(starts_at, ends_at, section, row_text)
            if event is None:
                continue

            if event.name == "Perfektion" and any(
                e.starts_at == starts_at and e.name == "Saisonabschluss" for e in events
            ):
                continue

            events.append(event)
            seen_starts.add(starts_at)

    return events
