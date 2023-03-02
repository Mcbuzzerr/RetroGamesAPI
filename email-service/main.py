import asyncio
from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from decouple import config
from util.kafkaUtil import consumer, DTicket

app = FastAPI()

from starlette_exporter import PrometheusMiddleware, handle_metrics

app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


conf = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_FROM"),
    MAIL_PASSWORD=config("MAIL_PASSWORD"),
    MAIL_FROM=config("MAIL_FROM"),
    MAIL_PORT=config("MAIL_PORT"),
    MAIL_SERVER=config("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

DTicket(conf, "Connection Config")
fastmail = FastMail(conf)


@app.on_event("startup")
async def startTradeConsumer():
    consumerInstance = consumer(
        {
            "bootstrap.servers": "retro-games-kafka-broker:29092",
            "group.id": "email-consumer",
        }
    )

    loop = asyncio.get_event_loop()
    loop.create_task(consumerInstance.consumeLoop("email-queue", sendEmail))
    # consumerInstance.consumeLoop("email-queue", sendEmail)


async def sendEmail(**kafkaData):
    for item in kafkaData:
        if item == "subject":
            subject = kafkaData[item]
        elif item == "recipients":
            recipients = kafkaData[item]
        elif item == "message":
            msg = kafkaData[item]

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=msg,
        subtype="plain",
    )
    await fastmail.send_message(message)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
