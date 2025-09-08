from typing import List
from pydantic import BaseModel

class SentMessage(BaseModel):
    date: str
    week: int
    name: str
    term: str
    # assessments: List[str]  # list of assessment IDs
