from datetime import datetime
from dataclasses import dataclass

@dataclass
class StatementSummary:
    path: str
    date: datetime

@dataclass
class InterestSummary:
    start: datetime
    end: datetime
    rate: float
    
