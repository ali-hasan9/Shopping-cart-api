from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Customer(Base):
    __tablename__ = "customer"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    carts = relationship("Cart", back_populates="customer")
    wishlists = relationship("Wishlist", back_populates="customer")


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    name = Column(String(150), nullable=False)
    price = Column(Float, nullable=False)
    discount_price = Column(Float, nullable=True)
    
    category = relationship("Category", back_populates="products")


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cust_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    coupon_code = Column(String(50), nullable=True)
    discount_amount = Column(Float, default=0.0)
    status = Column(String(20), default="active")


    customer = relationship("Customer", back_populates="carts")
    items = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan"
    )


class CartItem(Base):
    __tablename__ = "cart_item"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("cart.id"), nullable=False)
    prod_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


class Wishlist(Base):
    __tablename__ = "wishlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())

    customer = relationship("Customer", back_populates="wishlists")
    product = relationship("Product")