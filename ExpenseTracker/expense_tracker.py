import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text

from database import Database
import utils

class ExpenseTracker:
    def __init__(self):
        self.db = Database()
        self.console = Console()

    def show_header(self):
        self.console.clear()
        header = Text("EXPENSE TRACKER", style="bold white on blue", justify="center")
        self.console.print(Panel(header, expand=False, border_style="cyan"))
        self.console.print()

    def show_menu(self):
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold green")
        table.add_column("Action", style="cyan")

        menu_items = [
            ("1", "Add Expense"),
            ("2", "View All Expenses"),
            ("3", "Update Expense"),
            ("4", "Delete Expense"),
            ("5", "Search by Category"),
            ("6", "Search by Date"),
            ("7", "View Dashboard"),
            ("8", "Export to CSV"),
            ("9", "Import from CSV"),
            ("0", "Exit")
        ]

        for key, action in menu_items:
            table.add_row(f"[{key}]", action)

        self.console.print(Panel(table, title="Menu", expand=False, border_style="green"))

    def run(self):
        while True:
            self.show_header()
            self.show_menu()
            
            choice = Prompt.ask("\nEnter your choice", choices=[str(i) for i in range(10)])

            if choice == '1':
                self.add_new_expense()
            elif choice == '2':
                self.show_all_expenses()
            elif choice == '3':
                self.update_existing_expense()
            elif choice == '4':
                self.delete_existing_expense()
            elif choice == '5':
                self.search_by_category()
            elif choice == '6':
                self.search_by_date()
            elif choice == '7':
                self.display_dashboard()
            elif choice == '8':
                self.export_data()
            elif choice == '9':
                self.import_data()
            elif choice == '0':
                self.console.print("[bold red]Exiting program...[/bold red]")
                sys.exit(0)

            if choice != '0':
                Prompt.ask("\nPress Enter to continue")

    def print_table(self, expenses, title):
        if not expenses:
            self.console.print(f"[bold yellow]No records found for: {title}[/bold yellow]")
            return

        table = Table(title=title, style="cyan")
        table.add_column("ID", justify="right", style="magenta", no_wrap=True)
        table.add_column("Amount", justify="right", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Note", style="white")
        table.add_column("Date", justify="center", style="blue")

        for exp in expenses:
            table.add_row(str(exp[0]), f"Rs. {exp[1]:.2f}", exp[2], exp[3] if exp[3] else "-", exp[4])
        
        self.console.print(table)

    def add_new_expense(self):
        self.console.print("[bold cyan]--- Add Expense ---[/bold cyan]")
        
        amount_str = Prompt.ask("Enter amount")
        amount = utils.check_amount(amount_str)
        if amount is None:
            self.console.print("[bold red]Invalid amount.[/bold red]")
            return

        category = Prompt.ask("Enter category")
        if not category.strip():
            self.console.print("[bold red]Category is required.[/bold red]")
            return

        note = Prompt.ask("Enter note (optional)", default="")
        
        if Confirm.ask("Use today's date?", default=True):
            date_str = datetime.now().strftime("%Y-%m-%d")
        else:
            date_str = Prompt.ask("Enter date (YYYY-MM-DD)")
            if not utils.check_date(date_str):
                self.console.print("[bold red]Invalid date format.[/bold red]")
                return

        if self.db.add_expense(amount, category.strip(), note.strip(), date_str):
            self.console.print("[bold green]Expense saved![/bold green]")
        else:
            self.console.print("[bold red]Failed to save expense.[/bold red]")

    def show_all_expenses(self):
        expenses = self.db.get_all_expenses()
        self.print_table(expenses, "All Expenses")

    def update_existing_expense(self):
        self.show_all_expenses()
        expense_id_str = Prompt.ask("\nEnter expense ID to update")
        
        if not expense_id_str.isdigit():
            self.console.print("[bold red]Invalid ID.[/bold red]")
            return
            
        expense_id = int(expense_id_str)
        current = self.db.get_expense_by_id(expense_id)
        
        if not current:
            self.console.print("[bold red]Expense not found.[/bold red]")
            return

        amount_str = Prompt.ask(f"Enter new amount (Current: {current[1]})", default=str(current[1]))
        amount = utils.check_amount(amount_str)
        if amount is None:
            self.console.print("[bold red]Invalid amount.[/bold red]")
            return

        category = Prompt.ask(f"Enter new category (Current: {current[2]})", default=current[2])
        note = Prompt.ask(f"Enter new note (Current: {current[3]})", default=current[3] or "")
        date_str = Prompt.ask(f"Enter new date YYYY-MM-DD (Current: {current[4]})", default=current[4])
        
        if not utils.check_date(date_str):
            self.console.print("[bold red]Invalid date.[/bold red]")
            return

        if self.db.update_expense(expense_id, amount, category.strip(), note.strip(), date_str):
            self.console.print("[bold green]Expense updated![/bold green]")
        else:
            self.console.print("[bold red]Update failed.[/bold red]")

    def delete_existing_expense(self):
        expense_id_str = Prompt.ask("Enter expense ID to delete")
        
        if not expense_id_str.isdigit():
            self.console.print("[bold red]Invalid ID.[/bold red]")
            return

        expense_id = int(expense_id_str)
        current = self.db.get_expense_by_id(expense_id)
        
        if not current:
            self.console.print("[bold red]Expense not found.[/bold red]")
            return

        self.console.print(f"Deleting: ID {current[0]} | Rs.{current[1]} | {current[2]}")
        if Confirm.ask("Are you sure?", default=False):
            if self.db.delete_expense(expense_id):
                self.console.print("[bold green]Deleted successfully![/bold green]")
            else:
                self.console.print("[bold red]Delete failed.[/bold red]")

    def search_by_category(self):
        category = Prompt.ask("Enter category to search")
        expenses = self.db.search_by_category(category)
        self.print_table(expenses, f"Category: {category}")

    def search_by_date(self):
        date_str = Prompt.ask("Enter date (YYYY-MM-DD)")
        if not utils.check_date(date_str):
            self.console.print("[bold red]Invalid date format.[/bold red]")
            return
        expenses = self.db.search_by_date(date_str)
        self.print_table(expenses, f"Date: {date_str}")

    def display_dashboard(self):
        self.console.clear()
        self.console.print(Panel(Text("DASHBOARD", style="bold magenta", justify="center")))
        
        self.show_statistics()
        self.show_category_summary()
        self.show_monthly_summary()

    def show_statistics(self):
        stats = self.db.get_statistics()
        text = (
            f"Total: Rs. {stats['total']:.2f}\n"
            f"Highest: Rs. {stats['highest']:.2f}\n"
            f"Lowest: Rs. {stats['lowest']:.2f}\n"
            f"Average: Rs. {stats['average']:.2f}\n"
            f"Total count: {stats['count']}"
        )
        self.console.print(Panel(text, title="Overall Stats", border_style="green"))

    def show_category_summary(self):
        summary = self.db.get_category_summary()
        if summary:
            table = Table(title="By Category", style="yellow")
            table.add_column("Category", style="cyan")
            table.add_column("Total", justify="right", style="green")
            for cat, total in summary:
                table.add_row(cat, f"Rs. {total:.2f}")
            self.console.print(table)

    def show_monthly_summary(self):
        summary = self.db.get_monthly_summary()
        if summary:
            table = Table(title="By Month", style="blue")
            table.add_column("Month", style="cyan")
            table.add_column("Total", justify="right", style="green")
            for month, total in summary:
                table.add_row(month, f"Rs. {total:.2f}")
            self.console.print(table)

    def export_data(self):
        filepath = Prompt.ask("Enter filename", default="expenses.csv")
        expenses = self.db.get_all_expenses()
        
        if not expenses:
            self.console.print("[bold yellow]No data to export.[/bold yellow]")
            return

        if utils.save_to_csv(filepath, expenses):
            self.console.print(f"[bold green]Exported {len(expenses)} rows to {filepath}[/bold green]")
        else:
            self.console.print("[bold red]Export failed.[/bold red]")

    def import_data(self):
        filepath = Prompt.ask("Enter CSV filename", default="expenses.csv")
        data = utils.load_from_csv(filepath)
        
        if data is None:
            self.console.print("[bold red]File not found or invalid.[/bold red]")
            return
            
        if not data:
            self.console.print("[bold yellow]No valid rows found.[/bold yellow]")
            return
            
        count = self.db.add_multiple_expenses(data)
        if count > 0:
            self.console.print(f"[bold green]Imported {count} rows![/bold green]")
        else:
            self.console.print("[bold red]Import failed.[/bold red]")

if __name__ == "__main__":
    app = ExpenseTracker()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
