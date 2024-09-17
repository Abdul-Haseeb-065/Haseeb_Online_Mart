from datetime import datetime
import json
from typing import List
from sqlmodel import select
from fastapi import HTTPException
from app.models.payment_auth_models import PaymentDetails# type: ignore
from app.models.order_models import OrderItem, OrderModel, Order, Product, ProductSize# type: ignore
from app.curd.order_components import (get_product_and_size, handle_booking_order, handle_ready_made_order, validate_stock, create_order_item, get_user)# type: ignore
from app.main import DB_SESSION# type: ignore
from app.settings import ORDER_TOPIC # type: ignore
from app.utils.kafka_producers import KAFKA_PRODUCER# type: ignore



######################################################################  Order Creating #####################################################################

async def create_order_func(order_details: OrderModel, payment_model: PaymentDetails, session: DB_SESSION, producer: KAFKA_PRODUCER):
    user = get_user(order_details.user_id, session)
    booking_orders_total_price = 0
    booking_orders_advance_price = 0
    ready_made_orders_total_price = 0   
    booking_orders = []
    ready_made_orders = []

    order_responses: List[dict[str, str]] = []
    payment_details = payment_model.model_dump()

    for order_item in order_details.items:
        product_size, product = get_product_and_size(order_item, session)
        validate_stock(order_item, product_size)

        if product.product_type == "Booking":
            booking_orders_total_price += product_size.price * order_item.quantity
            booking_orders_advance_price += booking_orders_total_price * \
                product.advance_payment_percentage / 100
            item = create_order_item(order_item, product)
            booking_orders.append(item)
            
        elif product.product_type == "Ready made":
            item = create_order_item(order_item, product)
            ready_made_orders_total_price += product_size.price * order_item.quantity
            ready_made_orders.append(item)
    if len(booking_orders) > 0:
        print(f"Booking Orders: {booking_orders}")
        await handle_booking_order(booking_orders, booking_orders_total_price, booking_orders_advance_price,
                                   user, order_details, payment_model, payment_details, session, order_responses, producer)

    if len(ready_made_orders) > 0:
        print(f"Ready made Orders:{ready_made_orders}")
        await handle_ready_made_order(ready_made_orders, ready_made_orders_total_price, user,
                                      order_details, payment_model, payment_details, session, order_responses, producer)

    # Check if there are no valid orders
    if not order_responses:
        print(f"Order Response: {order_responses}")
        raise HTTPException(
            status_code=400, detail="No valid order items found.")

    await producer.send_and_wait(value=json.dumps({"order_responses": order_responses}).encode("utf-8"), topic=ORDER_TOPIC)

    return "Your order has been successfully created."



################################################################### Read Order Functions ############################################

def read_all_order_func(session: DB_SESSION):
    orders = session.exec(select(Order)).all()
    return orders

def read_orders_by_user_func(user_id: int, session: DB_SESSION):
    order_by_user = session.exec(
        select(Order).where(Order.user_id == user_id)).all()
    return order_by_user

def read_specific_product_orders_func(product_id: int, session: DB_SESSION):
    product_orders = []
    orders = session.exec(select(Order)).all()
    for order in orders:
        for order_item in order.items:
            if order_item.product_id == product_id:
                product = session.exec(select(Product).where(
                    Product.product_id == product_id)).one_or_none()
                if product:
                    product_orders.append(
                        {
                            "order_id": order.order_id,
                            "product_name": product.product_name,
                            "order_date": order.order_date,
                            "order_quantity": order_item.quantity,
                        }
                    )
    return product_orders


def read_specific_status_orders_func(status: str, session: DB_SESSION):
    orders_by_date = session.exec(
        select(Order).where(Order.order_status == status)).all()
    return orders_by_date


def read_specific_date_orders_func(date: datetime, session: DB_SESSION):
    orders_by_date = session.exec(
        select(Order).where(Order.order_date >= date)).all()
    return orders_by_date


def read_specific_type_orders_func(order_type: str, session: DB_SESSION):
    orders_by_date = session.exec(
        select(Order).where(Order.order_type == order_type)).all()
    return orders_by_date



################################################################### Update Order Functions ############################################


def update_order_status_func(order_id: int, status: str, session: DB_SESSION):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def update_order_quantity_func(order_item_id: int, quantity: int, session: DB_SESSION):
    order_item = session.get(OrderItem, order_item_id)

    if not order_item:
        raise HTTPException(status_code=404, detail="Order item not found.")

    if not order_item.order:
        raise HTTPException(status_code=404, detail="Order item not found.")

    if order_item.order.order_type == "Booking":
        raise HTTPException(
            status_code=400, detail="Cannot update quantity for Booking orders.")

    if order_item.order.order_status in ["dispatch", "delivered", "arrived"]:
        raise HTTPException(
            status_code=400, detail="Order cannot be updated after it has been dispatched, delivered, or arrived."
        )

    order_item.quantity = quantity
    session.add(order_item)
    session.commit()
    session.refresh(order_item)

    order = session.get(Order, order_item.order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    updated_price = sum(
        session.exec(select(ProductSize).where(
            ProductSize.product_size_id == item.product_size_id)).one().price * item.quantity
        for item in order.items
    )
    order.total_price = updated_price
    session.add(order)
    session.commit()
    session.refresh(order)
    return order



################################################################### Delete Order Functions ############################################


def delete_order_func(order_id: int, session: DB_SESSION):
    order = session.exec(select(Order).where(
        Order.order_id == order_id)).one_or_none()
    session.delete(order)
    session.commit()
    return f"Order has been successfully deleted of this id: {order_id}."
