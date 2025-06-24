from lib import statements as s, rates as r
from datetime import datetime
import params as p

def main():
    statements = s.parse_statements(p.STATEMENTS_ROOT)
    rates = r.get_rates(statements=statements)    
    
    for rate in rates:
        print(rate.toCSV())

if __name__ == "__main__":
    main()