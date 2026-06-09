from sqlalchemy.orm import Session
from app.models import Cart, CartItem, Customer, Product
from app.schemas import CartCreate, AddItemsRequest, RemoveItemsRequest
from app.exceptions import (
    NotFoundException,
    EmptyCartException,
    CartAlreadyCheckedOutException,
    DuplicateItemException,
)
from app.logger import logger


def _validate_customer(db: Session, cust_id: int):
    customer = db.query(Customer).filter(Customer.id == cust_id).first()
    if not customer:
        raise NotFoundException("Customer", cust_id)
    return customer


def _validate_cart(db: Session, cart_id: int, check_status: bool = True):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        raise NotFoundException("Cart", cart_id)
    if check_status and cart.status == "checked_out":
        raise CartAlreadyCheckedOutException(cart_id)
    return cart


def create_cart(db: Session, cart_data: CartCreate):
    logger.info(f"Creating cart for customer {cart_data.cust_id}")
    _validate_customer(db, cart_data.cust_id)
    new_cart = Cart(
        cust_id=cart_data.cust_id,
        coupon_code=cart_data.coupon_code,
        discount_amount=cart_data.discount_amount,
    )
    db.add(new_cart)
    db.commit()
    db.refresh(new_cart)
    logger.info(f"Cart created with id {new_cart.id}")
    return new_cart


def get_cart(db: Session, cart_id: int):
    logger.info(f"Fetching cart {cart_id}")
    cart = _validate_cart(db, cart_id, check_status=False)
    return cart


def add_items_to_cart(db: Session, cart_id: int, items_data: AddItemsRequest):
    logger.info(f"Adding {len(items_data.items)} items to cart {cart_id}")

    cart = _validate_cart(db, cart_id)

    added_items = []

    for item in items_data.items:
        product = db.query(Product).filter(Product.id == item.prod_id).first()
        if not product:
            raise NotFoundException("Product", item.prod_id)

        existing_item = (
            db.query(CartItem)
            .filter(CartItem.cart_id == cart_id, CartItem.prod_id == item.prod_id)
            .first()
        )
        if existing_item:
            raise DuplicateItemException(item.prod_id)

        new_item = CartItem(
            cart_id=cart_id,
            prod_id=item.prod_id,
            quantity=item.quantity,
        )
        db.add(new_item)
        added_items.append(new_item)

    db.commit()

    for item in added_items:
        db.refresh(item)

    logger.info(f"Added {len(added_items)} items to cart {cart_id}")

    db.refresh(cart)
    return cart


def remove_items_from_cart(db: Session, cart_id: int, remove_data: RemoveItemsRequest):
    logger.info(f"Removing {len(remove_data.item_ids)} items from cart {cart_id}")

    cart = _validate_cart(db, cart_id)

    for item_id in remove_data.item_ids:
        cart_item = (
            db.query(CartItem)
            .filter(CartItem.id == item_id, CartItem.cart_id == cart_id)
            .first()
        )
        if not cart_item:
            raise NotFoundException("CartItem", item_id)

        db.delete(cart_item)

    db.commit()

    logger.info(f"Removed items from cart {cart_id}")

    db.refresh(cart)
    return cart


def checkout_cart(db: Session, cart_id: int):
    logger.info(f"Checking out cart {cart_id}")

    cart = _validate_cart(db, cart_id)

    if not cart.items:
        raise EmptyCartException()

    cart.status = "checked_out"

    db.commit()
    db.refresh(cart)

    logger.info(f"Cart {cart_id} checked out successfully")

    return {
        "id": cart.id,
        "status": cart.status,
        "message": "Cart checked out successfully",
    }


def delete_cart(db: Session, cart_id: int):
    logger.info(f"Deleting cart {cart_id}")

    cart = _validate_cart(db, cart_id, check_status=False)

    db.delete(cart)
    db.commit()

    logger.info(f"Cart {cart_id} deleted successfully")

    return {"message": f"Cart with id {cart_id} deleted successfully"}
