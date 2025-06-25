import lib.definitions as d
import lib.utils as u
from collections import defaultdict
import os
from typing import Any, Dict, List
from datetime import datetime, date

def dict_to_row(json: Dict[str, Any]) -> d.AccountRow:
    date: datetime | None = None
    type: str | None = None
    description: str | None = None
    amount: float = 0
    balance: float = 0

    try:
        if "date" not in json:
            raise ValueError()
        date = datetime.strptime(json["date"], "%Y-%m-%d")
    except:
        raise ValueError(f"date could not be parsed from dict")
    
    if "type" in json:
        type = json["type"]
        
    if "description" in json:
        type = json["description"]
        
    if "amount" in json:
        amount = float(json["amount"])
    
    if "balance" in json:
        balance = float(json["balance"])
        
    
    return d.AccountRow(
        date = date,
        type = type,
        description=description,
        amount=amount,
        balance=balance
    )
    
def dict_to_account(json: Dict[str, Any]) -> d.Account:
    
    label: str = ""
    rows: List[d.AccountRow] = []
    currentBal = 0
    
    if "label" in json:
        label = json["label"]
        
    if "rows" in json:
        for row in json["rows"]:
            rows.append(dict_to_row(row))
            
    if "currentBalance" in json:
        currentBal = json["currentBalance"]
    
    return d.Account(
        label=label,
        rows=rows,
        currBalance=currentBal,
        totalInterest=0,
        totalPrinciple=0
    )

def get_row_map(account: d.Account) -> dict[str, d.AccountRow]:
    map: dict[str, d.AccountRow] = {}
    
    for row in account.rows:
        map[row.date.strftime("%Y-%m-%d")] = row

    return map

def export_csv(file: str, account: d.Account) -> None:
    """
    Exports the list of InterestSummary entries to a CSV file in the /data directory.

    Args:
        file (str): File name (e.g. 'july_rates.csv')
        rates (List[d.InterestSummary]): List of interest rate summaries
    """
    # Determine full path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(root_dir, "data")
    os.makedirs(data_path, exist_ok=True)

    full_path = os.path.join(data_path, file)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("date,type,description,amount,balance\n")
        for row in account.rows:
            f.write(row.toCSV() + "\n")

    print(f"Exported {len(account.rows)} entries to {full_path}")    
    
def validate_transactions(statements: d.Account, loanAccounts: list[d.Account]):
    row_map: dict[date, list[d.AccountRow]] = defaultdict(list)
    
    for row in statements.rows:
        row_map[row.date.date()].append(row)
    
    for loanAccount in loanAccounts:
        for row in loanAccount.rows:
            if row.date.date() not in row_map:
                raise ValueError(f"could not find transaction by {loanAccount.label} on {row.date.date()}")
            isEqual = False
            for rr in row_map[row.date.date()]:
                if rr.amount == row.amount:
                    isEqual = True
                    
            if not isEqual:
                raise ValueError(f"could not find transaction by {loanAccount.label} on {row.date.date()} with amount {u.format_currency(row.amount)}")
            