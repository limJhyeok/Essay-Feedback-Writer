import secrets
import os
from dotenv import load_dotenv

from pydantic import EmailStr
from fastapi import HTTPException

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# 임시 비밀번호 생성 함수
def generate_temporary_password():
    return secrets.token_urlsafe(8)  # 8자리 임시 비밀번호 생성


async def send_temporary_password(user_email: EmailStr, temp_password: str):
    message = MIMEMultipart()
    message["From"] = "gpt-copy-test"
    message["To"] = user_email
    message["Subject"] = "Your temporary password"
    message.attach(
        MIMEText(f"Your temporary password is: {temp_password}",
                 "plain")
                   )
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as  smtp_server:
            smtp_server.starttls()
            smtp_server.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp_server.sendmail(SMTP_USERNAME, user_email, message.as_string())

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Failed to send the email. {str(e)}")