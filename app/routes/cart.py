from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CartCreate,
    CartResponse,
    AddItemsRequest,
    RemoveItemsRequest,
    CheckoutResponse,
)
from app.services.cart_service import (
    create_cart,
    get_cart,
    add_items_to_cart,
    remove_items_from_cart,
    checkout_cart,
    delete_cart,
)
from app.exceptions import AppException
from app.logger import logger

router = APIRouter(prefix="/carts", tags=["Cart"])
@router.post("/", response_model=CartResponse, status_code=201)
def create_cart_endpoint(cart_data: CartCreate, db: Session = Depends(get_db)):
    try:
        cart = create_cart(db, cart_data)
        return cart
    except AppException as e:
        logger.error(e.message)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error while creating cart: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    

@router.get("/{cartId}", response_model=CartResponse)
def get_cart_endpoint(cartId: int, db: Session = Depends(get_db)):
    try:
        cart = get_cart(db, cartId)
        return cart
    except AppException as e:
        logger.error(e.message)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error while fetching cart: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
@router.post("/{cartId}/items", response_model=CartResponse, status_code=201)
def add_items_endpoint(
    cartId: int, items_data: AddItemsRequest, db: Session = Depends(get_db)
):
    try:
        cart = add_items_to_cart(db, cartId, items_data)
        return cart
    except AppException as e:
        logger.error(e.message)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error while adding items: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
@router.delete("/{cartId}/items", response_model=CartResponse)
def remove_items_endpoint(
    cartId: int, remove_data: RemoveItemsRequest, db: Session = Depends(get_db)
):
    try:
        cart = remove_items_from_cart(db, cartId, remove_data)
        return cart
    except AppException as e:
        logger.error(e.message)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error while removing items: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    

@router.patch("/{cartId}/checkout", response_model=CheckoutResponse)
def checkout_cart_endpoint(cartId: int, db: Session = Depends(get_db)):
    try:
        result = checkout_cart(db, cartId)
        return result
    except AppException as e:
        logger.error(e.message)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error while checking out cart: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    

@router.delete("/{cartId}", status_code=200)
def delete_cart_endpoint(cartId: int, db: Session = Depends(get_db)):
    try:
        result = delete_cart(db, cartId)
        return result
    except AppException as e:
        logger.error(e.message)
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error while deleting cart: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")