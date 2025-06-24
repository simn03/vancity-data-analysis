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
    
    def __str__(self):
        return f"{self.start.date()} to {self.end.date()} @ {self.rate:.2%}"
    def toCSV(self):
        return f"{self.start.date()},{self.end.date()},{self.rate},"