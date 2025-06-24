import re
import os
from datetime import datetime, timedelta
from typing import List
import fitz  # PyMuPDF
import lib.definitions as d

def _extract_rates(statement: d.StatementSummary) -> list[d.InterestSummary]:
    """
    Extracts all interest summary entries (start date, end date, rate) from a statement PDF.

    Returns a list of InterestSummary objects.
    """
    with fitz.open(statement.path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()  # type: ignore

    # Normalize the text
    cleaned = re.sub(r'\s+', '', text.upper())  # All uppercase, no whitespace

    # Find all matches like 15APRTO14MAY:5.250%
    matches = re.findall(r'(\d{1,2}[A-Z]{3})TO(\d{1,2}[A-Z]{3}):([\d.]+)%', cleaned)

    if not matches:
        raise ValueError(f"Failed to find any interest rates for {statement.date.strftime('%Y-%m')}")

    summaries: list[d.InterestSummary] = []
    for raw_start, raw_end, rate_str in matches:
        # Parse start and end date without year
        parsed_start = datetime.strptime(raw_start, "%d%b")
        parsed_end = datetime.strptime(raw_end, "%d%b")

        # overlaps with end of last year
        if parsed_start.month == 12 and parsed_end.month < 3: 
            parsed_start = parsed_start.replace(year=statement.date.year - 1)
            parsed_end = parsed_end.replace(year=statement.date.year)
        # overlaps with end of last year but also has a rate change splitting the month
        elif parsed_start.month == 12 and parsed_end.month == 12 and len(matches) > 1 and len(summaries) == 0: 
            parsed_start = parsed_start.replace(year=statement.date.year-1)
            parsed_end = parsed_end.replace(year=statement.date.year-1)
        # during the year (default)
        else:
            parsed_start = parsed_start.replace(year=statement.date.year)
            parsed_end = parsed_end.replace(year=statement.date.year)

        rate = float(rate_str) / 100
        
        summaries.append(d.InterestSummary(
            start=parsed_start,
            end=parsed_end,
            rate=rate
        ))

    return summaries

def _collapse_rates(rates: List[d.InterestSummary]) -> List[d.InterestSummary]:
    if not rates:
        return []

    # Sort by start date
    sorted_rates = sorted(rates, key=lambda r: r.start)

    # Validate continuous coverage
    for i in range(1, len(sorted_rates) - 1):
        expected_start = sorted_rates[i - 1].end + timedelta(days=1)
        actual_start = sorted_rates[i].start
        if expected_start != actual_start:
            raise ValueError(f"Gap detected before: {sorted_rates[i].start} to {sorted_rates[i].end}")

    # Collapse ranges
    collapsed: List[d.InterestSummary] = []
    current = sorted_rates[0]

    for next_rate in sorted_rates[1:]:
        if next_rate.rate == current.rate and \
           next_rate.start == current.end + timedelta(days=1):
            # Extend current range
            current = d.InterestSummary(
                start=current.start,
                end=next_rate.end,
                rate=current.rate
            )
        else:
            # Push current and reset
            collapsed.append(current)
            current = next_rate

    collapsed.append(current)
    return collapsed
    

def get_rates(statements: List[d.StatementSummary]) -> list[d.InterestSummary]:
    raw_rates: List[d.InterestSummary] = list()
    for s in statements:
        rates = _extract_rates(s)
        for r in rates:
            raw_rates.append(r)
            
    collapsed_rates = _collapse_rates(raw_rates)
        
    return collapsed_rates

def get_rate(date: datetime, rates: List[d.InterestSummary]) -> float:
    """
    Performs binary search on sorted InterestSummary list to find the rate for the given date.

    Raises:
        ValueError if the date does not fall within any interest range.
    """
    left = 0
    right = len(rates) - 1

    while left <= right:
        mid = (left + right) // 2
        summary = rates[mid]

        if summary.start <= date <= summary.end:
            return summary.rate
        elif date < summary.start:
            right = mid - 1
        else:
            left = mid + 1

    raise ValueError(f"No interest rate found for {date.date()}")

def export_csv(file: str, rates: List[d.InterestSummary]) -> None:
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
        f.write("start_date,end_date,interest_rate\n")
        for rate in rates:
            f.write(rate.toCSV() + "\n")

    print(f"Exported {len(rates)} entries to {full_path}")    