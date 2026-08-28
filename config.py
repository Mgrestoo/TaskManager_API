import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')



DATABASE_USERNAME=os.getenv('DATABASE_USERNAME')
PASSWORD=os.getenv('PASSWORD')
HOST=os.getenv('HOST')
PORT=os.getenv('PORT')
DATABASE=os.getenv('DATABASE') 

EMAIL_HOST=os.getenv('EMAIL_HOST')
EMAIL_PORT=os.getenv('EMAIL_PORT')      
EMAIL_USE_TLS=os.getenv('EMAIL_USE_TLS')     
EMAIL_HOST_USER=os.getenv('EMAIL_HOST_USER')   
EMAIL_HOST_PASSWORD=os.getenv('EMAIL_HOST_PASSWORD')


if not SECRET_KEY:
    raise ValueError("SECRET_KEY is not set")
