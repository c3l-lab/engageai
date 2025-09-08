from typing import List
from pydantic import BaseModel

class Student(BaseModel):
    id: str
    name: str
    term: str
    email: str
    # assessments: List[str]  # list of assessment IDs
