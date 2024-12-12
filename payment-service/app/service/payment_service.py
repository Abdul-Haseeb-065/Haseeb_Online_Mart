from app.model.product import Product, ProductItem, ProductSize, Stock, SizeModel, ProductItemFormModel, ProductFormModel, Size
from app.model.order import OrderModel, Order, OrderItem, OrderItemMetadata, OrderMetadata, OrderStatus
from app.model.transaction import TransactionModel, TransactionDetail, Refund, RefundDetails
from app.model.authentication import Users, Admin
from app.utils.kafka import AIOKafkaProducer, get_kafka_producer 
from app.utils.verification import get_current_active_admin_user
from app.transaction_order_pb2 import TransactionModelProto, TransactionProto as Transaction, OrderBase as OrderBaseProto, OrderItemForm as OrderItemFormProto, OrderModel as OrderModelProto # type: ignore
from fastapi import Depends, HTTPException, Query
from app.setting import ORDER_TOPIC, PAYMENT_TOPIC
from typing import Annotated
from app.main import DB_SESSION
from sqlmodel import select

# Create Transaction
async def create_transaction(
        transaction_details: TransactionModel,
        user_id: int,
        aio_producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
):
    try:
        transaction_proto_details = Transaction(
                TransactionModel=TransactionModelProto(
                    stripeId=transaction_details.stripeId,
                    amount=transaction_details.amount,
                    order_id=transaction_details.order_id
                ),
                user_id=user_id
            )
        
        serialized_transaction = transaction_proto_details.SerializeToString()

        # Send order details to Kafka
        await aio_producer.send_and_wait(topic=PAYMENT_TOPIC, value=serialized_transaction)

        
    except HTTPException as e:
        raise e

# Create Transaction & Order
async def create_transaction_order(
        order_details: OrderMetadata,
        transaction_details: TransactionModel,
        aio_producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)],
):
    try:
        order_proto_details = OrderModelProto(
                user_id=order_details.user_id,
                order_id=order_details.order_id,
                base=OrderBaseProto(
                    email=order_details.email,
                    country=order_details.country,
                    city=order_details.city,
                    postal_code=order_details.postal_code,
                    address=order_details.address, 
                    phone_number=order_details.phone_number, 
                    total_price=order_details.total_price,
                    order_payment=order_details.order_payment
                ),
                items=[
                    OrderItemFormProto(
                        product_id=item.product_id,
                        product_item_id=item.product_item_id,
                        product_size_id=item.product_size_id,
                        quantity=item.quantity
                    ) for item in order_details.items
                ]
            ) 
        
        serialized_order = order_proto_details.SerializeToString()

        # Send order details to Kafka
        await aio_producer.send_and_wait(topic=ORDER_TOPIC, value=serialized_order)

        await create_transaction(transaction_details, order_details.user_id, aio_producer)

        
    except HTTPException as e:
        raise e

# Get Transaction Details
async def get_transaction_details(transaction: Transaction, session: DB_SESSION):
    user = session.exec(select(Users).where(Users.id == transaction.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    order = session.exec(select(Order).where(Order.id == transaction.order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    transaction_details = TransactionDetail(
        transaction_id=transaction.transaction_id,
        stripeId=transaction.stripeId,
        amount=transaction.amount,
        order_id=transaction.order_id,
        user_id=transaction.user_id,
        username=user.username,
        email=user.email,
        imageUrl=user.imageUrl,
        order_email=order.email,
        country=order.country,
        city=order.city,
        postal_code=order.postal_code,
        address=order.address,
        phone_number=order.phone_number,
        total_price=order.total_price,
        order_status=order.order_status,
        delivery_date=order.delivery_date,
        order_date=order.order_date
    )

    return transaction_details

async def get_refunds(refund_id: str, session: DB_SESSION,
                    current_admin: Annotated[Admin, Depends(get_current_active_admin_user)]):
    if not current_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    refund = session.exec(
        select(Refund)
        .where(Refund.refund_id == refund_id)
    ).first()

    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")
    
    order = session.exec(select(Order).where(Order.id == refund.order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    user = session.exec(select(Users).where(Users.id == refund.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    refund_details = RefundDetails(
                refund_id=refund.refund_id,
                amount=refund.amount,
                stripeId=refund.stripeId,
                status=refund.status,
                reason=refund.reason,
                refund_date=refund.refund_date,
                username=user.username,
                email=user.email,
                imageUrl=user.imageUrl,
                order_email=order.email,
                country=order.country,
                city=order.city,
                postal_code=order.postal_code,
                address=order.address,
                phone_number=order.phone_number,
                order_status=order.order_status,
                delivery_date=order.delivery_date,
                order_date=order.order_date,
                user_id=user.id,
                order_id=order.id,
                transaction_id=refund.transaction_id
            )

    return refund_details
