# A new, complete app.py file to ensure all dependencies are handled correctly.

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime
import json
import pandas as pd
from main import Database  # Assuming main.py is in the same directory

# Initialize the FastAPI app and the database
app = FastAPI()
database = Database()


@app.get("/")
async def get_ui():
    """Serves the main HTML page."""
    return FileResponse("index.html")


@app.get("/styles.css")
async def get_styles():
    """Serves the CSS file."""
    return FileResponse("styles.css")


@app.get("/script.js")
async def get_script():
    """Serves the JavaScript file."""
    return FileResponse("script.js")


@app.post("/add_record")
async def add_record(
        name: str = Query(...),
        date: str = Query(...),
        symptoms: str = Query("[]"),
        hazards: str = Query("[]")
):
    """
    Adds a new record to the database.
    Symptoms and hazards are expected as JSON-encoded strings from the frontend.
    """
    try:
        symptoms_list = json.loads(symptoms)
        hazards_list = json.loads(hazards)
        record_date = datetime.fromisoformat(date.replace('Z', '+00:00'))

        database.add_record(name, record_date, symptoms_list, hazards_list)
        return {"status": "success", "message": "Record added successfully."}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid symptoms or hazards JSON format."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}


@app.get("/view_records")
async def view_records():
    """
    Returns all records as a JSON array for the frontend to display.
    """
    if database.df.empty:
        return []

    # Prepare DataFrame for JSON serialization
    df_copy = database.df.copy()

    # Fill NaN with False for consistent JSON output
    # This is important as to_dict does not handle NaNs gracefully for booleans.
    df_copy = df_copy.fillna(False)

    # Convert datetime objects to ISO format strings for JSON serialization
    for col in df_copy.select_dtypes(include=['datetime64[ns]']).columns:
        df_copy[col] = df_copy[col].apply(lambda x: x.isoformat() if pd.notna(x) else None)

    return df_copy.to_dict('records')


@app.post("/remove_record")
async def remove_record(idx: int = Query(...)):
    """Removes a record by its index."""
    try:
        database.remove_record(idx)
        return {"status": "success", "message": f"Record at index {idx} removed."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}


@app.post("/delete_all_records")
async def delete_all_records():
    """Deletes all records from the database."""
    try:
        database.delete_all_records()
        return {"status": "success", "message": "All records deleted."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {str(e)}"}
