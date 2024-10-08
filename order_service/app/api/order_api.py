from typing import Annotated, List
from fastapi import APIRouter, Depends

from app.models.order_models import Order # type: ignore
from app.curd.order_crud import (create_order_func, read_all_order_func, read_orders_by_user_func, read_specific_product_orders_func, read_specific_date_orders_func, read_specific_status_orders_func, read_specific_type_orders_func, update_order_quantity_func, update_order_status_func, delete_order_func)# type: ignore

order_router = APIRouter()


# 1) create order route -> user
@order_router.post("/create-order", response_model=str)
def create_order(order_creation_message: Annotated[str, Depends(create_order_func)]):
    return order_creation_message


@order_router.get("/get-all-orders", response_model=List[Order])
def get_all_orders(orders: Annotated[List[Order], Depends(read_all_order_func)]):
    return orders


@order_router.get("/get-specific-user-orders", response_model=List[Order])
def get_specific_user_orders(orders: Annotated[List[Order], Depends(read_orders_by_user_func)]):
    return orders


@order_router.get("/get-specific-product-orders", response_model=List[Order])
def get_specific_product_orders(orders: Annotated[List, Depends(read_specific_product_orders_func)]):
    return orders


@order_router.get("/get-specific-date-orders", response_model=List[Order])
def get_specific_date_orders(order: Annotated[List[Order], Depends(read_specific_date_orders_func)]):
    return order


@order_router.get("/get-specific-status-orders", response_model=List[Order])
def get_specific_status_orders(order: Annotated[List[Order], Depends(read_specific_status_orders_func)]):
    return order


@order_router.get("/get-specific-type-orders", response_model=List[Order])
def get_specific_type_orders(order: Annotated[List[Order], Depends(read_specific_type_orders_func)]):
    return order


@order_router.put("/update-order-quantity", response_model=Order)
def update_order_quantity(order: Annotated[Order, Depends(update_order_quantity_func)]):
    return order


@order_router.put("/update-order-status", response_model=Order)
def update_order_status(order: Annotated[Order, Depends(update_order_status_func)]):
    return order


@order_router.delete("/delete-order", response_model=str)
def delete_order(message: Annotated[str, Depends(delete_order_func)]):
    return message
