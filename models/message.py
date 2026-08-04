from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MessageRecord:
    id: str
    chat_id: str
    role: str
    content: str
    timestamp: Optional[datetime] = None
