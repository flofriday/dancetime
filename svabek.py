from datetime import date, datetime
from zoneinfo import ZoneInfo

import icalendar
import requests

from event import DanceEvent

VIENNA = ZoneInfo("Europe/Vienna")
SVABEK_ICAL_URL = "https://www.svabek.at/events/?ical=1"
SVABEK_WEBSITE = "https://www.svabek.at/perfektionen/"
SVABEK_DESCRIPTION = (
    "Heiligenstädter Strasse 157, 1190 Wien\nKeine Anmeldung erforderlich."
)


def _to_naive_local(dt: datetime | date) -> datetime | None:
    if isinstance(dt, date) and not isinstance(dt, datetime):
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(VIENNA).replace(tzinfo=None)
    return dt


def _is_perfection_event(component: icalendar.Event) -> bool:
    categories = component.get("categories")
    if categories is not None:
        for category in categories:
            if str(category).strip().lower() == "perfektion":
                return True

    summary = component.get("summary")
    return summary is not None and str(summary).startswith("Perfektion")


def download_svabek() -> list[DanceEvent]:
    response = requests.get(SVABEK_ICAL_URL, timeout=10)
    response.raise_for_status()

    calendar = icalendar.Calendar.from_ical(response.content)
    events = []

    for component in calendar.walk("VEVENT"):
        if not _is_perfection_event(component):
            continue

        starts_at = _to_naive_local(component.decoded("dtstart"))
        if starts_at is None:
            continue

        ends_at = component.decoded("dtend")
        if ends_at is not None:
            ends_at = _to_naive_local(ends_at)

        url = component.get("url")
        website = str(url) if url is not None else SVABEK_WEBSITE

        events.append(
            DanceEvent(
                starts_at=starts_at,
                ends_at=ends_at,
                name="Perfektion",
                price_euro_cent=1000,
                description=SVABEK_DESCRIPTION,
                dancing_school="Svabek",
                website=website,
            )
        )

    return events
