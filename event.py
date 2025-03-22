from dataclasses import dataclass
from datetime import datetime


@dataclass
class DanceEvent:
    starts_at: datetime
    name: str
    price_euro_cent: int | None
    description: str
    dancing_school: str
    website: str
    ends_at: datetime | None = None
