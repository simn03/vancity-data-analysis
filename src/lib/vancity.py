import lib.definitions as d
import csv
import re
from datetime import datetime
from typing import List

def parse_csv(file: str) -> d.Account:
    rows: List[d.AccountRow] = []

    with open(file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        account_number = None
        last_balance = None

        for i, row in enumerate(reader):
            if not row or len(row) < 7:
                continue  # skip empty or malformed lines

            acc_num = row[0].strip()
            date_str = row[1].strip()
            raw_description = row[2].strip()
            amount_sub = row[4].strip()
            amount_add = row[5].strip()
            balance_str = row[6].strip()

            # Save the first seen account number
            if account_number is None:
                account_number = acc_num

            # Parse date
            try:
                date = datetime.strptime(date_str, "%d-%b-%Y")
            except ValueError:
                raise ValueError(f"Invalid date format in row {i+1}: '{date_str}'")
            
            # Parse type and description
            parts = re.split(r'\s{2,}', raw_description)

            transaction_type = parts[0] if parts else ""
            description = " ".join(parts[1:]) if len(parts) > 1 else ""

            # Determine actual amount (subtracted is negative, added is positive)
            amount = 0.0
            if amount_sub:
                amount = -float(amount_sub.replace(",", ""))
            elif amount_add:
                amount = float(amount_add.replace(",", ""))

            # Parse balance
            balance = float(balance_str.replace(",", ""))
            last_balance = balance

            rows.append(d.AccountRow(
                date=date,
                type=transaction_type,
                description=description,
                amount=amount,
                balance=balance
            ))

    if account_number is None or last_balance is None:
        raise ValueError("Failed to parse account number or balance from file.")
    
    rows.sort(key=lambda r: r.date)

    return d.Account(
        label=account_number,
        rows=rows,
        currBalance=last_balance
    )
