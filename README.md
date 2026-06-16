# FastAPI JWT Authentication

## Project Structure 
```
root/
│
├── app 
│   └── __init__.py
│   └── app.py                 # our FastAPI app
│   └── utils.py                # Utility for JWT encoding/decoding
│   └── schemas.py              # Pydantic models
│   └── database.py           # Database connection
│   └── .env                     # Environment file, REMEMBER you have to create this!!
└── .gitignore 
└── pyproject.toml         # Project configuration file
└── README.md 
└── requirements.txt 
└── venv/             # Virtual environment
```

## 1. Setting up your Virtual Environment
Fire up your command prompt/terminal and type

```powershell
cd FastAPI-JWT-Authentication
python -m venv fastapienv
fastapienv\Scripts\activate                        # on Windows
source fastapienv/bin/activate                      # on macOs
```

## 2. Installing FastAPI with all dependencies
```powershell
pip install "fastapi[standard]"
pip install -r requirements.txt
```
## 3. Understanding Password Hashing
If you have the project setup on your local environment, here are the dependencies that you need to install for JWT authentication (assuming that you have a FastAPI project running):
```powershell
 pip install "python-jose[cryptography]" "passlib[bcrypt]" python-multipart 
```
### what's inside `utils.py`?
```
from passlib.context import CryptContext

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)
```


## 4. Creating and assigning JWT Tokens

JWT means "JSON Web Tokens". It's a standard way to codify a JSON object in a long dense string without spaces. It looks like this:
    ` eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c `

It's not encrypted, so anyone could recover the information from the contents, but since it's signed, so when you receive a token that you issued, you can verify that it was you who issued it.

## 5. User creation
## 6. Authorization vs. Authentication
## 7. Validating tokens on each request to ensure authentication
