from lib import parsers, definitions as d
import params


        

def main():
    statements = parsers.parse_statements_map(params.STATEMENT_ROOT)

    rates = parsers.get_interest_rates(statements=statements)
    

if __name__ == "__main__":
    main()