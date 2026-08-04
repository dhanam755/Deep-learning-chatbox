from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserRecord:
    id: str
    name: str
    email: str
    created_at: Optional[datetime] = None
