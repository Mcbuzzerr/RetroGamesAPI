from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from decouple import config

app = FastAPI()

conf = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_FROM"),
    MAIL_PASSWORD=config("MAIL_PASSWORD"),
    MAIL_FROM=config("MAIL_FROM"),
    MAIL_PORT=config("MAIL_PORT"),
    MAIL_SERVER=config("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

fastmail = FastMail(conf)


@app.get("/")
async def root():
    message = MessageSchema(
        subject="Hello World",
        recipients=["mcbuzzer@gmail.com"],
        body="This is a test email",
        subtype="plain",
    )
    await fastmail.send_message(message)
    return {"message": "Email sent"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
