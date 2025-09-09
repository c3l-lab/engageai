from pydantic import BaseModel
import pandas as pd
from datetime import datetime

class Action(BaseModel):
    id: str
    student_id: str
    score: float


    


