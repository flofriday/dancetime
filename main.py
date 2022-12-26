from datetime import datetime
from typing import List
import os
import csv
import concurrent.futures
import argparse
from jinja2 import Template, select_autoescape


from event import DanceEvent
from ballsaal import download_ballsaal


def download_events() -> List[DanceEvent]:
    downloaders = [download_ballsaal]

    events = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = [executor.submit(func) for func in downloaders]

        for result in concurrent.futures.as_completed(results):
            events += result.result()

    return events


def write_csv(events: List[DanceEvent], folder: str):
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


def write_html(events: List[DanceEvent], folder: str):

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
                timestamp=datetime.now(),
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

    events = download_events()

    events = list(filter(lambda e: e.starts_at > datetime.today(), events))
    events = sorted(events, key=lambda e: e.starts_at)
    # print(events)

    write_csv(events, args.output)
    write_html(events, args.output)


if __name__ == "__main__":
    main()
