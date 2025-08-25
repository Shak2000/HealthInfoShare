from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from main import Database

app = FastAPI()
database = Database()


@app.get("/")
async def get_ui():
    return FileResponse("index.html")


@app.get("/styles.css")
async def get_styles():
    return FileResponse("styles.css")


@app.get("/script.js")
async def get_script():
    return FileResponse("script.js")


@app.post("/add_record")
async def add_record(name, date, symptoms, hazards):
    database.add_record(name, date, symptoms, hazards)


@app.post("/remove_record")
async def remove_record(idx):
    database.remove_record(idx)


@app.post("/delete_all_records")
async def delete_all_records():
    database.delete_all_records()
