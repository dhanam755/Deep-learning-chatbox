from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatRecord:
    id: str
    user_id: str
    title: str
    model: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
