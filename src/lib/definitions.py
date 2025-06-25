from datetime import datetime
from dataclasses import dataclass
import lib.utils as u

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
        return f"{self.start.date()},{self.end.date()},{self.rate}"
@dataclass
class AccountRow:
    date: datetime
    type: str | None
    description: str | None
    amount: float
    balance: float
    
    def __str__(self):
        return f"{self.date.date()}: Change of {u.format_currency(self.amount)} resulting in new balance of {u.format_currency(self.balance)}"
    
    def toCSV(self):
        return f"{self.date.date()},{self.type},{self.description},{self.amount},{self.balance}"
    
@dataclass
class Account:
    label: str
    rows: list[AccountRow]
    totalInterest: float
    totalPrinciple: float
    currBalance: float        
    