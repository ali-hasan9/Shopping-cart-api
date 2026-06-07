from app.database import engine, SessionLocal, Base
from app.models import Customer, Category, Product

Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    existing = db.query(Customer).first()
    if existing:
        print("Database already has data, skipping seed")
        db.close()
        exit()

    customers = [
        Customer(name="Ali"),
        Customer(name="Ahmed"),
    ]
    db.add_all(customers)
    db.commit()
    print(f"Added {len(customers)} customers")

    categories = [
        Category(name="Electronics"),
        Category(name="Clothing"),
    ]
    db.add_all(categories)
    db.commit()
    print(f"Added {len(categories)} categories")

    products = [
        Product(name="Laptop", price=999.99, category_id=1),
        Product(name="Mouse", price=29.99, category_id=1),
        Product(name="T-Shirt", price=19.99, discount_price=14.99, category_id=2),
        Product(name="Jeans", price=49.99, category_id=2),
    ]
    db.add_all(products)
    db.commit()
    print(f"Added {len(products)} products")

    print("Seed completed successfully")

finally:
    db.close()