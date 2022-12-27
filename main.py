from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Tuple, Dict
import os
import csv
import json
import concurrent.futures
import argparse
from jinja2 import Template, select_autoescape


from event import DanceEvent
from ballsaal import download_ballsaal
from schwebach import download_schwebach


@dataclass
class MetaData:
    crawled_at: datetime
    duration: timedelta


def download_events() -> Tuple[List[DanceEvent], Dict]:
    downloaders = [download_ballsaal, download_schwebach]

    # FIXME: We should catch any exceptions here so that if a single source
    # isn't available not the whole script crashes.
    events = []
    crawled_at = datetime.now()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = [executor.submit(func) for func in downloaders]

        for result in concurrent.futures.as_completed(results):
            events += result.result()

    metadata = MetaData(crawled_at=crawled_at, duration=datetime.now() - crawled_at)
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

    events = list(filter(lambda e: e.starts_at > datetime.today(), events))
    events = sorted(events, key=lambda e: e.starts_at)
    # print(events)

    write_csv(events, metadata, args.output)
    write_json(events, metadata, args.output)
    write_html(events, metadata, args.output)


if __name__ == "__main__":
    main()
