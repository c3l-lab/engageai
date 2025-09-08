from pydantic import BaseModel
import pandas as pd
from datetime import datetime

class Assessment(BaseModel):
    id: str
    student_id: str
    score: float
    due_date: datetime

    
