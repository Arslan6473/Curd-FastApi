from fastapi import FastAPI
from . import models
from .db import engine
from .user_routes import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="User CRUD API")

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to User CRUD API"}



