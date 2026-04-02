from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import datetime
from jwt import ExpiredSignatureError, InvalidTokenError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = "super-tajna-sifra"

class User(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(user: User):
    try:
        if user.username == "admin" and user.password == "admin":
            payload = {
                "sub": user.username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return {"access_token": token, "token_type": "bearer"}

        raise HTTPException(status_code=401, detail="Neispravni podaci")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verify")
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return {"status": "valid", "user": payload["sub"]}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token istekao")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Neispravan token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))