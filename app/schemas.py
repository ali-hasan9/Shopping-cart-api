from pydantic import BaseModel, Field
from typing import Optional , List
from datetime import datetime


class CartItemCreate(BaseModel):
    prod_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemResponse(BaseModel):
    id: int
    cart_id: int
    prod_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartCreate(BaseModel):
    cust_id: int
    coupon_code: Optional[str] = None
    discount_amount: Optional[float] = Field(default=0, ge=0)


class CartResponse(BaseModel):
    id: int
    cust_id: int
    created_at: datetime
    coupon_code: Optional[str] = None
    discount_amount: float
    status: str
    items: List[CartItemResponse] = []

    class Config:
        from_attributes = True


class AddItemsRequest(BaseModel):
    items: List[CartItemCreate] = Field(min_length=1)


class RemoveItemsRequest(BaseModel):
    item_ids: List[int] = Field(min_length=1)


class CheckoutResponse(BaseModel):
    id: int
    status: str
    message: str

    class Config:
        from_attributes = False
