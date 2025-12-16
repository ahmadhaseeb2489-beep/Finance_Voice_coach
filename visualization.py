# visualization.py - Financial Charts and Graphs
import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
import os
from datetime import datetime
import numpy as np


class FinanceVisualizer:
    def __init__(self):
        self.conn = sqlite3.connect('data/user_finance.db')
        print("📊 Finance Visualizer initialized!")

    def create_spending_chart(self):
        """Create spending by category pie chart"""
        query = '''
        SELECT category, SUM(amount) as total 
        FROM transactions 
        WHERE type = 'expense'
        GROUP BY category
        ORDER BY total DESC
        '''

        df = pd.read_sql_query(query, self.conn)

        if df.empty:
            return None

        plt.figure(figsize=(10, 6))
        colors = plt.cm.Set3(np.arange(len(df)))

        plt.pie(df['total'], labels=df['category'], autopct='%1.1f%%',
                colors=colors, startangle=90)
        plt.title('Spending by Category', fontsize=16, fontweight='bold')
        plt.axis('equal')

        # Save chart
        chart_path = 'data/spending_chart.png'
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()

        return chart_path

    def create_income_expense_chart(self):
        """Create income vs expense bar chart"""
        query = '''
        SELECT type, SUM(amount) as total 
        FROM transactions 
        GROUP BY type
        '''

        df = pd.read_sql_query(query, self.conn)

        if df.empty:
            return None

        plt.figure(figsize=(8, 5))
        colors = ['green' if t == 'income' else 'red' for t in df['type']]

        bars = plt.bar(df['type'], df['total'], color=colors)
        plt.title('Income vs Expenses', fontsize=14, fontweight='bold')
        plt.ylabel('Amount ($)', fontsize=12)
        plt.grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + 10,
                     f'${height:,.0f}', ha='center', va='bottom')

        # Save chart
        chart_path = 'data/income_expense_chart.png'
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()

        return chart_path

    def create_budget_chart(self):
        """Create budget vs actual spending chart"""
        query_budget = '''
        SELECT category, monthly_limit, current_spent 
        FROM budget
        WHERE monthly_limit > 0
        '''

        df = pd.read_sql_query(query_budget, self.conn)

        if df.empty:
            return None

        df['remaining'] = df['monthly_limit'] - df['current_spent']
        df['percentage_used'] = (df['current_spent'] / df['monthly_limit']) * 100

        plt.figure(figsize=(10, 6))

        x = np.arange(len(df))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 6))
        bars1 = ax.bar(x - width / 2, df['monthly_limit'], width, label='Budget', color='skyblue')
        bars2 = ax.bar(x + width / 2, df['current_spent'], width, label='Spent', color='salmon')

        ax.set_xlabel('Categories', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.set_title('Budget vs Actual Spending', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(df['category'], rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 10,
                        f'${height:,.0f}', ha='center', va='bottom', fontsize=9)

        # Save chart
        chart_path = 'data/budget_chart.png'
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()

        return chart_path

    def show_financial_summary(self):
        """Create comprehensive financial report"""
        # Get financial data
        income_query = "SELECT SUM(amount) FROM transactions WHERE type='income'"
        expense_query = "SELECT SUM(amount) FROM transactions WHERE type='expense'"

        income = pd.read_sql_query(income_query, self.conn).iloc[0, 0] or 0
        expenses = pd.read_sql_query(expense_query, self.conn).iloc[0, 0] or 0
        balance = income - expenses

        # Create summary figure
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

        # Pie chart for spending
        spending_df = pd.read_sql_query(
            "SELECT category, SUM(amount) as total FROM transactions WHERE type='expense' GROUP BY category",
            self.conn
        )
        if not spending_df.empty:
            ax1.pie(spending_df['total'], labels=spending_df['category'], autopct='%1.1f%%')
            ax1.set_title('Spending Distribution')

        # Bar chart for income vs expense
        types = ['Income', 'Expenses']
        amounts = [income, expenses]
        colors = ['green', 'red']
        ax2.bar(types, amounts, color=colors)
        ax2.set_title('Income vs Expenses')
        ax2.set_ylabel('Amount ($)')

        # Budget progress
        budget_df = pd.read_sql_query(
            "SELECT category, monthly_limit, current_spent FROM budget WHERE monthly_limit > 0",
            self.conn
        )
        if not budget_df.empty:
            budget_df['percentage'] = (budget_df['current_spent'] / budget_df['monthly_limit']) * 100
            ax3.barh(budget_df['category'], budget_df['percentage'], color='orange')
            ax3.set_xlabel('Percentage Used (%)')
            ax3.set_title('Budget Utilization')

        # Financial metrics
        metrics = ['Balance', 'Income', 'Expenses']
        values = [balance, income, expenses]
        ax4.bar(metrics, values, color=['blue', 'green', 'red'])
        ax4.set_title('Financial Summary')
        ax4.set_ylabel('Amount ($)')

        plt.tight_layout()
        chart_path = 'data/financial_summary.png'
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()

        return chart_path

    def close(self):
        self.conn.close()