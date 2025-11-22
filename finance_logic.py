# finance_logic.py - Financial intelligence
import sqlite3
from datetime import datetime


class FinanceLogic:
    def __init__(self):
        self.setup_database()
        self.setup_sample_data()
        print("💰 Finance Logic initialized!")

    def setup_database(self):
        self.conn = sqlite3.connect('data/user_finance.db')
        self.cursor = self.conn.cursor()

        # Transactions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                amount REAL,
                category TEXT,
                description TEXT,
                date TEXT,
                type TEXT
            )
        ''')

        # Budget table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS budget (
                category TEXT PRIMARY KEY,
                monthly_limit REAL,
                current_spent REAL DEFAULT 0
            )
        ''')

        self.conn.commit()

    def setup_sample_data(self):
        # Sample transactions
        sample_data = [
            (3000.00, 'salary', 'Monthly Salary', '2024-01-15', 'income'),
            (1200.00, 'rent', 'Apartment Rent', '2024-01-01', 'expense'),
            (150.00, 'groceries', 'Weekly Shopping', '2024-01-05', 'expense')
        ]

        self.cursor.executemany(
            'INSERT OR IGNORE INTO transactions VALUES (NULL, ?, ?, ?, ?, ?)',
            sample_data
        )

        # Sample budget
        sample_budget = [
            ('groceries', 400.0, 150.0),
            ('entertainment', 200.0, 45.0),
            ('transport', 150.0, 120.0)
        ]
        self.cursor.executemany('INSERT OR IGNORE INTO budget VALUES (?, ?, ?)', sample_budget)

        self.conn.commit()

    def process_command(self, command):
        command = command.lower()
        print(f"Processing: {command}")

        # First check for general queries
        if any(word in command for word in ["balance", "how much", "money left"]):
            return self.get_balance()
        elif any(word in command for word in ["spending", "expenses", "how much have i spent"]):
            return self.get_spending()
        # Then check for transaction commands
        elif any(word in command for word in ["i spent", "i paid", "spent", "paid"]):
            return self.process_spending_command(command)
        elif any(word in command for word in ["i saved", "i earned", "saved", "earned"]):
            return self.process_income_command(command)
        elif any(word in command for word in ["budget", "limit"]):
            return self.get_budget_status()
        else:
            return "I can help track spending, income, balance, or budget. Try 'I spent $50 on groceries' or 'What's my balance?'"
    def process_spending_command(self, command):
        try:
            # Extract amount - look for $ or numbers
            if "$" in command:
                amount_str = command.split("$")[1].split()[0]
            else:
                # Look for numbers after "spent"
                words = command.split()
                for i, word in enumerate(words):
                    if word in ["spent", "paid"] and i + 1 < len(words):
                        amount_str = words[i + 1]
                        break
                else:
                    return "How much did you spend? Please say 'I spent $50 on groceries'"

            amount = float(amount_str)

            # Extract category
            if "on" in command:
                category = command.split("on")[1].strip().split()[0]
            else:
                category = "other"

            return self.add_transaction(amount, category, "User added expense", "expense")

        except Exception as e:
            return f"Sorry, I didn't understand. Try 'I spent $50 on groceries'"

    def process_income_command(self, command):
        try:
            # Extract amount - look for $ or numbers
            if "$" in command:
                amount_str = command.split("$")[1].split()[0]
            else:
                # Look for numbers after "saved" or "earned"
                words = command.split()
                for i, word in enumerate(words):
                    if word in ["saved", "earned"] and i + 1 < len(words):
                        amount_str = words[i + 1]
                        break
                else:
                    return "How much did you save? Please say 'I saved $100'"

            amount = float(amount_str)
            return self.add_transaction(amount, "income", "User added income", "income")

        except Exception as e:
            return f"Sorry, I didn't understand. Try 'I saved $100'"

    def add_transaction(self, amount, category, description, type):
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute(
            'INSERT INTO transactions (amount, category, description, date, type) VALUES (?, ?, ?, ?, ?)',
            (amount, category, description, date, type)
        )
        self.conn.commit()
        return f"✅ Added {type}: ${amount} for {category}"

    def get_balance(self):
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="income"')
        income = self.cursor.fetchone()[0] or 0

        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type="expense"')
        expenses = self.cursor.fetchone()[0] or 0

        balance = income - expenses
        return f"Your balance is ${balance:.2f}. Income: ${income:.2f}, Expenses: ${expenses:.2f}"

    def get_spending(self):
        self.cursor.execute('SELECT category, SUM(amount) FROM transactions WHERE type="expense" GROUP BY category')
        spending = self.cursor.fetchall()

        response = "Your spending: "
        for category, amount in spending:
            response += f"{category}: ${amount:.2f}. "
        return response

    def get_budget_status(self):
        self.cursor.execute('SELECT category, monthly_limit, current_spent FROM budget')
        budget_data = self.cursor.fetchall()

        response = "Budget status: "
        for category, limit, spent in budget_data:
            remaining = limit - spent
            response += f"{category}: ${spent:.2f} of ${limit:.2f}. "
        return response

    def add_transaction(self, amount, category, description, type="expense"):
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")

        self.cursor.execute(
            'INSERT INTO transactions (amount, category, description, date, type) VALUES (?, ?, ?, ?, ?)',
            (amount, category, description, date, type)
        )
        self.conn.commit()
        return f"Added {type}: ${amount} for {category} - {description}"