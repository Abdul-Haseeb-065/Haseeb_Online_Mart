from aiokafka.errors import KafkaConnectionError # type: ignore
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer # type: ignore
from fastapi import HTTPException
from typing import AsyncGenerator
from app.model.transaction import TransactionModel
from app.utils.actions import create_transactions
from app import transaction_pb2 # type: ignore
from app.setting import PAYMENT_TOPIC
from app.main import engine

async def get_kafka_consumer(topics: list[str]) -> AIOKafkaConsumer:
    consumer_kafka = AIOKafkaConsumer(
        *topics,
        group_id="ecommerce-mart",
        bootstrap_servers="kafka:19092",
        auto_offset_reset="earliest",
    )
    await consumer_kafka.start()
    return consumer_kafka


async def payment_consumer():
    consumer_kafka = await get_kafka_consumer([PAYMENT_TOPIC])
    try:
        async for msg in consumer_kafka:
            payment_proto = transaction_pb2.ProductItemFormProtoModel()
            payment_proto.ParseFromString(msg.value)

            user_id = payment_proto.userId

            payment_form = TransactionModel(
                stripeId=payment_proto.stripeId,
                orderId=payment_proto.orderId,
                amount=payment_proto.amount
            )

            with Session(engine) as session:
                transaction = await create_transactions(session, user_id, payment_form)

                print(f"Transaction created: {transaction}")
    except KafkaConnectionError as e:
        print(f"Error connecting to Kafka: {e}")
    finally:
        await consumer_kafka.stop()


##################################################################################################################################

async def get_kafka_producer() -> AsyncGenerator[AIOKafkaProducer, None]:
    producer = AIOKafkaProducer(bootstrap_servers='kafka:19092')
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
        