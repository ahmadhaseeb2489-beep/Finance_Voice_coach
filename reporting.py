# reporting.py - Professional financial reports
import pandas as pd
import sqlite3
from datetime import datetime
import os


class FinancialReporter:
    def __init__(self):
        self.conn = sqlite3.connect('data/user_finance.db')
        print("📄 Financial Reporter initialized!")

    def generate_monthly_report(self, month=None, year=None):
        """Generate comprehensive monthly report"""
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        # Get monthly data
        query = f"""
        SELECT * FROM transactions 
        WHERE strftime('%Y', date) = '{year}' 
        AND strftime('%m', date) = '{month:02d}'
        """

        df = pd.read_sql_query(query, self.conn)

        if df.empty:
            return None, "No data for this month"

        # Calculate metrics
        income = df[df['type'] == 'income']['amount'].sum()
        expenses = df[df['type'] == 'expense']['amount'].sum()
        balance = income - expenses

        # Create report content
        report = {
            'month': month,
            'year': year,
            'income': income,
            'expenses': expenses,
            'balance': balance,
            'transactions': df.to_dict('records'),
            'spending_by_category': df[df['type'] == 'expense']
            .groupby('category')['amount'].sum().to_dict(),
            'top_expenses': df[df['type'] == 'expense']
            .nlargest(5, 'amount')[['description', 'amount', 'date']].to_dict('records')
        }

        # Generate PDF report
        pdf_path = self._create_pdf_report(report)

        return pdf_path, f"Monthly report for {month}/{year} generated!"

    def _create_pdf_report(self, report_data):
        """Create PDF report using fpdf"""
        from fpdf import FPDF

        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, f"Financial Report - {report_data['month']}/{report_data['year']}", 0, 1, 'C')
        pdf.ln(10)

        # Summary
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Financial Summary', 0, 1)
        pdf.set_font('Arial', '', 12)

        pdf.cell(0, 8, f"Income: ${report_data['income']:,.2f}", 0, 1)
        pdf.cell(0, 8, f"Expenses: ${report_data['expenses']:,.2f}", 0, 1)
        pdf.cell(0, 8, f"Balance: ${report_data['balance']:,.2f}", 0, 1)
        pdf.ln(10)

        # Spending by category
        if report_data['spending_by_category']:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Spending by Category', 0, 1)
            pdf.set_font('Arial', '', 12)

            for category, amount in report_data['spending_by_category'].items():
                pdf.cell(0, 8, f"{category}: ${amount:,.2f}", 0, 1)

        # Save PDF
        reports_dir = 'data/reports'
        os.makedirs(reports_dir, exist_ok=True)

        filename = f"financial_report_{report_data['year']}_{report_data['month']:02d}.pdf"
        filepath = os.path.join(reports_dir, filename)
        pdf.output(filepath)

        return filepath

    def export_to_excel(self):
        """Export all data to Excel"""
        # Load all data
        transactions = pd.read_sql_query("SELECT * FROM transactions", self.conn)
        budget = pd.read_sql_query("SELECT * FROM budget", self.conn)

        # Create Excel file
        reports_dir = 'data/reports'
        os.makedirs(reports_dir, exist_ok=True)

        filename = f"financial_data_export_{datetime.now().strftime('%Y%m%d')}.xlsx"
        filepath = os.path.join(reports_dir, filename)

        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            transactions.to_excel(writer, sheet_name='Transactions', index=False)
            budget.to_excel(writer, sheet_name='Budget', index=False)

            # Add summary sheet
            summary_data = {
                'Metric': ['Total Income', 'Total Expenses', 'Net Balance'],
                'Amount': [
                    transactions[transactions['type'] == 'income']['amount'].sum(),
                    transactions[transactions['type'] == 'expense']['amount'].sum(),
                    transactions[transactions['type'] == 'income']['amount'].sum() -
                    transactions[transactions['type'] == 'expense']['amount'].sum()
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        return filepath

    def generate_tax_summary(self, year=None):
        """Generate tax preparation summary"""
        if year is None:
            year = datetime.now().year

        query = f"""
        SELECT category, SUM(amount) as total 
        FROM transactions 
        WHERE type = 'expense' 
        AND strftime('%Y', date) = '{year}'
        AND category IN ('charity', 'medical', 'education', 'business')
        GROUP BY category
        """

        df = pd.read_sql_query(query, self.conn)

        if df.empty:
            return None, "No tax-deductible expenses found"

        # Create tax summary
        tax_report = f"Tax Summary for {year}\n"
        tax_report += "=" * 40 + "\n"
        total_deductions = 0

        for _, row in df.iterrows():
            tax_report += f"{row['category'].title()}: ${row['total']:,.2f}\n"
            total_deductions += row['total']

        tax_report += "=" * 40 + "\n"
        tax_report += f"Total Deductions: ${total_deductions:,.2f}\n"

        # Save to file
        reports_dir = 'data/reports'
        os.makedirs(reports_dir, exist_ok=True)

        txt_filename = f"tax_summary_{year}.txt"
        txt_filepath = os.path.join(reports_dir, txt_filename)

        with open(txt_filepath, 'w') as f:
            f.write(tax_report)

        return txt_filepath, f"Tax summary for {year} generated!"

    def close(self):
        self.conn.close()