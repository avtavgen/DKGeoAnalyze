from fastapi import FastAPI
from routers.tasks import router as tasks_router


app = FastAPI()


app.include_router(tasks_router)


@app.get("/")
def read_root():
    return "Server is running."
