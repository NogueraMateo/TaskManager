from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from jose import JWTError, jwt 
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .. import schemas, models
from ..database import SessionLocal, get_db
import os

load_dotenv()

router = APIRouter(prefix="/login", tags=["Login"])
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1



def authenticate_user(db: Session, username: str, password: str):
    '''Checks wheather the user exits or the password given matches'''
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not user.verify_password(password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None= None):
    '''Generates an access token given a dict and an expiration time'''
    to_encode = data.copy()
    if expires_delta:
        expire  = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=2)
    to_encode.update({"exp" : expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2), db:Session= Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail= "Could not validate credentials",
        headers={"WWW-Authenticate" : "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/")
async def login_for_access_token(
    response : Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db:Session= Depends(get_db)):
    '''Retrieves the data from the form, authenticates the user and generates an access token for it'''
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub" : user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        secure=False,  # Debería ser True en producción con HTTPS
        samesite='Lax',
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    
    # Devuelve el contenido como JSON sin necesidad de crear un nuevo JSONResponse
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "username": user.username
    }

@router.get("/verify-token")
async def verify_token(token: str = Depends(oauth2), db: Session = Depends(get_db)):
    try:
        current_user = await get_current_user(token, db)
        return current_user
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )   