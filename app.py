import json
import pandas as pd
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles


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


# Initialize the FastAPI application and the database
app = FastAPI()
db = Database()


# --- API Endpoints ---

@app.get("/api/records")
async def get_records_endpoint():
    """Endpoint to get all records."""
    records_json = db.get_records()
    return JSONResponse(content=json.loads(records_json))


@app.post("/api/add_record")
async def add_record_endpoint(request: Request):
    """Endpoint to add a new record."""
    data = await request.json()
    name = data.get('name')
    date_str = data.get('date')
    symptoms = data.get('symptoms', [])
    hazards = data.get('hazards', [])

    if not name or not date_str:
        return JSONResponse(content={"error": "Name and date are required."}, status_code=400)

    try:
        record_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        if record_date > datetime.now() + timedelta(minutes=1):
            return JSONResponse(content={"error": "Cannot enter a future date."}, status_code=400)
    except ValueError:
        return JSONResponse(content={"error": "Invalid date format."}, status_code=400)

    db.add_record(name, record_date, symptoms, hazards)
    return JSONResponse(content={"message": "Record added successfully."}, status_code=201)


@app.post("/api/remove_record")
async def remove_record_endpoint(request: Request):
    """Endpoint to remove a record."""
    data = await request.json()
    idx = data.get('index')

    if idx is None:
        return JSONResponse(content={"error": "Index is required."}, status_code=400)

    message = db.remove_record(idx)
    return JSONResponse(content={"message": message}, status_code=200)


@app.post("/api/delete_all_records")
async def delete_all_records_endpoint():
    """Endpoint to delete all records."""
    message = db.delete_all_records()
    return JSONResponse(content={"message": message}, status_code=200)


# Mount the static files directory to serve the frontend
# IMPORTANT: This must come AFTER the API endpoints to avoid them being
# treated as static files.
app.mount("/", StaticFiles(directory=".", html=True), name="static")
