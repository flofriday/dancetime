from dataclasses import dataclass
from datetime import datetime


@dataclass
class DanceEvent:
    starts_at: datetime
    name: str
    description: str
    location: str
    website: str
