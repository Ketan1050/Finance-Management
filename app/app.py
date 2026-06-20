from fastapi import FastAPI, status, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from jose import jwt, JWTError

from app import models
from app.database import engine, get_db
from app.schemas import UserOut, UserAuth, TokenSchema, ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password,
    SECRET_KEY,
    ALGORITHM
)

# Initialize the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates") 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- FRONTEND ROUTE ---

@app.get("/", summary="Render Frontend UI")
async def serve_frontend(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    ) 

# --- DEPENDENCIES ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- AUTHENTICATION ENDPOINTS --- 

@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        (models.User.email == data.email) | (models.User.username == data.username)
    ).first()
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    new_user = models.User(
        email=data.email,
        password=get_hashed_password(data.password),
        username=data.username
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Note: OAuth2PasswordRequestForm uses 'username' field, we will check both email and username
    user = db.query(models.User).filter(
        (models.User.email == form_data.username) | (models.User.username == form_data.username)
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    return {
        "access_token": create_access_token(user.email),
        "refresh_token": create_refresh_token(user.email),
    }

@app.get("/users", summary="List all users", response_model=List[UserOut])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

# --- EXPENSE TRACKER ENDPOINTS ---

@app.post('/expenses', summary="Add a new expense", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(data: ExpenseCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_expense = models.Expense(
        title=data.title,
        amount=data.amount,
        category=data.category,
        description=data.description,
        owner_id=current_user.id
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@app.get('/expenses', summary="Get all expenses", response_model=List[ExpenseResponse])
async def get_expenses(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_expenses = db.query(models.Expense).filter(models.Expense.owner_id == current_user.id).all()
    return user_expenses

@app.get('/expenses/summary', summary="Get expense summary")
async def get_expense_summary(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_expenses = db.query(models.Expense).filter(models.Expense.owner_id == current_user.id).all()
    
    total = sum(exp.amount for exp in user_expenses)
    
    category_breakdown = {}
    for exp in user_expenses:
        cat = exp.category
        category_breakdown[cat] = category_breakdown.get(cat, 0) + exp.amount
        
    return {
        "total_spent": total,
        "category_breakdown": category_breakdown,
        "total_transactions": len(user_expenses)
    }

@app.put('/expenses/{expense_id}', summary="Update an expense", response_model=ExpenseResponse)
async def update_expense(expense_id: int, data: ExpenseUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    if expense.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this expense")
        
    update_data = data.model_dump(exclude_unset=True) # Using Pydantic V2 model_dump
    for key, value in update_data.items():
        setattr(expense, key, value)
        
    db.commit()
    db.refresh(expense)
    return expense

@app.delete('/expenses/{expense_id}', summary="Delete an expense")
async def delete_expense(expense_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        
    if expense.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this expense")
        
    db.delete(expense)
    db.commit()
    return {"detail": "Expense successfully deleted"}