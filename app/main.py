from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routes.cart import router as cart_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopping Cart API")

app.include_router(cart_router)

@app.get("/")
def root():
    return {"message": "Shopping Cart API is running"}