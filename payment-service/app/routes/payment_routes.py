from app.model.transaction import TransactionModel, Transaction, TransactionDetail, RefundModel, Refund, TransactionStatus, RefundDetails
from app.service.payment_service import create_transaction_order, get_transaction_details, get_refunds
from fastapi import APIRouter, Response, HTTPException, Request, Depends, Query
from stripe.error import SignatureVerificationError, StripeError # type: ignore
from app.utils.actions import get_transactionBy_date, get_all_refunds_details
from app.utils.kafka import AIOKafkaProducer, get_kafka_producer
from app.setting import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.utils.verification import get_current_active_admin_user
from typing import Annotated, Optional, List, Sequence
from app.model.authentication import Users, Admin
from app.model.order import OrderMetadata, Order
from fastapi.responses import JSONResponse
from app.main import DB_SESSION
from datetime import datetime
from sqlmodel import select
import json
import stripe

stripe.api_key = STRIPE_SECRET_KEY
payment_router = APIRouter(prefix="/api/v1/payment")

@payment_router.post("/stripe/webhook")
async def payment_webhook(request: Request, 
                        aio_producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        
        # Extract and parse metadata
        metadata = session_data['metadata']
        items_json = json.loads(metadata['items'])  # Parse the items JSON string
        order_metadata = OrderMetadata(
            user_id=int(metadata['user_id']),
            order_id=metadata['order_id'],
            city=metadata['city'],
            email=metadata['email'],
            country=metadata['country'],
            postal_code=metadata['postal_code'],
            address=metadata['order_address'],
            phone_number=metadata['phone_number'],
            total_price=session_data['amount_total'] / 100,
            order_payment=metadata['order_payment'],
            items=items_json  # This should be a list of dictionaries
        )
        
        # Store the transaction
        transaction_model = TransactionModel(
            stripeId=session_data['id'],
            amount=session_data['amount_total'] / 100,
            order_id=metadata['order_id'],
        )

        transaction = await create_transaction_order(order_metadata, transaction_model, aio_producer)

        return JSONResponse(content={"message": "OK", "transaction": transaction})

    return Response(content="", status_code=200)


@payment_router.get("/transaction/all", response_model=List[TransactionDetail])
async def get_all_transactions(
    session: DB_SESSION,
    current_admin: Annotated[Admin, Depends(get_current_active_admin_user)],
    page: int = 1, 
    limit: int = 5, 
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None)
):
    offset = (page - 1) * limit
    transaction = await get_transactionBy_date(session, current_admin, offset, limit, from_date, to_date)
    return transaction


@payment_router.get("/transaction/specific/{transaction_id}")
async def get_transaction(transaction_id: str, 
                        session: DB_SESSION,
                        current_admin: Annotated[Admin, Depends(get_current_active_admin_user)]):
    if not current_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    transaction = session.exec(select(Transaction).where(Transaction.id == transaction_id)).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction_details = await get_transaction_details(transaction, session)

    return transaction_details

@payment_router.get("/transaction/order/{order_id}")
async def get_transaction_by_order(order_id: str, session: DB_SESSION,
                                current_admin: Annotated[Admin, Depends(get_current_active_admin_user)]):
    if not current_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    
    transaction = session.exec(select(Transaction).where(Transaction.order_id == order_id)).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    transaction_details = await get_transaction_details(transaction, session)

    return transaction_details


@payment_router.post("/transaction/refund/{transaction_id}")
async def refund_transaction(transaction_id: str,
                            refund_details: RefundModel,
                        session: DB_SESSION,
                        current_admin: Annotated[Admin, Depends(get_current_active_admin_user)]):
    if not current_admin:
        raise HTTPException(status_code=403, detail="Unauthorized access")

    transaction = session.exec(select(Transaction).where(Transaction.id == transaction_id)).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    try:
        refund = stripe.Refund.create(
            payment_intent=transaction.stripeId,
            amount=int(refund_details.amount * 100),
            reason=refund_details.reason
        )
    except StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    order = session.exec(select(Order).where(Order.id == transaction.order_id)).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    transaction.transaction_status = TransactionStatus.refunded
    session.commit()

    refund_model = Refund(
        refund_id=refund.id,
        transaction_id=transaction.id,
        user_id=transaction.user_id,
        order_id=order.id,
        amount=refund_details.amount,
        reason=refund_details.reason,
        status=refund.status
    )

    session.add(refund_model)
    session.commit()
    session.refresh(refund_model)

    return refund_model

@payment_router.get("/transaction/refund/all", response_model=List[RefundDetails])
async def get_all_refunds(session: DB_SESSION,
                        current_admin: Annotated[Admin, Depends(get_current_active_admin_user)],
                        from_date: Optional[datetime] = Query(None),
                        to_date: Optional[datetime] = Query(None)):
    refund = await get_all_refunds_details(session, current_admin, from_date, to_date)
    return refund

@payment_router.get("/transaction/refund/{refund_id}", response_model=RefundDetails)
async def get_refund(refund_id: str, session: DB_SESSION,
                    current_admin: Annotated[Admin, Depends(get_current_active_admin_user)]):
    refund = await get_refunds(refund_id, session, current_admin)
    return refund