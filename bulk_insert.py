import time
import random
import string
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Customer, Category, Product, Cart, CartItem, Wishlist

RDS_URL = "postgresql://postgres:takeitgiveit987@shopping-cart-db.c52e48g2o03l.ap-south-1.rds.amazonaws.com:5432/postgres"
engine = create_engine(RDS_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()
print("Dropping all existing tables...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Tables recreated\n")
BATCH_SIZE = 5000
TOTAL_CUSTOMERS = 100000
TOTAL_PRODUCTS = 50000
TOTAL_CARTS = 200000
TOTAL_CART_ITEMS = 500000
TOTAL_WISHLISTS = 150000


def random_name(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))


def bulk_insert_customers():
    print(f"Inserting {TOTAL_CUSTOMERS} customers...")
    start = time.time()

    for i in range(0, TOTAL_CUSTOMERS, BATCH_SIZE):
        batch = [
            Customer(name=random_name())
            for _ in range(min(BATCH_SIZE, TOTAL_CUSTOMERS - i))
        ]
        db.bulk_save_objects(batch)
        db.commit()
        print(f"  Customers: {i + len(batch)} / {TOTAL_CUSTOMERS}")

    elapsed = time.time() - start
    print(f"  Done in {elapsed:.1f}s\n")


def bulk_insert_categories():
    print("Inserting 10 categories...")
    categories = [
        Category(name=f"Category_{i}")
        for i in range(1, 11)
    ]
    db.bulk_save_objects(categories)
    db.commit()
    print("  Done\n")


def bulk_insert_products():
    print(f"Inserting {TOTAL_PRODUCTS} products...")
    start = time.time()

    for i in range(0, TOTAL_PRODUCTS, BATCH_SIZE):
        batch = [
            Product(
                name=random_name(15),
                price=round(random.uniform(5.0, 999.99), 2),
                discount_price=round(random.uniform(1.0, 500.0), 2) if random.random() > 0.5 else None,
                category_id=random.randint(1, 10)
            )
            for _ in range(min(BATCH_SIZE, TOTAL_PRODUCTS - i))
        ]
        db.bulk_save_objects(batch)
        db.commit()
        print(f"  Products: {i + len(batch)} / {TOTAL_PRODUCTS}")

    elapsed = time.time() - start
    print(f"  Done in {elapsed:.1f}s\n")


def bulk_insert_carts():
    print(f"Inserting {TOTAL_CARTS} carts...")
    start = time.time()
    statuses = ["active", "checked_out"]

    for i in range(0, TOTAL_CARTS, BATCH_SIZE):
        batch = [
            Cart(
                cust_id=random.randint(1, TOTAL_CUSTOMERS),
                coupon_code=f"CODE{random.randint(1, 100)}" if random.random() > 0.7 else None,
                discount_amount=round(random.uniform(0, 50), 2),
                status=random.choice(statuses)
            )
            for _ in range(min(BATCH_SIZE, TOTAL_CARTS - i))
        ]
        db.bulk_save_objects(batch)
        db.commit()
        print(f"  Carts: {i + len(batch)} / {TOTAL_CARTS}")

    elapsed = time.time() - start
    print(f"  Done in {elapsed:.1f}s\n")


def bulk_insert_cart_items():
    print(f"Inserting {TOTAL_CART_ITEMS} cart items...")
    start = time.time()

    for i in range(0, TOTAL_CART_ITEMS, BATCH_SIZE):
        batch = [
            CartItem(
                cart_id=random.randint(1, TOTAL_CARTS),
                prod_id=random.randint(1, TOTAL_PRODUCTS),
                quantity=random.randint(1, 10)
            )
            for _ in range(min(BATCH_SIZE, TOTAL_CART_ITEMS - i))
        ]
        db.bulk_save_objects(batch)
        db.commit()
        print(f"  Cart Items: {i + len(batch)} / {TOTAL_CART_ITEMS}")

    elapsed = time.time() - start
    print(f"  Done in {elapsed:.1f}s\n")


def bulk_insert_wishlists():
    print(f"Inserting {TOTAL_WISHLISTS} wishlists...")
    start = time.time()

    for i in range(0, TOTAL_WISHLISTS, BATCH_SIZE):
        batch = [
            Wishlist(
                customer_id=random.randint(1, TOTAL_CUSTOMERS),
                product_id=random.randint(1, TOTAL_PRODUCTS)
            )
            for _ in range(min(BATCH_SIZE, TOTAL_WISHLISTS - i))
        ]
        db.bulk_save_objects(batch)
        db.commit()
        print(f"  Wishlists: {i + len(batch)} / {TOTAL_WISHLISTS}")

    elapsed = time.time() - start
    print(f"  Done in {elapsed:.1f}s\n")


if __name__ == "__main__":
    total_start = time.time()

    print("=" * 50)
    print("BULK INSERT - 1 MILLION+ RECORDS")
    print("=" * 50 + "\n")

    bulk_insert_customers()
    bulk_insert_categories()
    bulk_insert_products()
    bulk_insert_carts()
    bulk_insert_cart_items()
    bulk_insert_wishlists()

    total = time.time() - total_start

    print("=" * 50)
    print(f"TOTAL RECORDS: {TOTAL_CUSTOMERS + 10 + TOTAL_PRODUCTS + TOTAL_CARTS + TOTAL_CART_ITEMS + TOTAL_WISHLISTS:,}")
    print(f"TOTAL TIME: {total:.1f}s")
    print("=" * 50)

    db.close()