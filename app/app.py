from fastapi import FastAPI, status, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from datetime import datetime
from typing import List
from jose import jwt, JWTError 
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional 

# Assuming these are available in your app folder
from app.schemas import UserOut, UserAuth, TokenSchema, ExpenseCreate, ExpenseResponse
from app.utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password,
    SECRET_KEY,
    ALGORITHM
) 

app = FastAPI(title="Personal Expense Tracker API")

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Jinja2 Templates (Points to the "templates" folder)
templates = Jinja2Templates(directory="templates") 

# In-memory databases
users_db = {}
expenses_db = {} # Structure: {expense_id: expense_data_dict}

# OAuth2 Scheme mapping for dependency injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- FRONTEND ROUTE ---

@app.get("/", summary="Render Frontend UI")
async def serve_frontend(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    ) 

# --- DEPENDENCIES ---

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Validates the JWT token and returns the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = users_db.get(email)
    if user is None:
        raise credentials_exception
    return user

# --- AUTHENTICATION ENDPOINTS --- 

@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    user = users_db.get(data.email, None)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    user = {
        'email': data.email,
        'password': get_hashed_password(data.password),
        'id': str(uuid4()),
        "username": data.username
    }
    users_db[data.email] = user 
    return UserOut(id=user["id"], email=user["email"], username=user["username"])

@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found!"
        )

    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
    }

@app.get("/users", summary="List all users", response_model=List[UserOut])
async def get_users():
    return [
        {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
        for user in users_db.values()
    ]

# --- EXPENSE TRACKER ENDPOINTS ---

@app.post('/expenses', summary="Add a new expense", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(data: ExpenseCreate, current_user: dict = Depends(get_current_user)):
    expense_id = str(uuid4())
    expense = {
        "id": expense_id,
        "user_id": current_user["id"],
        "title": data.title,
        "amount": data.amount,
        "category": data.category,
        "description": data.description,
        "created_at": datetime.now()
    }
    expenses_db[expense_id] = expense
    return expense

@app.get('/expenses', summary="Get all expenses", response_model=List[ExpenseResponse])
async def get_expenses(current_user: dict = Depends(get_current_user)):
    user_expenses = [exp for exp in expenses_db.values() if exp["user_id"] == current_user["id"]]
    return user_expenses

@app.get('/expenses/summary', summary="Get expense summary")
async def get_expense_summary(current_user: dict = Depends(get_current_user)):
    user_expenses = [exp for exp in expenses_db.values() if exp["user_id"] == current_user["id"]]
    
    total = sum(exp["amount"] for exp in user_expenses)
    
    category_breakdown = {}
    for exp in user_expenses:
        cat = exp["category"]
        category_breakdown[cat] = category_breakdown.get(cat, 0) + exp["amount"]
        
    return {
        "total_spent": total,
        "category_breakdown": category_breakdown,
        "total_transactions": len(user_expenses)
    }

@app.delete('/expenses/{expense_id}', summary="Delete an expense")
async def delete_expense(expense_id: str, current_user: dict = Depends(get_current_user)):
    expense = expenses_db.get(expense_id)
    
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    if expense["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this expense")
        
    del expenses_db[expense_id]
    return {"detail": "Expense successfully deleted"} 