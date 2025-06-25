import pandas as pd

import lib.rates as r
import lib.vancity as v
import lib.interest as i
import lib.accounts as a
import lib.utils as u

import lib.definitions as d

from config import config

def main():
    # Redact statements for sharing
    if config["REDACT_STATEMENTS"]:
        v.redact_statements(
            input_folder=config["STATEMENT_FOLDER"],
            output_folder=f"{config["STATEMENT_FOLDER"]}/output",
            account=config["VANCITY_ACCOUNT_NUMBER"]
        )
    
    # Export parsed rates
    statements = r.parse_statements(config["STATEMENT_FOLDER"])
    rates = r.get_rates(statements=statements)    
    r.export_csv("rates.csv", rates)
    
    # Export statement file
    account = v.parse_csv(config["VANCITY_PATH"])
    a.export_csv("account.csv", account)
    
    # Parse loan accounts from config
    loanAccounts: list[d.Account] = []
    for jsonAccount in config["LOANS"]:
        # convert json data (dict) to account type
        loanAccount = a.dict_to_account(jsonAccount)
        loanAccounts.append(loanAccount)
        
    # Validate imported loan accounts
    a.validate_transactions(account, loanAccounts)
    
    accounts: list[d.Account] = []
    
    for loanAccount in loanAccounts:
        
        # calculate the interest and create new account
        interestAccount = i.calculate_interest_rows(loanAccount, rates, 14)
        
        accounts.append(interestAccount)
        
        # export to file
        a.export_csv(f"interest_{interestAccount.label}.csv", interestAccount)
        
    # Visualize data in console
    df = pd.DataFrame(accounts)
    df["Principle"] = df["totalPrinciple"].apply(u.format_currency)
    df["Interest"] = df["totalInterest"].apply(u.format_currency)
    df["Balance Remaining"] = df["currBalance"].apply(u.format_currency)
    df = df.rename(columns={"label": "Label"})
    
    total_balance = df["currBalance"].sum()
    total_interest = df["totalInterest"].sum()
    
    df = df.drop(columns=["rows", "currBalance", "totalInterest", "totalPrinciple"]) # drop for visualization
    
    print(df)
    print(f"Total Balance is {u.format_currency(total_balance)}")
    print(f"Total Interest is {u.format_currency(total_interest)}")
    

if __name__ == "__main__":
    main()