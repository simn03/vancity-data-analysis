from datetime import datetime

def format_currency(amount: float, symbol: str = "$", places: int = 2) -> str:
    """
    Formats a float as currency with comma grouping and optional symbol.

    Example:
        format_currency(1234.5) -> "$1,234.50"
        format_currency(-1200.9) -> "-$1,200.90"
    """
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    return f"{sign}{symbol}{amount:,.{places}f}"

def format_date(date_str: str) -> str:
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%b %d, %Y")