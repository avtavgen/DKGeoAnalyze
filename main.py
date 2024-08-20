import os

from dotenv import load_dotenv
from fastapi import FastAPI
from routers.tasks import router as tasks_router
from fastapi_sqlalchemy import DBSessionMiddleware

load_dotenv('.env')

app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ['DATABASE_URL'])


app.include_router(tasks_router)


@app.get("/")
def read_root():
    return {"message": "Server is running."}
