# FastAPI JWT Authentication

## 1. Setting up your Virtual Environment
Fire up your command prompt/terminal and type

```powershell
    python -m venv fastapienv
    fastapienv\Scripts\activate
```
## 2. Password Hashing


## 3. Creating and assigning JWT Tokens

If you have the project setup on your local environment, here are the dependencies that you need to install for JWT authentication (assuming that you have a FastAPI project running):

    ` pip install "python-jose[cryptography]" "passlib[bcrypt]" python-multipart `

JWT means "JSON Web Tokens". It's a standard way to codify a JSON object in a long dense string without spaces. It looks like this:
    ` eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c `

It's not encrypted, so anyone could recover the information from the contents, but since it's signed, so when you receive a token that you issued, you can verify that it was you who issued it.

## 4. User creation
## 5. Authorization vs. Authentication
## 6. Validating tokens on each request to ensure authentication
