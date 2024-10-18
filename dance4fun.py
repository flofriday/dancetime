import concurrent.futures
from datetime import datetime
from typing import List

import requests

from event import DanceEvent


def parse_datetimes(date: str, time: str) -> datetime:
    return datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")


def download_dance4fun_page(page: int) -> List[DanceEvent]:
    url = f"https://retro.danceforfun.at/termine.php?page={page}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    events = []
    if not data.get("data"):
        return events

    for event in data.get("data", []):
        if event.get("kurstypname") != "Perfektion":
            continue

        if "tag" not in data:
            continue

        starts_at = parse_datetimes(data["tag"], event["von"])
        ends_at = parse_datetimes(data["tag"], event["bis"])
        events.append(
            DanceEvent(
                starts_at=starts_at,
                ends_at=ends_at,
                name=f"{event['kursname']}",
                price_euro_cent=350,  # static price since it is not provided in the API FIXME
                description=event.get("inhalte", ""),
                dancing_school="Dance4Fun",
                website="https://danceforfun.at/termine/",
            )
        )

    return events


def download_dance4fun() -> List[DanceEvent]:
    max_pages = 100  # Adjust this value if we want less events FIXME

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_page = {
            executor.submit(download_dance4fun_page, page): page
            for page in range(max_pages)
        }
        all_events = []

        for future in concurrent.futures.as_completed(future_to_page):
            page = future_to_page[future]
            try:
                events = future.result()
                all_events.extend(events)
                if page >= max_pages - 1:
                    break
            except Exception:
                pass

    return all_events
