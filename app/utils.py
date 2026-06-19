from datetime import datetime, timedelta
import os
from typing import Optional
from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv()

import bcrypt

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


# ==========================
# PASSWORD FUNCTIONS
# ==========================

def get_hashed_password(password: str) -> str:
    # Hash a password with a randomly-generated salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    # Check that an unhashed password matches one that has previously been hashed
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


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