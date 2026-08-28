from pwdlib import PasswordHash
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from database import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User
from config import SECRET_KEY

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(email: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        'sub': email,
        'exp': expire
    }
    
    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token

async def get_current_user(token: str =  Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    
    try: 
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        email = payload.get('sub')
        
        if email is None:
            raise HTTPException(
                status_code=401,
                detail='Invalid token'
            )
        
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        user = result.scalar_one_or_none()  
        
        if user is None:
            raise HTTPException(
                status_code=401,
                detail='User not found'
            )
        
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail='Invalid token'
        )
            
            
    return user        
    