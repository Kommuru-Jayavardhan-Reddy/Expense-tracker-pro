import csv
import os
from datetime import datetime

def check_date(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def check_amount(amount_str):
    try:
        amount = float(amount_str)
        if amount > 0:
            return amount
        return None
    except ValueError:
        return None

def save_to_csv(filepath, data):
    try:
        headers = ["ID", "Amount", "Category", "Note", "Date"]
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def load_from_csv(filepath):
    if not os.path.exists(filepath):
        return None
        
    imported_data = []
    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)
            
            for row in reader:
                if len(row) == 5:
                    try:
                        amount = float(row[1])
                        category = row[2].strip()
                        note = row[3].strip()
                        date = row[4].strip()
                        
                        if check_date(date) and amount > 0 and category:
                            imported_data.append((amount, category, note, date))
                    except ValueError:
                        continue
        return imported_data
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None
