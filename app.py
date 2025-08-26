import json
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime, timedelta
import pandas as pd

# This is a critical line to prevent browser errors during development
# It allows requests from different origins (like your browser)
from flask_cors import CORS


# The main logic from your original program, now self-contained
class Database:
    """
    A class to manage a database of patient symptom and hazard records using a pandas DataFrame.
    """

    def __init__(self):
        """
        Initializes the Database with a predefined schema for patient records.
        """
        # The core columns that will always be present
        self.columns = {
            'name': 'object',
            'date': 'datetime64[ns]',
        }
        # Opt-in to the future pandas behavior to resolve the FutureWarning
        pd.set_option('future.no_silent_downcasting', True)

        # Initialize an empty DataFrame with the specified columns and data types
        self.df = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in self.columns.items()})
        # Set an option to display all columns when printing the DataFrame
        pd.set_option('display.max_columns', None)

    def add_record(self, name, date, symptoms, hazards):
        """
        Adds a new symptom and hazard record to the database.

        Args:
            name (str): The patient's name.
            date (datetime): The datetime of the record.
            symptoms (list): A list of symptoms.
            hazards (list): A list of hazards.
        """
        record = {'name': name, 'date': date}

        # Add symptoms to the record
        for symptom in symptoms:
            record[symptom] = True

        # Add hazards to the record
        for hazard in hazards:
            record[hazard] = True

        # Create a new DataFrame from the single record
        new_record_df = pd.DataFrame([record])

        # Concatenate the new record with the existing DataFrame.
        self.df = pd.concat([self.df, new_record_df], ignore_index=True, sort=False)

        # Fill any NaN values (for new columns in old rows) with False
        self.df = self.df.fillna(False)

        return "Record added successfully."

    def remove_record(self, idx):
        """
        Removes a record from the database based on its index.

        Args:
            idx (int): The index of the record to remove.
        """
        if 0 <= idx < len(self.df):
            self.df = self.df.drop(index=idx).reset_index(drop=True)
            return "Record removed successfully."
        else:
            return "Invalid index."

    def get_records(self):
        """
        Returns all records as a JSON string.
        """
        # Convert DataFrame to a list of dictionaries for JSON serialization
        # The `to_json` method handles datetime objects correctly
        return self.df.to_json(orient='records', date_format='iso')

    def delete_all_records(self):
        """
        Deletes all records from the database.
        """
        if self.df.empty:
            return "No records to delete."

        self.df = pd.DataFrame({col: pd.Series(dtype=dt) for col, dt in self.columns.items()})
        return "All records have been deleted."


# Initialize the Flask application and the database
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
db = Database()


# --- API Endpoints ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)


@app.route('/api/records', methods=['GET'])
def get_records():
    """Endpoint to get all records."""
    records = db.get_records()
    return records, 200


@app.route('/api/add_record', methods=['POST'])
def add_record():
    """Endpoint to add a new record."""
    data = request.json
    name = data.get('name')
    date_str = data.get('date')
    symptoms = data.get('symptoms', [])
    hazards = data.get('hazards', [])

    if not name or not date_str:
        return jsonify({'error': 'Name and date are required.'}), 400

    try:
        record_date = datetime.fromisoformat(date_str)
        if record_date > datetime.now() + timedelta(minutes=1):
            return jsonify({'error': 'Cannot enter a future date.'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid date format.'}), 400

    db.add_record(name, record_date, symptoms, hazards)
    return jsonify({'message': 'Record added successfully.'}), 201


@app.route('/api/remove_record', methods=['POST'])
def remove_record():
    """Endpoint to remove a record."""
    data = request.json
    idx = data.get('index')

    if idx is None:
        return jsonify({'error': 'Index is required.'}), 400

    message = db.remove_record(idx)
    return jsonify({'message': message}), 200


@app.route('/api/delete_all_records', methods=['POST'])
def delete_all_records():
    """Endpoint to delete all records."""
    message = db.delete_all_records()
    return jsonify({'message': message}), 200


if __name__ == '__main__':
    # Flask will now serve the HTML, CSS, and JS files from the same directory
    app.run(debug=True)
