from lib import rates as r, vancity as v, interest as i, accounts as a
from datetime import datetime
from config import config
def main():
    statements = r.parse_statements(config["STATEMENT_FOLDER"])
    rates = r.get_rates(statements=statements)    
    
    r.export_csv("rates.csv", rates)
    
    account = v.parse_csv(config["VANCITY_PATH"])
    a.export_csv("account.csv", account)
    
    for jsonAccount in config["LOANS"]:
        # convert json data (dict) to account type
        loanAccount = a.dict_to_account(jsonAccount)
        
        # calculate the interest and create new account
        interestAccount = i.calculate_interest_rows(loanAccount, rates, 14)
        
        # export to file
        a.export_csv(f"interest_{interestAccount.label}.csv", interestAccount)

if __name__ == "__main__":
    main()