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
