# Vancity Loan Interest Allocator
---

This project helps calculate and allocate loan interest charges for **multiple borrowers** sharing a **single financial account**. It determines how much interest each individual owes, based on real account statements and a detailed transaction history.

## 🧾 What It Does

- Parses official **Vancity account statements** to extract **variable interest rates** over time.
- Ingests a detailed **transaction history** (payments, withdrawals, fees).
- Calculates **daily interest accrual**, using real interest rates and outstanding balances.
- Aggregates interest by borrower, based on who withdrew how much and when.
- Outputs an **interest ledger** showing how much each person owes, including interest and principal.

---

## 📁 Project Structure

```
backend/
├── src/
│ ├── main.py # Entry point
│ ├── lib/
│ │ ├── accounts.py # Handles creating and managing Account data
│ │ ├── rates.py # Handles parsing and managing variable interest rate from monthly account statements exported from vancity
│ │ ├── vancity.py # Handles parsing and managing account history csv exported from vancity
│ │ ├── interest.py # Interest calculations
│ │ ├── definitions.py # Shared data models
│ │ └── utils.py # Helpers
├── data/ # process result files
```
---

## 🧮 Data Input

### 📄 Statement PDFs

- Format: `statement-<account_number>-<date>.pdf`
- Contains a block like:

        INTEREST SUMMARY: 15APR TO 14MAY : 5.250%

### 📊 Account History CSV

- No header; columns are:

        account number, date (dd-mmm-yyyy), description, [unused], amount subtracted, amount added, balance

- Used to build the full payment history and compute interest owed over time.

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/vancity-interest-allocator.git
cd vancity-interest-allocator
```

### 2. Create virtual environment

```bash
python -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Usage

```bash
python src/main.py
```

- Extracts interest rates from PDFs
- Parses payment history
- Calculates monthly interest charged
- Outputs a clean ledger per borrower (in CSV)

