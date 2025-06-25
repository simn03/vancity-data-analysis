from collections import defaultdict
from datetime import timedelta, date
from typing import List, Dict
import lib.definitions as defs
from datetime import datetime, date

def calculate_interest_rows(
    account_history: defs.Account,
    interest_summaries: List[defs.InterestSummary],
    interest_day: int = 15
) -> defs.Account:

    # Convert payments to {date: amount}
    payment_map: Dict[date, List[defs.AccountRow]] = defaultdict(list)
    for entry in account_history.rows:
        payment_date = entry.date.date()
        payment_map[payment_date].append(entry)

    # Build timeline
    min_date = min(payment_map.keys())
    max_date = date.today()
    
    interest_summaries = sorted(interest_summaries, key=lambda r: r.start)
    interest_by_date = {}

    for summary in interest_summaries:
        d = summary.start.date()
        while d <= summary.end.date():
            interest_by_date[d] = summary.rate
            d += timedelta(days=1)

    current_balance = 0.0
    current_interest = 0.0
    total_interest = 0.0
    total_principle = 0.0
    rows: List[defs.AccountRow] = []

    d = min_date
    while d <= max_date:
        # Apply payments first
        if d in payment_map:
            for row in payment_map[d]:
                amt = row.amount
                current_balance += amt
                total_principle += amt
                rows.append(defs.AccountRow(
                    date=datetime.combine(d, datetime.min.time()),
                    type="payment" if amt > 0 else "loan",
                    description=row.description,
                    amount=round(amt,2),
                    balance=round(current_balance,2)
                ))

        # Apply daily interest
        rate = interest_by_date.get(d, 0.0)
        daily_interest = current_balance * (rate / 365)
        current_interest += min(0, daily_interest) # do not remove interest
 
        # Charge interest monthly on specified day
        if d.day == interest_day:
            if abs(current_interest) > 0.005:  # threshold to avoid noise
                current_balance += current_interest
                rows.append(defs.AccountRow(
                    date=datetime.combine(d, datetime.min.time()),
                    type="interest",
                    description=f"Interest charge @ {interest_by_date[d]:.2%}",
                    amount=round(current_interest, 2),
                    balance=round(current_balance, 2)
                ))
                total_interest += current_interest
                current_interest = 0.0

        d += timedelta(days=1)
        
    account = defs.Account(
        label=account_history.label,
        rows=rows,
        currBalance=rows[len(rows)-1].balance,
        totalInterest=total_interest,
        totalPrinciple=total_principle
    )

    return account
