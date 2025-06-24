import os
import re
from datetime import datetime
from typing import List
import lib.definitions as d

def parse_statements(folder_path: str) -> List[d.StatementSummary]:
    """
    Scans the given folder for statement PDF files and maps them by 'yyyy-mm' date string.

    Parameters:
        folder_path (str): The path to the folder containing the statement files.

    Returns:
        List[d.StatementSummary: A list of StatementSummary objects sorted by the start date
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

