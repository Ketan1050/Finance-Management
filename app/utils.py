from datetime import datetime, timedelta
import os
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt

# ==========================
# SECURITY CONFIG
# ==========================

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
)
    

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==========================
# PASSWORD FUNCTIONS
# ==========================

def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


# ==========================
# ACCESS TOKEN
# ==========================

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "access"
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================
# REFRESH TOKEN
# ==========================

def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )

    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": "refresh"
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ==========================
# DECODE TOKEN
# ==========================

def decode_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload

    except JWTError:
        return None


# ==========================
# GET TOKEN SUBJECT
# ==========================

def get_token_subject(token: str):
    payload = decode_token(token)

    if payload:
        return payload.get("sub")

    return None 