import pandas as pd
from datetime import datetime

class Database:
    def __init__(self):
        self.columns = {
            'name': 'object',
            'date': 'datetime64[ns]',
            'headache': 'bool',
            'back pain': 'bool',
            'abdominal pain': 'bool',
            'muscle aches': 'bool',
            'cough': 'bool',
            'sore throat': 'bool',
            'nasal congestion': 'bool',
            'runny nose': 'bool',
            'shortness of breath': 'bool',
            'fatigue': 'bool',
            'nausea': 'bool',
            'vomiting': 'bool',
            'diarrhea': 'bool',
            'fever': 'bool'
        }
        self.df = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in self.columns.items()})

    def add_record(self):
        record = {}

        # Name
        while True:
            name = input("Enter name (string): ")
            if name:
                record['name'] = name
                break
            else:
                print("Name cannot be empty.")

        # Date
        record['date'] = datetime.now()

        # Boolean symptoms
        for col in self.columns:
            if self.columns[col] == 'bool':
                while True:
                    val = input(f"Is the patient experiencing {col}? (y/n): ").lower()
                    if val in ['y', 'n']:
                        record[col] = (val == 'y')
                        break
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")

        new_record_df = pd.DataFrame([record])
        self.df = pd.concat([self.df, new_record_df], ignore_index=True)
        print("Record added successfully.")

    def remove_record(self):
        if self.df.empty:
            print("No records to remove.")
            return

        self.view_records()
        try:
            idx = int(input("Enter the index of the record to remove: "))
            if 0 <= idx < len(self.df):
                self.df = self.df.drop(index=idx).reset_index(drop=True)
                print("Record removed successfully.")
            else:
                print("Invalid index.")
        except ValueError:
            print("Invalid input. Please enter an integer.")

    def view_records(self):
        if self.df.empty:
            print("No records to display.")
        else:
            print(self.df)

    def delete_all_records(self):
        if self.df.empty:
            print("No records to delete.")
            return

        confirm = input("Are you sure you want to delete all records? (y/n): ").lower()
        if confirm == 'y':
            self.df = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in self.columns.items()})
            print("All records have been deleted.")
        else:
            print("Deletion cancelled.")

def main():
    db = Database()
    while True:
        print("\nHealthcare Symptom Tracker")
        print("1. Add a record")
        print("2. Remove a record")
        print("3. View records")
        print("4. Delete all records")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            db.add_record()
        elif choice == '2':
            db.remove_record()
        elif choice == '3':
            db.view_records()
        elif choice == '4':
            db.delete_all_records()
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
