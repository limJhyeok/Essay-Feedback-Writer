import os
import secrets
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import EmailStr

load_dotenv()
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def generate_temporary_password() -> str:
    return secrets.token_urlsafe(8)


async def send_temporary_password(user_email: EmailStr, temp_password: str) -> None:
    message = MIMEMultipart()
    message["From"] = "gpt-copy-test"
    message["To"] = user_email
    message["Subject"] = "Your temporary password"
    message.attach(MIMEText(f"Your temporary password is: {temp_password}", "plain"))
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp_server.sendmail(SMTP_USERNAME, user_email, message.as_string())

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to send the email. {str(e)}"
        )
