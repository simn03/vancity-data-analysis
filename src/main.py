from lib import statements as s, rates as r
from datetime import datetime
from config import config
def main():
    statements = s.parse_statements(config["STATEMENT_FOLDER"])
    rates = r.get_rates(statements=statements)    
    
    r.export_csv("rates.csv", rates)

if __name__ == "__main__":
    main()