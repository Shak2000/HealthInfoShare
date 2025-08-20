import pandas as pd
from datetime import datetime, timedelta


class Database:
    """
    A class to manage a database of patient symptom records using a pandas DataFrame.
    """

    def __init__(self):
        """
        Initializes the Database with a predefined schema for patient records.
        """
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
        # Initialize an empty DataFrame with the specified columns and data types
        self.df = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in self.columns.items()})
        # Set an option to display all columns when printing the DataFrame
        pd.set_option('display.max_columns', None)

    def add_record(self):
        """
        Prompts the user to add a new symptom record, including a choice for the date.
        """
        record = {}

        # Get patient name
        while True:
            name = input("Enter name (string): ")
            if name:
                record['name'] = name
                break
            else:
                print("Name cannot be empty.")

        # Get date/time information
        while True:
            date_choice = input("Would you like to use the current datetime (1) or a custom datetime (2)? ")
            if date_choice == '1':
                record['date'] = datetime.now()
                print("Using current datetime.")
                break
            elif date_choice == '2':
                if self.get_custom_datetime(record):
                    break
            else:
                print("Invalid choice. Please enter '1' or '2'.")

        # Get boolean symptoms
        for col in self.columns:
            if self.columns[col] == 'bool':
                while True:
                    val = input(f"Is the patient experiencing {col}? (y/n): ").lower()
                    if val in ['y', 'n']:
                        record[col] = (val == 'y')
                        break
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")

        # Add the new record to the DataFrame
        new_record_df = pd.DataFrame([record])
        self.df = pd.concat([self.df, new_record_df], ignore_index=True)
        print("Record added successfully.")

    def get_custom_datetime(self, record):
        """
        Prompts the user for a custom datetime and validates the input.

        Args:
            record (dict): The dictionary to store the custom datetime.

        Returns:
            bool: True if a valid custom datetime was entered, False otherwise.
        """
        try:
            year = int(input("Enter year (YYYY): "))
            month = int(input("Enter month (1-12): "))
            day = int(input("Enter day (1-31): "))
            hour = int(input("Enter hour (0-23): "))
            minute = int(input("Enter minute (0-59): "))
            second = int(input("Enter second (0-59): "))

            # Use datetime to validate the components
            custom_date = datetime(year, month, day, hour, minute, second)

            # Check if the custom date is in the future
            if custom_date > datetime.now() + timedelta(minutes=1):  # Add a small buffer
                print("Invalid date. Cannot enter a future date.")
                return False

            record['date'] = custom_date
            print("Using custom datetime.")
            return True
        except ValueError as e:
            print(f"Invalid datetime component: {e}. Please enter valid numbers.")
            return False

    def remove_record(self):
        """
        Removes a record from the database based on its index.
        """
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
        """
        Displays all records currently in the database.
        """
        if self.df.empty:
            print("No records to display.")
        else:
            print(self.df)

    def delete_all_records(self):
        """
        Deletes all records from the database after a confirmation prompt.
        """
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
    """
    Main function to run the symptom tracker program.
    """
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
