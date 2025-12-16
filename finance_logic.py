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

        if any(word in command for word in ["chart", "graph", "visualize", "show me"]):
            return self.handle_visualization(command)
        elif any(word in command for word in ["report", "export", "excel", "pdf", "tax"]):
            return self.handle_reporting(command)

        # First check for general queries
        if any(word in command for word in ["balance", "how much", "money left", "my income", "income"]):
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
        elif any(word in command for word in ["advice", "tip"]):
            return "Try saving 20% of your income each month!"
        else:
            return "I can help with balance, spending, budget, or adding transactions."

    def process_spending_command(self, command):
        try:
            print(f"🔍 Processing spending command: {command}")

            # Convert words to numbers (fifty → 50)
            word_to_number = {
                'fifty': 50, 'fifteen': 15, 'twenty': 20, 'thirty': 30,
                'forty': 40, 'sixty': 60, 'seventy': 70, 'eighty': 80,
                'ninety': 90, 'hundred': 100
            }

            # Extract amount - look for numbers or number words
            amount = None
            words = command.split()

            for i, word in enumerate(words):
                # Check for number words
                if word in word_to_number:
                    amount = word_to_number[word]
                    break
                # Check for digits
                elif word.isdigit():
                    amount = float(word)
                    break
                # Check for numbers with symbols
                elif any(char.isdigit() for char in word):
                    # Extract numbers from mixed strings
                    import re
                    numbers = re.findall(r'\d+', word)
                    if numbers:
                        amount = float(numbers[0])
                        break

            if amount is None:
                return "How much did you spend? Please say 'I spent 50 dollars on groceries'"

            # Extract category
            category = "other"
            if "grocery" in command or "food" in command:
                category = "groceries"
            elif "entertainment" in command or "movie" in command:
                category = "entertainment"
            elif "transport" in command or "gas" in command:
                category = "transport"
            elif "rent" in command:
                category = "rent"

            return self.add_transaction(amount, category, "Voice added expense", "expense")

        except Exception as e:
            return f"Sorry, I didn't understand. Try 'I spent 50 dollars on groceries'"

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

    def handle_visualization(self, command):
        """Handle visualization requests"""
        try:
            # Import here to avoid circular imports
            from visualization import FinanceVisualizer
            visualizer = FinanceVisualizer()

            if "spending" in command:
                chart_path = visualizer.create_spending_chart()
                if chart_path:
                    return f"I created a spending chart! Check '{chart_path}'"
                else:
                    return "No spending data available for visualization"

            elif "income" in command or "expense" in command:
                chart_path = visualizer.create_income_expense_chart()
                if chart_path:
                    return f"I created an income vs expenses chart! Check '{chart_path}'"
                else:
                    return "No transaction data available"

            elif "budget" in command:
                chart_path = visualizer.create_budget_chart()
                if chart_path:
                    return f"I created a budget chart! Check '{chart_path}'"
                else:
                    return "No budget data available"

            elif "summary" in command or "report" in command:
                chart_path = visualizer.show_financial_summary()
                if chart_path:
                    return f"I created a comprehensive financial report! Check '{chart_path}'"
                else:
                    return "Not enough data for a full report"

            else:
                return "I can create charts for: spending, income vs expenses, budget, or a full summary report"

        except Exception as e:
            return f"Sorry, I couldn't create the visualization: {e}"

    def handle_reporting(self, command):
        """Handle reporting requests"""
        try:
            from reporting import FinancialReporter
            reporter = FinancialReporter()

            if "monthly report" in command or "month report" in command:
                filepath, message = reporter.generate_monthly_report()
                if filepath:
                    return f"{message} File saved: {filepath}"
                else:
                    return "No data available for monthly report"

            elif "export" in command or "excel" in command:
                filepath = reporter.export_to_excel()
                return f"Data exported to Excel! File saved: {filepath}"

            elif "tax" in command or "deduction" in command:
                filepath, message = reporter.generate_tax_summary()
                if filepath:
                    return f"{message} File saved: {filepath}"
                else:
                    return "No tax-deductible expenses found"

            elif "report" in command:
                return "I can generate: monthly reports, Excel exports, or tax summaries"

            else:
                return "Available reports: monthly report, Excel export, tax summary"

        except Exception as e:
            return f"Sorry, I couldn't generate the report: {e}"