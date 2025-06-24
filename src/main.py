from lib import statements as s, rates as r
import params as p


def main():
    statements = s.parse_statements(p.STATEMENT_ROOT)

    rates = r.get_rates(statements=statements)
    

if __name__ == "__main__":
    main()