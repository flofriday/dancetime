from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DanceEvent:
    starts_at: datetime
    name: str
    description: str
    location: str
    website: str
    ends_at: Optional[datetime] = None
