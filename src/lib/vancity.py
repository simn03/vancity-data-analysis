import lib.definitions as d
import csv
import re
from datetime import datetime
from typing import List
import os
import fitz  # PyMuPDF


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
        currBalance=last_balance,
        totalInterest=-1,
        totalPrinciple=-1
    )
    
metadata_pattern = re.compile(
        r'^ACCOUNTOWNERS:.*'
        r'|^STATEMENTPERIOD:.*'
        r'|^ACCOUNTSUMMARY$'
        r'|^DAILYBANKING$'
        r'|^TOTAL$'
        r'|^OPENINGCLOSING$'
        r'|^TOTALTOTALBALANCEONBALANCEON$'
        r'|^ACCOUNTSUMMARY$'
        r'|^WITHDRAWALSDEPOSITS$'
        r'|VANCITY/.COM$'
        r'|^BORROWING$'
        r'|^MORTGAGES$'
        ,re.IGNORECASE
    )
header_pattern = re.compile(
    r'.\s*#\d{12}($|\(\w+(?!\))$|\(\w+\)$)',
    re.IGNORECASE
)
interest_pattern = re.compile(
    r'(#\d{12}LINEOFCREDITDETAILS.*)'
    r'|INTERESTSUMMARY:\d{1,2}[A-Z]{3}TO\d{1,2}[A-Z]{3}:[\d.]+%'
    r'|\d{1,2}[A-Z]{3}TO\d{1,2}[A-Z]{3}:[\d.]+%',
    re.IGNORECASE
)
item_pattern = re.compile(
    r'.* [^\(] .*\)$$'
    r'|DATEDESCRIPTION\s*'
    r'|\d{1,2}[A-Z]{3}.*OFFICIALCHEQUE'                # official cheque lines (out)
    r'|\d{1,2}[A-Z]{3}.*FUNDSTRANSFER-ONLINE'          # funds transfer lines (out)
    r'|\d{1,2}[A-Z]{3}.*FUNDSTRANSFER',                # funds transfer (in)
    re.IGNORECASE
)
    
def _redact_statement(in_path: str, out_path: str, account: str) -> None:
    correct_header_pattern = re.compile(
        rf'.\s*#{account}.\s*', 
        re.IGNORECASE
    )
    
    doc = fitz.open(in_path, filetype="pdf")

    for page in doc:
        blocks = page.get_text("blocks") # type: ignore
        inside_section = False

        for block in blocks:
            if len(block) < 5:
                continue

            rect = fitz.Rect(block[:4])
            text = block[4].strip()
            cleaned = re.sub(r'\s+', '', text.upper())  # All uppercase, no whitespace
            
            if metadata_pattern.search(cleaned):
                continue

            # Check for the chequing-account header
            if header_pattern.search(cleaned):
                if correct_header_pattern.search(cleaned):
                    inside_section = True
                else:
                    inside_section = False
                continue
                
            # Determine if this block should be preserved
            if interest_pattern.search(cleaned):
                continue  # Keep interest lines
            if inside_section and item_pattern.search(cleaned):
                continue  # Keep chequing section transactions

            # Otherwise, redact
            page.add_redact_annot(rect, fill=(1, 1, 1))

        page.apply_redactions() # type: ignore

    doc.save(out_path)
    doc.close()
    inside_section = False

def redact_statements(input_folder: str, output_folder: str, account: str) -> None:
    # Patterns

    os.makedirs(output_folder, exist_ok=True)

    for fname in os.listdir(input_folder):
        if not fname.lower().endswith(".pdf"):
            continue

        in_path = os.path.join(input_folder, fname)
        out_path = os.path.join(output_folder, fname.replace(".pdf", "-redacted.pdf"))
        
        _redact_statement(in_path, out_path, account)
        
    print(f"Redacted {len(os.listdir(input_folder))} statements to {output_folder}")