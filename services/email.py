import smtplib
from email.message import EmailMessage

from config import (
    EMAIL_HOST,
    EMAIL_HOST_PASSWORD,
    EMAIL_HOST_USER,
    EMAIL_PORT,
    EMAIL_USE_TLS
)


def send_welcome_email(
    email: str,
    username: str
)-> None:
    message = EmailMessage()
    
    message['Subject'] = "Welcome to Task Manager"
    message['From'] = EMAIL_HOST
    message['To'] = email
    
    message.set_content(
        f"""
Hello {username},

Welcome to Task Manager.

Your account has been successfully created.

Regards,
Task Manager
"""
        
    )
    
    with smtplib.SMTP(EMAIL_HOST,EMAIL_PORT) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_HOST_USER,EMAIL_HOST_PASSWORD)
        
        smtp.send_message(message)
