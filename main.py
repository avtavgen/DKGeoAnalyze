import os

from dotenv import load_dotenv
from fastapi import FastAPI
from routers.tasks import router as tasks_router

load_dotenv('.env')

app = FastAPI()


app.include_router(tasks_router)


@app.get("/")
def read_root():
    return {"message": "Server is running."}
