import os
import re
from datetime import datetime
from typing import Dict, List
import fitz  # PyMuPDF
import lib.definitions as d

def parse_statements_map(folder_path: str) -> List[d.StatementSummary]:
    """
    Scans the given folder for statement PDF files and maps them by 'yyyy-mm' date string.

    Parameters:
        folder_path (str): The path to the folder containing the statement files.

    Returns:
        Dict[str, str]: A dictionary mapping the 'yyyy-mm' date to the file's full path.
    """
    pattern = re.compile(r"statement-\d+-(\d{2}[A-Za-z]{3}\d{2})\.pdf$")
    statements: List[d.StatementSummary] = []

    for filename in os.listdir(folder_path):
        match = pattern.match(filename)
        if match:
            raw_date = match.group(1)  # e.g., '21Apr01'
            try:
                # Convert to datetime using expected format
                parsed_date = datetime.strptime(raw_date, "%y%b%d")
                full_path = os.path.join(folder_path, filename)
                statements.append(d.StatementSummary(
                    path = full_path,
                    date = parsed_date
                ))
            except ValueError as e:
                print(f"Skipping {filename}: could not parse date '{raw_date}' ({e})")
                
    statements.sort(key=lambda s: s.date)

    return statements

def extract_interest_summary(statement: d.StatementSummary) -> d.InterestSummary:
    """
    Extracts interest start date, end date, and rate from the interest summary block in the PDF.

    Returns a dictionary with 'start_date', 'end_date', and 'interest_rate' keys.
    """
    with fitz.open(statement.path) as doc:
        text = ""
        for page in doc:
            text += page.get_text() # type: ignore

    # Normalize spacing (remove extra whitespace and newlines)
    cleaned = re.sub(r'\s+', '', text.upper())  # remove all whitespace and uppercase for consistency

    # Match pattern like "INTERESTSUMMARY:15APRTO14MAY:5.250%"
    match = re.search(r'INTERESTSUMMARY:(\d{1,2}[A-Z]{3})TO(\d{1,2}[A-Z]{3}):([\d.]+)%', cleaned)
    
    if not match or match is None:
        raise ValueError(f"Failed to find interest rate for {statement.date.strftime("%Y")}")

    raw_start, raw_end, interest_rate = match.groups()
    
    parsed_start = datetime.strptime(raw_start, "%d%b")
    if parsed_start.month == 12:
        parsed_start = parsed_start.replace(year=statement.date.year - 1)
    else:
        parsed_start = parsed_start.replace(year=statement.date.year)
    
    parsed_end = datetime.strptime(raw_end, "%d%b")
    parsed_end = parsed_end.replace(year=statement.date.year)
    
    rate = float(interest_rate) / 100
    
    print(parsed_start, " - ", parsed_end, " - ", rate)
    
    return d.InterestSummary(
        start = parsed_start,
        end = parsed_end,
        rate = rate
    )

def get_interest_rates(statements: List[d.StatementSummary]) -> dict[str, d.InterestSummary]:
    interest_rates: dict[str, d.InterestSummary] = dict()
    for s in statements:
        summary = extract_interest_summary(s)
        interest_rates[s.date.strftime("%Y-%m")] = summary
        
    return interest_rates