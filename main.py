from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Dict
import os
import csv
import json
import concurrent.futures
import argparse
import shutil
from jinja2 import Template, select_autoescape
import icalendar


from event import DanceEvent
from ballsaal import download_ballsaal
from rueff import download_rueff
from schwebach import download_schwebach
from stanek import download_stanek


@dataclass
class MetaData:
    count: int
    crawled_at: datetime
    duration: timedelta


def download_events() -> Tuple[List[DanceEvent], Dict]:
    downloaders = [
        download_ballsaal,
        download_rueff,
        download_schwebach,
        download_stanek,
    ]

    # FIXME: We should catch any exceptions here so that if a single source
    # isn't available not the whole script crashes.
    events = []
    crawled_at = datetime.now()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = [executor.submit(func) for func in downloaders]

        for result in concurrent.futures.as_completed(results):
            events += result.result()

    metadata = MetaData(
        count=len(events),
        crawled_at=crawled_at,
        duration=datetime.now() - crawled_at,
    )
    return events, metadata


def write_csv(events: List[DanceEvent], metadata: MetaData, folder: str):
    csv_path = os.path.join(folder, "events.csv")
    with open(csv_path, "w") as csvfile:
        writer = csv.writer(csvfile, delimiter=",")
        writer.writerow(["Date", "Name", "Description", "Location", "Website"])
        for event in events:
            writer.writerow(
                [
                    event.starts_at,
                    event.name,
                    event.description,
                    event.location,
                    event.website,
                ]
            )


def write_json(events: List[DanceEvent], metadata: MetaData, folder: str):

    # A helper function to serialize datetime
    def defaultconverter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, timedelta):
            return o.microseconds / 1000
        return o.__dict__

    data = {
        "timestamp": metadata.crawled_at,
        "duration_ms": metadata.duration,
        "event_count": metadata.count,
        "events": events,
    }

    json_path = os.path.join(folder, "events.json")
    with open(json_path, "w") as json_file:
        json.dump(data, json_file, indent=2, default=defaultconverter)


def write_html(events: List[DanceEvent], metadata: MetaData, folder: str):

    with open("template.html") as template_html:
        template = Template(
            template_html.read(),
            autoescape=select_autoescape(
                enabled_extensions=("html", "xml"),
                default_for_string=True,
            ),
        )

    index_path = os.path.join(folder, "index.html")
    with open(index_path, "w") as index:
        index.write(
            template.render(
                events=events,
                metadata=metadata,
            )
        )


def write_ics(events: List[DanceEvent], metadata: MetaData, folder: str):
    # Create a new calendar
    cal = icalendar.Calendar()
    cal.add('prodid', '-//DanceTime//flofriday//')
    cal.add('version', '2.0')
    cal.add('x-wr-calname', 'DanceTime')

    for event in events:
        # Create a new event
        ics_event = icalendar.Event()

        # Set the event properties
        ics_event.add("summary", event.name)
        ics_event.add("dtstart", icalendar.vDDDTypes(event.starts_at))
        if event.ends_at != None:
            ics_event.add("dtend", icalendar.vDDDTypes(event.ends_at))
        ics_event.add("location", event.location)
        ics_event.add("url", event.website)
        ics_event.add("description",
                      event.website + '\n' + event.description)
        ics_event.add("x-alt-desc",
                      """<a href="http: // """ + event.website + """">Website</a><br><br>""" + event.description)

        # Add the event to the calendar
        cal.add_component(ics_event)

    # Serialize the calendar to an ICS file
    ics_path = os.path.join(folder, "events.ics")
    with open(ics_path, "wb") as icsfile:
        icsfile.write(cal.to_ical())


def main():
    parser = argparse.ArgumentParser(
        prog="DanceTime",
        description="Aggregate dance envents and compile them into multiple formats.",
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
    events = list(filter(lambda e: e.starts_at > today, events))
    events = sorted(events, key=lambda e: e.starts_at)

    # Create a couple of data files
    write_json(events, metadata, args.output)
    write_csv(events, metadata, args.output)
    write_ics(events, metadata, args.output)

    # Create the Webpage which needs the css file
    try:
        shutil.copy("index.css", os.path.join(args.output, "index.css"))
    except shutil.SameFileError:
        pass
    write_html(events, metadata, args.output)


if __name__ == "__main__":
    main()
