from datetime import datetime
from typing import List
import csv
import concurrent.futures
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


def write_csv(events: List[DanceEvent]):
    with open("events.csv", "w") as csvfile:
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


def write_html(events: List[DanceEvent]):

    with open("template.html") as template_html:
        template = Template(
            template_html.read(),
            autoescape=select_autoescape(
                enabled_extensions=("html", "xml"),
                default_for_string=True,
            ),
        )

    with open("index.html", "w") as index:
        index.write(
            template.render(
                events=events,
                timestamp=datetime.now(),
            )
        )


def main():
    events = download_events()

    events = list(filter(lambda e: e.starts_at > datetime.today(), events))
    events = sorted(events, key=lambda e: e.starts_at)
    # print(events)

    write_csv(events)
    write_html(events)


if __name__ == "__main__":
    main()
