from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.database import engine, Base
from app import models  # noqa: F401
from app.routes.cart import router as cart_router
from app.exceptions import AppException
from app.logger import logger

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopping Cart API")


@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        messages.append(f"{field}: {error['msg']}")
    return JSONResponse(
        status_code=422,
        content={"detail": messages},
    )


@app.exception_handler(Exception)
def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )


app.include_router(cart_router)


@app.post("/seed")
def seed_data():
    from app.database import SessionLocal
    from app.models import Customer, Category, Product

    db = SessionLocal()
    try:
        if db.query(Customer).first():
            return {"message": "Already seeded"}

        db.add_all([Customer(name="Ali"), Customer(name="Ahmed")])
        db.commit()

        db.add_all([Category(name="Electronics"), Category(name="Clothing")])
        db.commit()

        db.add_all([
            Product(name="Laptop", price=999.99, category_id=1),
            Product(name="Mouse", price=29.99, category_id=1),
            Product(name="T-Shirt", price=19.99, discount_price=14.99, category_id=2),
            Product(name="Jeans", price=49.99, category_id=2),
        ])
        db.commit()
        return {"message": "Seeded"}
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "Shopping Cart API is running"}
