import argparse
import concurrent.futures
import contextlib
import csv
import html
import inspect
import json
import os
import shutil
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import icalendar
from jinja2 import Template, select_autoescape
from requests.exceptions import ConnectionError, HTTPError

from ballsaal import download_ballsaal
from chris import download_chris
from dance4fun import download_dance4fun
from dimitarstefanin import download_dimitarstefanin
from dorner import download_dorner
from event import DanceEvent
from immervoll import download_immervoll
from kopetzky import download_kopetzky
from rueff import download_rueff
from schwebach import download_schwebach
from strobl import download_strobl


@dataclass
class MetaData:
    count: int
    crawled_at: datetime
    duration: timedelta
    error_messages: list[str]


def download_events() -> tuple[list[DanceEvent], MetaData]:
    downloaders = [
        ("Ballsaal", download_ballsaal),
        ("Chris", download_chris),
        ("Immervoll", download_immervoll),
        ("Rueff", download_rueff),
        ("Schwebach", download_schwebach),
        ("Strobl", download_strobl),
        ("Kopetzky", download_kopetzky),
        ("Dorner", download_dorner),
        ("Dance4Fun", download_dance4fun),
        ("Dimitar Stefanin", download_dimitarstefanin),
    ]

    events = []
    error_messages = []
    crawled_at = datetime.now()
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=len(downloaders)
    ) as executor:
        results = [executor.submit(downloader[1]) for downloader in downloaders]

        name_map = {r: downloaders[i][0] for (i, r) in enumerate(results)}

        for result in concurrent.futures.as_completed(results):
            try:
                new_events = result.result()
                print(
                    f"Downloaded {(name_map[result])} \tin {(datetime.now() - crawled_at).total_seconds():.2f}s \t({len(new_events):02d} events)"
                )
                events += new_events
            except HTTPError as e:
                status = e.response.status_code
                url = e.request.url
                message = f"Got {status} from {url}"
                print("🔥 " + message)
                error_messages.append(message)

            except ConnectionError as e:
                message = f"Failed to connect to {e.request.url}"
                print("🔥 " + message)
                error_messages.append(message)

            except Exception as e:
                line_no, file_name = inspect.trace()[-1][2:4]
                exc_type, _, _exc_tb = sys.exc_info()
                message = f"{exc_type.__name__} in {file_name}:{line_no}: {str(e)}"
                print("🔥 " + message)
                error_messages.append(message)

    metadata = MetaData(
        count=len(events),
        crawled_at=crawled_at,
        duration=datetime.now() - crawled_at,
        error_messages=error_messages,
    )
    return events, metadata


def format_price(price_euro_cent: int) -> str:
    if price_euro_cent % 100 == 0:
        return f"€{price_euro_cent // 100},-"

    return f"€{price_euro_cent / 100:.2f}".replace(".", ",")


def write_csv(events: list[DanceEvent], metadata: MetaData, folder: str):
    csv_path = os.path.join(folder, "events.csv")
    with open(csv_path, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(
            [
                "Starts at",
                "Ends at",
                "Name",
                "Price",
                "Description",
                "Dancing School",
                "Website",
            ]
        )
        for event in events:
            writer.writerow(
                [
                    event.starts_at,
                    event.ends_at,
                    event.name,
                    format_price(event.price_euro_cent)
                    if event.price_euro_cent
                    else None,
                    event.description,
                    event.dancing_school,
                    event.website,
                ]
            )


def write_json(events: list[DanceEvent], metadata: MetaData, folder: str):
    # A helper function to serialize datetime
    def defaultconverter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, timedelta):
            return (o.seconds * 1000) + int(o.microseconds / 1000)
        return o.__dict__

    data = {
        "timestamp": metadata.crawled_at,
        "duration_ms": metadata.duration,
        "event_count": metadata.count,
        "error_messages": metadata.error_messages,
        "events": events,
    }

    json_path = os.path.join(folder, "events.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2, default=defaultconverter)


def write_html(events: list[DanceEvent], metadata: MetaData, folder: str):
    def format_date(d: datetime) -> str:
        if d.date() == datetime.now().date():
            return "Heute"
        if d.date() == (datetime.now() + timedelta(days=1)).date():
            return "Morgen"

        days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        if (d - datetime.now()).days < 7:
            return days[d.weekday()] + "."

        return d.strftime("%d.%m.%Y") + " " + days[d.weekday()] + "."

    with open("template.html", encoding="utf-8") as template_html:
        template = Template(
            template_html.read(),
            autoescape=select_autoescape(
                enabled_extensions=("html", "xml"),
                default_for_string=True,
            ),
        )
        template.globals["format_date"] = format_date
        template.globals["format_price"] = format_price

    index_path = os.path.join(folder, "index.html")
    with open(index_path, "w", encoding="utf-8") as index:
        index.write(
            template.render(
                events=events,
                metadata=metadata,
            )
        )


def write_ics(events: list[DanceEvent], _: MetaData, folder: str):
    # Create a new calendar
    cal = icalendar.Calendar()
    cal.add("prodid", "-//DanceTime//flofriday//")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", "DanceTime")

    for event in events:
        # Create a new event
        ics_event = icalendar.Event()

        # Generate a UUID
        event_uuid = str(uuid.uuid4()) + "@dancetime.flofriday.dev"

        # Set the event properties
        ics_event.add("uid", event_uuid)
        ics_event.add("summary", event.name)
        ics_event.add(
            "dtstamp", datetime.now().replace(tzinfo=ZoneInfo("Europe/Vienna"))
        )
        ics_event.add(
            "dtstart", event.starts_at.replace(tzinfo=ZoneInfo("Europe/Vienna"))
        )
        if event.ends_at is not None:
            ics_event.add(
                "dtend", event.ends_at.replace(tzinfo=ZoneInfo("Europe/Vienna"))
            )
        ics_event.add("location", event.dancing_school)

        description = event.website + "\n\n"
        if event.price_euro_cent is not None:
            description += f"Preis pro Person: {format_price(event.price_euro_cent)}\n"
        description += event.description
        ics_event.add("description", description)
        ics_event.add(
            "x-alt-desc;fmttype=text/html",
            '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN><HTML><BODY>\n'
            f'<a href="{event.website}">Webseite</a><br><br>{html.escape(description).replace("\n", "<br>")}'
            "\n</BODY></HTML>",
        )

        # Add the event to the calendar
        cal.add_component(ics_event)

    # Serialize the calendar to an ICS file
    ics_path = os.path.join(folder, "events.ics")
    with open(ics_path, "wb") as icsfile:
        icsfile.write(cal.to_ical())


def main():
    parser = argparse.ArgumentParser(
        prog="DanceTime",
        description="Aggregate dance events and compile them into multiple formats.",
    )
    parser.add_argument(
        "--output",
        required=False,
        default=".",
        help="folder into which the outputs should be written.",
    )
    args = parser.parse_args()

    events, metadata = download_events()

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    events = list(filter(lambda e: e.starts_at >= today, events))
    metadata.count = len(events)  # update count after sorting
    events = sorted(events, key=lambda e: e.starts_at)

    # Create a couple of data files
    write_json(events, metadata, args.output)
    write_csv(events, metadata, args.output)
    write_ics(events, metadata, args.output)

    # Create the Webpage which needs some static files
    static_files = [
        "index.css",
        "logo32.png",
        "logo180.png",
        "logo.svg",
        "calendar.png",
    ]

    with contextlib.suppress(shutil.SameFileError):
        for file in static_files:
            shutil.copy(file, os.path.join(args.output, file))

    write_html(events, metadata, args.output)

    # Write final statistics
    print(
        f"Created {metadata.count} events in {metadata.duration.total_seconds():.2f}s. 💃✨"
    )


if __name__ == "__main__":
    main()
