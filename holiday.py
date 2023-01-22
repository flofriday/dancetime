from datetime import date, timedelta
from typing import Set
import csv


# Get all holydays from the official federal list from:
# https://www.data.gv.at/katalog/en/dataset/3deb9da7-8394-4797-9f32-5ca95281ba5b
# Note: yes this might look as not as sustainable as downloading from an API,
# but since the csv includes dates for the next 10 years I think we will be
# good. Also the webscraping will break much faster than this.
def holidays() -> Set[date]:
    holidays = set()
    with open("holyday.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only get federal holidays
            if row["TYP"] != "HF":
                continue

            day = date.fromisoformat(row["DATUM"])

            # Ignore events in the past or to far in the future
            if day < date.today() or day > date.today() + timedelta(days=365):
                continue

            holidays.add(day)

    return holidays
